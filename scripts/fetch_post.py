#!/usr/bin/env python3
"""Download a social post (images/frames + caption + transcript) into inbox/<platform>-<id>/.

Usage: fetch_post.py URL [--out inbox] [--cookies-from-browser firefox] [--every 3]

Platforms:
  tiktok      Photo posts: every slide at full resolution (via yt-dlp raw API dump).
              Video posts: falls back to the generic video path.
  instagram   Carousels/images via gallery-dl when installed (usually needs
              --cookies-from-browser), otherwise yt-dlp (videos/reels).
  youtube     Video/Shorts: scene-change frames + description + subtitles/auto-captions.
  other       Anything yt-dlp supports, same as the generic video path.

Output (same layout for every platform, so crop_bottles.py works on all of them):
  slides/s01.jpg ...   slides or extracted video frames, in order
  sheet.jpg            contact sheet of slides (first 40)
  transcript.txt       spoken text from subtitles, when available (reviews often only say the names)
  meta.json            platform, post_id, url, account, title, caption, upload_date, slides
  raw/                 downloads and yt-dlp dumps (debugging)

Exit code 2: nothing visual could be extracted (log in raw/).
"""
import argparse
import json
import math
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
MAX_SHEET = 40


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", *args], check=True)


def detect_platform(url):
    host = re.sub(r"^https?://(www\.|m\.|vm\.)?", "", url).split("/")[0]
    if "tiktok" in host:
        return "tiktok"
    if "instagram" in host:
        return "instagram"
    if "youtube" in host or "youtu.be" in host:
        return "youtube"
    return "other"


def cookie_args(args):
    return ["--cookies-from-browser", args.cookies_from_browser] if args.cookies_from_browser else []


def download(url, dst):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    dst.write_bytes(urllib.request.urlopen(req, timeout=60).read())


def to_jpg(src, dst):
    ffmpeg("-i", str(src), "-q:v", "2", str(dst))


# --- TikTok photo posts -----------------------------------------------------------------

def tiktok_photos(url, out, args):
    """Return (meta, slide paths) for a TikTok photo post, or None if it is a video."""
    m = re.search(r"@([^/?]+)/(?:photo|video)/(\d+)", url)
    if not m:
        return None
    account, post_id = m.groups()
    raw = out / "raw"
    # yt-dlp has no /photo/ extractor; the same id works as /video/. --write-pages drops
    # the raw API responses (which list the slides) in the cwd, hence cwd=raw.
    proc = run(["yt-dlp", "--write-pages", "--skip-download", "--dump-json", *cookie_args(args),
                f"https://www.tiktok.com/@{account}/video/{post_id}"], cwd=raw)
    info = json.loads(proc.stdout) if proc.stdout.strip().startswith("{") else {}
    aweme = None
    for dump in sorted(raw.glob("*.dump")):
        try:
            data = json.loads(dump.read_text(encoding="utf-8", errors="replace"))
        except json.JSONDecodeError:
            continue
        aweme = next((a for a in data.get("aweme_list") or [] if a.get("aweme_id") == post_id), aweme)
    images = ((aweme or {}).get("image_post_info") or {}).get("images") or []
    if not images:
        return None

    slides = []
    for i, img in enumerate(images, 1):
        urls = (img.get("display_image") or img.get("owner_watermark_image") or {}).get("url_list") or []
        src = raw / f"img{i:02d}.bin"
        download(urls[0], src)
        dst = out / "slides" / f"s{i:02d}.jpg"
        to_jpg(src, dst)
        slides.append(dst)
    meta = {
        "platform": "tiktok", "post_id": post_id, "url": url, "account": "@" + account,
        "title": None, "caption": aweme.get("desc") or info.get("description"),
        "upload_date": info.get("upload_date"),
    }
    return meta, slides


# --- Instagram carousels ----------------------------------------------------------------

def gallery_dl_images(url, out, args):
    if not shutil.which("gallery-dl"):
        return []
    dl = out / "raw" / "gallery"
    cmd = ["gallery-dl", "-D", str(dl), "--write-metadata", url]
    if args.cookies_from_browser:
        cmd[1:1] = ["--cookies-from-browser", args.cookies_from_browser]
    proc = run(cmd)
    (out / "raw" / "gallery-dl.log").write_text(proc.stdout + proc.stderr)
    files = sorted(p for p in dl.glob("*") if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".heic"})
    slides = []
    for i, src in enumerate(files, 1):
        dst = out / "slides" / f"s{i:02d}.jpg"
        to_jpg(src, dst)
        slides.append(dst)
    return slides


# --- Generic: yt-dlp video / images -----------------------------------------------------

def scene_frames(video, frames_dir, every):
    """Frames at scene changes; if the video barely changes, one frame every `every` seconds."""
    frames_dir.mkdir(exist_ok=True)
    ffmpeg("-i", str(video), "-vf", "select='gt(scene,0.3)',scale=1080:-2", "-vsync", "vfr",
           str(frames_dir / "f%03d.jpg"))
    frames = sorted(frames_dir.glob("f*.jpg"))
    if len(frames) < 3:
        for f in frames:
            f.unlink()
        ffmpeg("-i", str(video), "-vf", f"fps=1/{every},scale=1080:-2", str(frames_dir / "f%03d.jpg"))
        frames = sorted(frames_dir.glob("f*.jpg"))
    return frames


def vtt_to_text(path):
    lines, last = [], None
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = re.sub(r"<[^>]+>", "", line).strip()
        if not line or "-->" in line or line.startswith(("WEBVTT", "Kind:", "Language:", "NOTE")):
            continue
        if line != last:  # auto-captions repeat each line while it scrolls
            lines.append(line)
        last = line
    return "\n".join(lines)


def ytdlp_generic(url, out, args, platform):
    raw = out / "raw"
    proc = run(["yt-dlp", "--dump-single-json", *cookie_args(args), url])
    if not proc.stdout.strip().startswith("{"):
        (raw / "yt-dlp.log").write_text(proc.stderr)
        return None, []
    info = json.loads(proc.stdout)
    entries = info.get("entries") or [info]

    # Subtitles / auto-captions: reviewers often say the perfume names out loud.
    run(["yt-dlp", "--skip-download", "--write-subs", "--write-auto-subs", "--sub-langs", "es.*,en.*",
         "--sub-format", "vtt", "-o", str(raw / "subs.%(ext)s"), *cookie_args(args), url])
    vtts = sorted(raw.glob("subs*.vtt"))
    if vtts:
        (out / "transcript.txt").write_text(vtt_to_text(vtts[0]), encoding="utf-8")

    slides = []
    for n, entry in enumerate(entries, 1):
        is_video = entry.get("vcodec") not in (None, "none") or entry.get("duration")
        if is_video:
            target = entry.get("webpage_url") or entry.get("url") or url
            run(["yt-dlp", "-f", "bv*[height<=1080]+ba/b[height<=1080]/b", "--merge-output-format", "mp4",
                 "-o", str(raw / f"video{n:02d}.%(ext)s"), *cookie_args(args), target])
            videos = sorted(raw.glob(f"video{n:02d}.*"))
            if videos:
                slides += scene_frames(videos[0], raw / f"frames{n:02d}", args.every)
        elif entry.get("url"):
            src = raw / f"img{n:02d}.bin"
            download(entry["url"], src)
            slides.append(src)

    final = []
    for i, src in enumerate(slides, 1):
        dst = out / "slides" / f"s{i:02d}.jpg"
        to_jpg(src, dst)
        final.append(dst)
    meta = {
        "platform": platform, "post_id": str(info.get("id")), "url": url,
        "account": info.get("uploader_id") or info.get("channel") or info.get("uploader"),
        "title": info.get("title"), "caption": info.get("description"),
        "upload_date": info.get("upload_date"),
    }
    return meta, final


# --- Main -------------------------------------------------------------------------------

def contact_sheet(slides, out):
    thumbs = out / "raw" / "thumbs"
    thumbs.mkdir(exist_ok=True)
    for old in thumbs.glob("*.jpg"):
        old.unlink()
    shown = slides[:MAX_SHEET]
    # Same-size thumbnails first: mixed sizes make ffmpeg reset `tile` mid-stream.
    for i, p in enumerate(shown, 1):
        ffmpeg("-i", str(p), "-vf",
               "scale=600:800:force_original_aspect_ratio=decrease,pad=600:800:(ow-iw)/2:(oh-ih)/2:white",
               str(thumbs / f"t{i:02d}.jpg"))
    cols = min(5, len(shown))
    rows = math.ceil(len(shown) / cols)
    ffmpeg("-i", str(thumbs / "t%02d.jpg"), "-vf", f"tile={cols}x{rows}:color=white", "-frames:v", "1",
           str(out / "sheet.jpg"))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url")
    ap.add_argument("--out", default="inbox", type=Path)
    ap.add_argument("--cookies-from-browser", metavar="BROWSER",
                    help="pass the browser's login cookies (instagram usually needs it): firefox, chrome, ...")
    ap.add_argument("--every", type=int, default=3, help="seconds between frames when scene detection finds few")
    args = ap.parse_args()

    platform = detect_platform(args.url)
    staging = args.out / f"_staging-{platform}"
    if staging.exists():
        shutil.rmtree(staging)
    (staging / "raw").mkdir(parents=True)
    (staging / "slides").mkdir()

    result = tiktok_photos(args.url, staging, args) if platform == "tiktok" else None
    if result is None and platform == "instagram":
        imgs = gallery_dl_images(args.url, staging, args)
        if imgs:
            m = re.search(r"/(?:p|reel|reels|tv)/([^/?]+)", args.url)
            result = ({"platform": "instagram", "post_id": m.group(1) if m else "unknown", "url": args.url,
                       "account": None, "title": None, "caption": None, "upload_date": None}, imgs)
    if result is None:
        result = ytdlp_generic(args.url, staging, args, platform)
    meta, slides = result
    if not meta or not slides:
        print(f"Nothing visual extracted. Check {staging / 'raw'} (login may be needed: --cookies-from-browser).")
        sys.exit(2)

    out = args.out / f"{meta['platform']}-{meta['post_id']}"
    if out.exists():
        shutil.rmtree(out)
    staging.rename(out)
    slides = [out / "slides" / p.name for p in slides]
    contact_sheet(slides, out)
    meta["slides"] = [str(p) for p in slides]
    meta["transcript"] = str(out / "transcript.txt") if (out / "transcript.txt").exists() else None
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(slides)} slides -> {out / 'slides'}\nsheet: {out / 'sheet.jpg'}")
    print(f"transcript: {meta['transcript'] or '-'}\ncaption: {(meta['caption'] or '')[:300]}")


if __name__ == "__main__":
    main()
