#!/usr/bin/env python3
"""Create or merge perfume notes from JSON on stdin (one object or a list).

Fields (all optional except name and brand):
  name, brand, concentration, aliases[], scent_family[], key_notes[] (or "a, b"),
  season[], occasion[], status, priority, my_rating, price_mxn, size_ml,
  notion_page_id, image ("attachments/x.jpg"), sources[] (source slugs),
  opinions[]: {"date": "YYYY-MM-DD", "source": "tiktok-123", "author": "...", "text": "..."}
  my_notes[]: {"date": "YYYY-MM-DD", "text": "..."}

Merge rules when the note already exists (same file name, or pass "file"):
  - lists are unioned (existing order first),
  - scalars only fill empty fields, unless --overwrite,
  - opinions / my_notes are appended unless the same text is already there.
Prints one line per note: created | merged | unchanged.
"""
import argparse
import datetime
import json
import sys

from vaultlib import LIST_KEYS, VAULT, note_filename, read_note, write_note

BODY_TEMPLATE = """# {brand} — {name}

{image}
## Opiniones

## Mis notas
"""
SKIP_KEYS = {"opinions", "my_notes", "file"}


def as_list(value):
    if value is None:
        return []
    if isinstance(value, str):
        return [v.strip() for v in value.split(",") if v.strip()]
    return list(value)


def insert_in_section(body, heading, lines):
    """Append lines at the end of the `## heading` section (created if missing)."""
    marker = f"## {heading}\n"
    if marker not in body:
        body = body.rstrip("\n") + f"\n\n{marker}"
    start = body.index(marker) + len(marker)
    nxt = body.find("\n## ", start)
    end = len(body) if nxt == -1 else nxt
    content = body[start:end].strip("\n")
    content = (content + "\n" if content else "") + "\n".join(lines) + "\n"
    # body[end:] starts with "\n## ..." so one blank line separates the sections.
    return body[:start] + content + body[end:]


def upsert(item, overwrite, today):
    path = VAULT / item["file"] if item.get("file") else note_filename(item["brand"], item["name"])
    exists = path.exists()
    if exists:
        meta, body = read_note(path)
    else:
        image = f"![[{item['image'].split('/')[-1]}|220]]\n" if item.get("image") else ""
        meta = {"type": "perfume", "added": today}
        body = BODY_TEMPLATE.format(brand=item["brand"], name=item["name"], image=image)

    before = (dict(meta), body)
    for key, value in item.items():
        if key in SKIP_KEYS:
            continue
        if key in LIST_KEYS:
            merged = list(meta.get(key) or [])
            merged += [v for v in as_list(value) if v not in merged]
            meta[key] = merged
        elif value not in (None, "") and (overwrite or meta.get(key) in (None, "")):
            meta[key] = value
    if meta.get("notion_page_id") and not meta.get("notion_url"):
        meta["notion_url"] = "https://app.notion.com/p/" + meta["notion_page_id"].replace("-", "")

    new_ops = []
    for op in item.get("opinions") or []:
        src = f"[[{op['source']}]]" if op.get("source") else ""
        line = " · ".join(x for x in [op.get("date", today), src, op.get("author", "")] if x) + f": {op['text']}"
        if op["text"] not in body:
            new_ops.append(f"- {line}")
    if new_ops:
        body = insert_in_section(body, "Opiniones", new_ops)
    new_notes = [f"- {n.get('date', today)}: {n['text']}" for n in item.get("my_notes") or [] if n["text"] not in body]
    if new_notes:
        body = insert_in_section(body, "Mis notas", new_notes)

    if (meta, body) == before:
        return "unchanged", path
    if exists:
        meta["updated"] = today
    write_note(path, meta, body)
    return ("merged" if exists else "created"), path


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--overwrite", action="store_true", help="replace non-empty scalar fields")
    args = ap.parse_args()
    data = json.load(sys.stdin)
    today = datetime.date.today().isoformat()
    for item in data if isinstance(data, list) else [data]:
        status, path = upsert(item, args.overwrite, today)
        print(f"{status:9} {path.relative_to(VAULT)}")


if __name__ == "__main__":
    main()
