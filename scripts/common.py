"""Shared helpers for fetching from Likumi.lv (official publisher "Latvijas Vēstnesis").

Politeness: likumi.lv/robots.txt declares `Crawl-delay: 1`, so every request goes through a
single global throttle that waits at least DELAY seconds between requests (effectively
concurrency 1). Paths disallowed by robots.txt (search.php, doc.php, /redakcijas-datums/ ...)
are never requested. Raw pages are cached gzip-compressed under RAW so re-runs do not
re-download.
"""
import gzip
import os
import re
import threading
import time

import requests

UA = "LawCodex/1.0 (+https://github.com/LawCodex)"
BASE = "https://likumi.lv"
RAW = os.environ.get("LV_RAW", "/Users/magicaltux/projects/lawcodex/_raw/lv")
DELAY = 1.1  # robots.txt Crawl-delay: 1

_session = None
_lock = threading.Lock()
_last = [0.0]


def session():
    global _session
    if _session is None:
        _session = requests.Session()
        _session.headers.update({"User-Agent": UA, "Accept-Language": "lv,en;q=0.5"})
    return _session


def _throttle():
    with _lock:
        wait = _last[0] + DELAY - time.time()
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()


def get(url, **kw):
    """GET with crawl-delay throttle, retries and exponential backoff."""
    delay = 5
    for attempt in range(8):
        _throttle()
        try:
            r = session().get(url, timeout=180, **kw)
            if r.status_code == 200:
                return r
            if r.status_code in (400, 403, 404, 410):
                print(f"  HTTP {r.status_code} {url}", flush=True)
                return r
            print(f"  HTTP {r.status_code} {url} (attempt {attempt})", flush=True)
        except Exception as e:  # network error
            print(f"  {e!r} {url} (attempt {attempt})", flush=True)
        time.sleep(delay)
        delay = min(delay * 2, 300)
    raise RuntimeError(f"giving up on {url}")


def robots_disallowed_ids():
    """Document ids that likumi.lv/robots.txt singles out (`Disallow: /*id=NNN$`).

    These patterns technically target `?id=` URLs, but we skip those documents entirely
    to respect the publisher's intent.
    """
    path = os.path.join(RAW, "robots.txt")
    if not os.path.exists(path):
        r = get(BASE + "/robots.txt")
        os.makedirs(RAW, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(r.text)
    txt = open(path, encoding="utf-8").read()
    return set(re.findall(r"id[=*](\d+)", txt))


def cache_path(kind, doc_id):
    d = os.path.join(RAW, kind, str(int(doc_id) // 10000))
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, f"{doc_id}.html.gz")


def read_cache(kind, doc_id):
    p = cache_path(kind, doc_id)
    if os.path.exists(p):
        with gzip.open(p, "rt", encoding="utf-8") as f:
            return f.read()
    return None


def write_cache(kind, doc_id, text):
    p = cache_path(kind, doc_id)
    tmp = p + ".tmp"
    with gzip.open(tmp, "wt", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, p)
