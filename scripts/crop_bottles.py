#!/usr/bin/env python3
"""Crop one bottle per perfume out of comparison slides.

Usage: crop_bottles.py --slides DIR --map FILE --out DIR [--y 390 --h 500 --margin 0.12]

Map file, one perfume per line ('#' comments allowed):
    <output-name> <slide-number> <columns-in-slide> <column-index-from-0>
    sauvage-elixir 3 4 3
or an explicit box in slide pixels (for split/irregular layouts):
    <output-name> <slide-number> box <x> <y> <w> <h>
    naxos 5 box 520 190 215 850

In column mode each slide is split into equal-width columns; the bottle band is rows
y..y+h (defaults fit the 1200x1600 "Perfume & Diamond" template). Crops are padded onto a
480x600 white canvas. Writes <out>/crops_sheet.jpg in map order: check it before uploading.
"""
import argparse
import json
import subprocess
import tempfile
from pathlib import Path


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", *args], check=True)


def width_of(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width",
                          "-of", "json", str(path)], capture_output=True, text=True, check=True).stdout
    return json.loads(out)["streams"][0]["width"]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--slides", required=True, type=Path)
    ap.add_argument("--map", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--y", type=int, default=390)
    ap.add_argument("--h", type=int, default=500)
    ap.add_argument("--margin", type=float, default=0.12, help="side margin per column, fraction of column width")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    made = []
    for line in args.map.read_text().splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        name, slide, *rest = line.split()
        src = args.slides / f"s{int(slide):02d}.jpg"
        if rest[0] == "box":
            x, y, crop_w, crop_h = map(int, rest[1:5])
        else:
            col_w = width_of(src) // int(rest[0])
            margin = int(col_w * args.margin)
            crop_w = col_w - 2 * margin
            x, y, crop_h = col_w * int(rest[1]) + margin, args.y, args.h
        dst = args.out / f"{name}.jpg"
        ffmpeg("-i", str(src), "-vf",
               f"crop={crop_w}:{crop_h}:{x}:{y},scale=-1:480,pad=480:600:(ow-iw)/2:(oh-ih)/2:white",
               "-q:v", "3", str(dst))
        made.append(dst)

    # Sheet in map order: number symlinks so ffmpeg's pattern input keeps that order.
    with tempfile.TemporaryDirectory() as tmp:
        for i, p in enumerate(made):
            Path(tmp, f"{i:03d}.jpg").symlink_to(p.resolve())
        cols = min(12, len(made))
        rows = -(-len(made) // cols)
        ffmpeg("-i", f"{tmp}/%03d.jpg", "-vf", f"scale=160:200,tile={cols}x{rows}", "-frames:v", "1",
               str(args.out / "crops_sheet.jpg"))
    for i, p in enumerate(made):
        print(f"{i:2d} row{i // cols} col{i % cols}  {p.name}")
    print(f"sheet: {args.out / 'crops_sheet.jpg'}")


if __name__ == "__main__":
    main()
