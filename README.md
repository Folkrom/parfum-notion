# parfum-notion

Agent-driven perfume wish list: turn social posts (TikTok, Instagram, YouTube) into a
Notion database, with an Obsidian vault as the agent's memory.

- **Notion** — the `Perfume Wish List` database: price, priority, buy links, status, images.
- **This repo** — an Obsidian vault the agent keeps in sync: one note per perfume (properties in
  frontmatter + opinions from every source), one note per processed post, workflows and memory.
- **Any agent/model** — open a session in this folder; `AGENTS.md` has everything it needs
  (`CLAUDE.md` imports it for Claude Code).

## What it does

1. Downloads a post: slides from photo posts, scene frames from videos, caption and transcript.
2. Reads the perfumes in it and lets you choose which to keep.
3. Detects duplicates against what you already saved and merges them instead of adding rows.
4. Creates the Notion rows with a cropped bottle image and the reviewer's opinion.
5. Records your own opinions, ratings and purchases over time.

## Requirements

- Python 3.10+ (standard library only)
- [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) — a **recent** version (`pipx install yt-dlp`); distro packages go stale
- `ffmpeg` / `ffprobe`, `curl`
- An agent with the **Notion MCP** connected (Claude Code, or any MCP client)
- Optional: [`gallery-dl`](https://github.com/mikf/gallery-dl) for Instagram carousels

## Usage

Open the folder as an Obsidian vault (`Home.md` is the entry point) and start an agent here:

```
Save the perfumes from this TikTok: https://www.tiktok.com/@account/photo/123
I tried Sauvage Elixir: 4 stars, too strong for the office
Do I already have something similar to Tobacco Vanille?
```

Scripts can also be used directly:

```bash
python3 scripts/fetch_post.py "<url>" [--cookies-from-browser firefox]
python3 scripts/vault_index.py match "Dior Sauvage Elixir"
python3 scripts/crop_bottles.py --slides inbox/<post>/slides --map inbox/<post>/map.txt --out inbox/<post>/crops
python3 scripts/upsert_note.py < perfumes.json
```

Each script documents itself with `--help`.

## Layout

| Path | Contents |
|---|---|
| `AGENTS.md` | Rules and map for agents (start here) |
| `config/notion.md` | Notion IDs, schema, valid options, views |
| `memory/` | User preferences and known technical gotchas |
| `workflows/` | Ingest a post, dedupe/merge, opinions |
| `docs/enrichment.md` | Fragrantica and fragrance-data APIs |
| `perfumes/` | One note per perfume |
| `sources/` | One note per processed post |
| `scripts/` | Download, crop, index, upsert, upload |
| `attachments/` | Bottle crops (git-ignored; also stored in Notion) |
| `inbox/` | Raw downloads (git-ignored) |

## Notes

- Images and post content belong to their creators; they are only stored privately in Notion
  and locally, and are excluded from git.
- Fragrantica has no official API; see `docs/enrichment.md` for alternatives.
