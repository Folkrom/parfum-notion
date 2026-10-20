#!/usr/bin/env python3
"""Query the perfume notes in the vault.

Usage:
  vault_index.py list [--json]          Table of every perfume (brand, name, concentration, status).
  vault_index.py match "TEXT" [-n 5]    Fuzzy candidates for TEXT (e.g. "Dior Sauvage Elixir").
  vault_index.py source SLUG            Perfumes that cite a source (e.g. tiktok-7529011813543857416).

`match` scores against "brand name", the bare name and every alias. Variant words
(EDT/EDP/Intense...) are kept on purpose, so EDT and EDP of the same line score
high but not 1.0 -- read the concentration column before deciding they are the same.
"""
import argparse
import json
import sys
from difflib import SequenceMatcher

from vaultlib import iter_perfumes, normalize, VAULT


def score(query, meta):
    q = normalize(query)
    brand = meta.get("brand") or ""
    candidates = [f"{brand} {meta.get('name', '')}", meta.get("name", "")] + list(meta.get("aliases") or [])
    best = 0.0
    for cand in candidates:
        c = normalize(cand)
        if not c:
            continue
        ratio = SequenceMatcher(None, q, c).ratio()
        # Reward token containment ("sauvage elixir" inside "dior sauvage elixir").
        q_tokens, c_tokens = set(q.split()), set(c.split())
        if q_tokens == c_tokens:
            ratio = max(ratio, 0.95)
        elif (q_tokens <= c_tokens or c_tokens <= q_tokens) and len(q_tokens & c_tokens) >= 2:
            ratio = max(ratio, 0.9)
        best = max(best, ratio)
    return best


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_list = sub.add_parser("list")
    p_list.add_argument("--json", action="store_true")
    p_match = sub.add_parser("match")
    p_match.add_argument("text")
    p_match.add_argument("-n", type=int, default=5)
    p_src = sub.add_parser("source")
    p_src.add_argument("slug")
    args = ap.parse_args()

    notes = list(iter_perfumes())
    if args.cmd == "list":
        if args.json:
            json.dump([dict(meta, file=str(p.relative_to(VAULT))) for p, meta, _ in notes], sys.stdout,
                      ensure_ascii=False, indent=1)
            return
        for p, meta, _ in notes:
            print(f"{meta.get('brand','')} | {meta.get('name','')} | {meta.get('concentration') or '-'} | "
                  f"{meta.get('status') or '-'} | {p.name}")
        print(f"\n{len(notes)} perfumes")
    elif args.cmd == "match":
        ranked = sorted(((score(args.text, m), p, m) for p, m, _ in notes), key=lambda t: -t[0])
        for s, p, m in ranked[: args.n]:
            print(f"{s:.2f}  {m.get('brand','')} | {m.get('name','')} | {m.get('concentration') or '-'} | "
                  f"notion={m.get('notion_page_id') or '-'} | {p.name}")
    elif args.cmd == "source":
        for p, m, _ in notes:
            if any(args.slug in s for s in m.get("sources") or []):
                print(f"{m.get('brand','')} | {m.get('name','')} | {p.name}")


if __name__ == "__main__":
    main()
