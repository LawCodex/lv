#!/usr/bin/env python3
"""Download the consolidated (current) text page of every listed act from Likumi.lv.

Reads _raw/lv/lists/<name>.json (from lv_list.py) and caches each page as
_raw/lv/html/<id//10000>/<id>.html.gz. Already cached pages are skipped.

  lv_fetch.py [likumi] [mk-noteikumi]          Latvian consolidated texts
  lv_fetch.py --en likumi                       official English translations (where linked)
"""
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor

from common import BASE, RAW, get, read_cache, robots_disallowed_ids, write_cache


def ids_for(name):
    rows = json.load(open(os.path.join(RAW, "lists", f"{name}.json"), encoding="utf-8"))
    return [r["doc_id"] for r in rows]


def main():
    args = sys.argv[1:]
    en = "--en" in args
    names = [a for a in args if not a.startswith("--")] or ["likumi", "mk-noteikumi"]
    skip = robots_disallowed_ids()
    for name in names:
        ids = ids_for(name)
        print(f"{name}: {len(ids)} documents", flush=True)
        todo = [d for d in ids if d not in skip]
        for d in ids:
            if d in skip:
                print(f"  skip {d} (robots.txt)", flush=True)
        # Requests are serialised by the global Crawl-delay throttle in common.get();
        # the small pool only overlaps slow server responses, it never exceeds 1 req/s.
        with ThreadPoolExecutor(max_workers=3) as pool:
            for n, _ in enumerate(pool.map(lambda d: fetch_one(d, en), todo), 1):
                if n % 100 == 0:
                    print(f"  {name}: {n}/{len(todo)}", flush=True)


def fetch_one(doc_id, en):
    try:
        if en:
            lv = read_cache("html", doc_id)
            if lv is None:
                return
            m = re.search(r"href='(/ta/en/en/id/[^']+)'", lv)
            if not m or read_cache("en", doc_id) is not None:
                return
            r = get(BASE + m.group(1))
            if r.status_code == 200 and "doc-body" in r.text:
                write_cache("en", doc_id, r.text)
            else:
                print(f"  FAILED en {doc_id}: HTTP {r.status_code}", flush=True)
        else:
            if read_cache("html", doc_id) is not None:
                return
            r = get(f"{BASE}/ta/id/{doc_id}")
            if r.status_code == 200 and "doc-body" in r.text:
                write_cache("html", doc_id, r.text)
            else:
                print(f"  FAILED {doc_id}: HTTP {r.status_code}", flush=True)
    except Exception as e:
        print(f"  ERROR {doc_id}: {e!r}", flush=True)

if __name__ == "__main__":
    main()
