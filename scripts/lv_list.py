#!/usr/bin/env python3
"""List the acts in force on Likumi.lv, by issuer and type.

Uses the JSON endpoint behind https://likumi.lv/ta/veids/<issuer>/<type> (the public
"Tiesību aktu veidi" listing):  /ajax/ties_akti_pec_veida.php
  spe=1   -> only acts currently in force ("spēkā esošs")
  ngr=1   -> hide amending acts ("Grozījumi ..."), whose content is already merged into the
             consolidated base acts.
Output: _raw/lv/lists/<name>.json
"""
import json
import os
import sys

from common import BASE, RAW, get

CATEGORIES = {
    # name: (izd_id, veids_id)
    "likumi": (138, 84),       # Saeima / likumi
    "mk-noteikumi": (92, 87),  # Ministru kabinets / noteikumi
}


def fetch_list(izd_id, veids_id, extra="spe=1&ngr=1"):
    url = (f"{BASE}/ajax/ties_akti_pec_veida.php?piece={{piece}}&mode=i&alpha=&izd_id={izd_id}"
           f"&veids_id={veids_id}&{extra}&oby=0&odir=0&tstamp=0")
    stats = get(url.format(piece=0) + "&qwstats=1").json()
    print(f"  {stats['rows']} rows in {stats['pieces']} pieces", flush=True)
    rows = []
    for piece in range(stats["pieces"]):
        rows.extend(get(url.format(piece=piece)).json())
    ids = {r["doc_id"] for r in rows}
    if len(ids) != stats["rows"]:
        print(f"  WARNING: got {len(ids)} unique ids, expected {stats['rows']}", flush=True)
    return rows


def main():
    os.makedirs(os.path.join(RAW, "lists"), exist_ok=True)
    names = sys.argv[1:] or list(CATEGORIES)
    for name in names:
        print(name, flush=True)
        rows = fetch_list(*CATEGORIES[name])
        with open(os.path.join(RAW, "lists", f"{name}.json"), "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=0)


if __name__ == "__main__":
    main()
