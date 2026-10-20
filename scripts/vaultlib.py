"""Shared helpers for reading and writing perfume notes in the vault.

Frontmatter is a restricted YAML subset: one `key: value` per line, where every
value is JSON (strings quoted, lists as JSON arrays). That keeps it valid YAML for
Obsidian while staying trivial to parse without third-party packages.
"""
import json
import re
import unicodedata
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
PERFUMES = VAULT / "perfumes"

# Order in which frontmatter keys are written; unknown keys go after these.
KEY_ORDER = [
    "type", "name", "brand", "concentration", "aliases", "scent_family", "key_notes",
    "season", "occasion", "status", "priority", "my_rating", "price_mxn", "size_ml",
    "buy_option", "store", "link_to_buy", "notion_page_id", "notion_url", "image",
    "sources", "added", "updated",
]
LIST_KEYS = {"aliases", "scent_family", "key_notes", "season", "occasion", "store", "sources"}


def split_note(text):
    """Return (frontmatter dict, body str)."""
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    meta = {}
    for line in text[4:end].splitlines():
        if not line.strip() or ":" not in line:
            continue
        key, raw = line.split(":", 1)
        raw = raw.strip()
        if raw == "":
            meta[key.strip()] = None
            continue
        try:
            meta[key.strip()] = json.loads(raw)
        except json.JSONDecodeError:
            meta[key.strip()] = raw
    return meta, text[end + 5:]


def dump_frontmatter(meta):
    keys = [k for k in KEY_ORDER if k in meta] + sorted(k for k in meta if k not in KEY_ORDER)
    lines = ["---"]
    for k in keys:
        v = meta[k]
        lines.append(f"{k}:" if v is None or v == "" else f"{k}: {json.dumps(v, ensure_ascii=False)}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def read_note(path):
    return split_note(Path(path).read_text(encoding="utf-8"))


def write_note(path, meta, body):
    Path(path).write_text(dump_frontmatter(meta) + body, encoding="utf-8")


def note_filename(brand, name):
    safe = re.sub(r'[\\/:*?"<>|#^\[\]]', "-", f"{brand} - {name}")
    return PERFUMES / f"{safe}.md"


def normalize(text):
    """Lowercase, strip accents and punctuation, for fuzzy matching."""
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(c for c in text if not unicodedata.combining(c)).lower()
    text = text.replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", " ", text).strip()
    for long, short in CONCENTRATION_ALIASES:
        text = re.sub(rf"\b{long}\b", short, text)
    return text


# Spelled-out concentrations -> the abbreviations used in note names.
CONCENTRATION_ALIASES = [
    ("extrait de parfum", "extrait"),
    ("eau de parfum", "edp"),
    ("eau de toilette", "edt"),
    ("eau de cologne", "edc"),
]


def iter_perfumes():
    for path in sorted(PERFUMES.glob("*.md")):
        meta, body = read_note(path)
        if meta.get("type") == "perfume":
            yield path, meta, body
