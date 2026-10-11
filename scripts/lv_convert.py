#!/usr/bin/env python3
"""Convert cached Likumi.lv pages to LawCodex Markdown.

  lv_convert.py [likumi] [mk-noteikumi] [--en] [--only ID]

Output (relative to the repository root):
  satversme/latvijas-republikas-satversme.md
  likumi/<year adopted>/<id>-<slug>.md
  mk-noteikumi/<year adopted>/<id>-<slug>.md
  en/... (same layout) for official English translations, when --en is given
"""
import datetime
import json
import os
import re
import sys

from bs4 import BeautifulSoup, NavigableString, Tag

from common import BASE, RAW, has_body, read_cache, robots_disallowed_ids

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = datetime.date.today()
SATVERSME_ID = "57980"

TYPES = {"likumi": "act", "mk-noteikumi": "regulation"}

# ---------------------------------------------------------------- inline rendering

WS = re.compile(r"[ \t\r\n ]+")


def norm(s):
    return WS.sub(" ", s)


def inline(node, in_table=False):
    """Render inline content of a node to Markdown text (single line)."""
    out = []
    for c in node.children if isinstance(node, Tag) else [node]:
        if isinstance(c, NavigableString):
            if type(c).__name__ in ("Comment", "Doctype", "ProcessingInstruction"):
                continue
            out.append(norm(str(c)))
            continue
        if not isinstance(c, Tag):
            continue
        name = c.name.lower()
        if name in ("script", "style"):
            continue
        if name == "br":
            out.append("<br>" if in_table else "\n")
        elif name in ("b", "strong"):
            t = inline(c, in_table)
            out.append(wrap(t, "**"))
        elif name in ("i", "em"):
            t = inline(c, in_table)
            out.append(wrap(t, "*"))
        elif name in ("sup", "sub"):
            t = inline(c, in_table).strip()
            out.append(f"<{name}>{t}</{name}>" if t else "")
        elif name == "img":
            src = c.get("src", "")
            if src and not src.startswith("http"):
                src = BASE + ("" if src.startswith("/") else "/") + src
            alt = norm(c.get("alt", "")).strip()
            out.append(f"![{alt}]({src})" if src else "")
        elif name == "u":
            out.append(inline(c, in_table))
        else:
            out.append(inline(c, in_table))
    return "".join(out)


def wrap(t, mark):
    if not t.strip():
        return t
    lead = t[: len(t) - len(t.lstrip())]
    trail = t[len(t.rstrip()):]
    return f"{lead}{mark}{t.strip()}{mark}{trail}"


def clean_line(s):
    s = re.sub(r"[ \t]+", " ", s)
    s = "\n".join(x.strip() for x in s.split("\n"))
    s = re.sub(r"\n{2,}", "\n", s).strip()
    s = s.replace("****", "")
    return s


# ---------------------------------------------------------------- tables

def render_table(t):
    rows = t.find_all("tr")
    simple = not t.find(["table"], recursive=True) or True
    grid = []
    for tr in rows:
        if tr.find_parent("table") is not t:
            continue
        cells = [c for c in tr.find_all(["td", "th"], recursive=False)]
        if any(int(c.get("colspan", 1) or 1) > 1 or int(c.get("rowspan", 1) or 1) > 1 for c in cells):
            simple = False
        if any(c.find("table") for c in cells):
            simple = False
        grid.append([clean_line(cell_text(c)).replace("\n", "<br>").replace("|", "\\|") for c in cells])
    if not grid:
        return ""
    width = max(len(r) for r in grid)
    if simple and width > 0 and all(len(r) == width for r in grid):
        lines = ["| " + " | ".join(grid[0]) + " |", "|" + " --- |" * width]
        for r in grid[1:]:
            lines.append("| " + " | ".join(r) + " |")
        return "\n".join(lines)
    return html_table(t)


def cell_text(c):
    parts = []
    for blk in blocks(c, in_table=True):
        parts.append(blk)
    return "<br>".join(p.replace("\n\n", "<br>").replace("\n", "<br>") for p in parts if p)


def html_table(t):
    """Keep complex tables as minimal HTML (only rowspan/colspan attributes kept)."""
    def rec(node):
        if isinstance(node, NavigableString):
            return norm(str(node)).replace("<", "&lt;").replace(">", "&gt;")
        name = node.name.lower()
        if name in ("table", "thead", "tbody", "tfoot", "tr", "td", "th"):
            attrs = ""
            for a in ("colspan", "rowspan"):
                v = node.get(a)
                if v and str(v) != "1":
                    attrs += f' {a}="{v}"'
            inner = "".join(rec(c) for c in node.children)
            if name in ("td", "th"):
                inner = inner.strip()
            sep = "\n" if name in ("table", "thead", "tbody", "tfoot", "tr") else ""
            return f"<{name}{attrs}>{sep}{inner}</{name}>\n" if name != "td" and name != "th" else f"<{name}{attrs}>{inner}</{name}>"
        if name in ("b", "strong"):
            return "<b>" + "".join(rec(c) for c in node.children) + "</b>"
        if name in ("i", "em"):
            return "<i>" + "".join(rec(c) for c in node.children) + "</i>"
        if name in ("sup", "sub"):
            return f"<{name}>" + "".join(rec(c) for c in node.children) + f"</{name}>"
        if name == "br":
            return "<br>"
        if name == "p" or name == "div":
            inner = "".join(rec(c) for c in node.children).strip()
            return inner + "<br>" if inner else ""
        if name == "img":
            src = node.get("src", "")
            if src and not src.startswith("http"):
                src = BASE + ("" if src.startswith("/") else "/") + src
            return f'<img src="{src}" alt="{node.get("alt", "")}">'
        if name in ("script", "style"):
            return ""
        return "".join(rec(c) for c in node.children)
    s = rec(t)
    s = re.sub(r"(<br>)+</t([dh])>", r"</t\2>", s)
    s = re.sub(r"\n\s*\n", "\n", s)
    return s.strip()


# ---------------------------------------------------------------- block rendering

BLOCK_TAGS = {"p", "div", "center", "table", "ul", "ol", "li", "h1", "h2", "h3", "h4", "h5", "h6",
              "blockquote", "pre", "dl", "dt", "dd", "hr", "tbody", "form"}


def blocks(node, in_table=False):
    """Render the children of a container to a list of Markdown blocks."""
    out = []
    buf = []

    def flush():
        if buf:
            t = clean_line("".join(buf))
            if t:
                out.append(t)
            buf.clear()

    for c in node.children:
        if isinstance(c, NavigableString):
            if type(c).__name__ in ("Comment", "Doctype"):
                continue
            buf.append(norm(str(c)))
            continue
        if not isinstance(c, Tag):
            continue
        name = c.name.lower()
        if name in ("script", "style"):
            continue
        if name == "br":
            buf.append("<br>" if in_table else "\n")
            continue
        if name not in BLOCK_TAGS:
            if c.find(list(BLOCK_TAGS)):
                flush()
                out.extend(blocks(c, in_table))
            else:
                buf.append(inline(c, in_table))
            continue
        flush()
        if name == "table":
            if in_table:
                out.append(html_table(c))
            else:
                out.append(render_table(c))
        elif name in ("ul", "ol"):
            items = []
            for i, li in enumerate(c.find_all("li", recursive=False), 1):
                t = " ".join(blocks(li, in_table)).replace("\n", " ")
                items.append(("- " if name == "ul" else f"{i}. ") + t)
            if items:
                out.append("\n".join(items))
        elif name == "hr":
            continue
        elif name == "p" and "labojumu_pamats" in (c.get("class") or []):
            t = clean_line(inline(c, in_table))
            if t:
                out.append(wrap(t, "*") if not in_table else t)
        elif c.find(list(BLOCK_TAGS - {"p"}) + ["p"]) and name != "p":
            out.extend(blocks(c, in_table))
        else:
            t = clean_line(inline(c, in_table))
            if t:
                out.append(t)
    flush()
    return [b for b in out if b and b.strip()]


# ---------------------------------------------------------------- structure

def heading_rank(text):
    t = text.lower()
    head = t[:60]
    if re.search(r"apakšnodaļa", head):
        return 4
    if re.search(r"nodaļa", head):
        return 3
    if re.search(r"nodalījums|sadaļa", head):
        return 2
    if re.search(r"\bdaļa\b", head):
        return 1
    return 3


def strip_noise(body):
    for sel in ["div.panta-doc-npk", "div.info-icon-wrapper", "div.panta-piezimite", "div.court",
                "a.p_id", "a.satura_raditajs", "div.notify-msg", "style", "script",
                "div.tooltip", "div.ico-status"]:
        for el in body.select(sel):
            el.decompose()


STRUCT_RE = re.compile(r"^([IVXLC]+\.?\s|\d+\.\s*)?(\S+\s+)?(daļa|sadaļa|nodaļa|apakšnodaļa|nodalījums)\b"
                       r"|^(pārejas noteikumi|noslēguma jautājumi|informatīva atsauce|\S+ pielikums)", re.I)
ART_RE = re.compile(r"^\d+(<sup>\d+</sup>)?\.\s*pants\b")
STRUCT_RE_EN = re.compile(r"^(part|division|chapter|sub-chapter|subchapter|title|transitional provisions|"
                          r"closing provisions|informative reference|annex)\b", re.I)
ART_RE_EN = re.compile(r"^section \d+(<sup>\d+</sup>)?\.", re.I)


def heading_rank_en(text):
    t = text.lower()
    if t.startswith(("sub-chapter", "subchapter")):
        return 4
    if t.startswith("chapter"):
        return 3
    if t.startswith(("division", "title")):
        return 2
    if t.startswith("part") or t.endswith(" part"):
        return 1
    return 3


def is_bold_block(el):
    style = (el.get("style") or "").replace(" ", "").lower()
    if "font-weight:bold" in style:
        return True
    text = norm(el.get_text()).strip()
    b = el.find(["b", "strong"])
    return bool(text) and b is not None and norm(b.get_text()).strip() == text


def unwrap_layout_tables(root):
    """English pages wrap the consolidation note in a one-cell layout table."""
    for t in root.find_all("table", recursive=False):
        cells = t.find_all(["td", "th"])
        if len(cells) == 1:
            t.replace_with(cells[0])
            cells[0].name = "div"


def convert_neko(neko, title, en=False):
    """Pages without the publisher's structural markup: plain HTML paragraphs.

    Used for recent Latvian texts not yet structured ("neko-body") and for the English
    translations. Headings are recognised heuristically: <h*> elements and bold paragraphs
    like "N. pants. ..." / "Section N. ..." (articles) or "... nodaļa" / "Chapter ..." (structure).
    """
    sre, are, rank = (STRUCT_RE_EN, ART_RE_EN, heading_rank_en) if en else (STRUCT_RE, ART_RE, heading_rank)
    unwrap_layout_tables(neko)
    els = [c for c in neko.children if isinstance(c, Tag)]
    kinds = []
    for el in els:
        t = norm(el.get_text()).strip()
        if el.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            if t.rstrip(".").lower() != norm(title).rstrip(".").lower():
                kinds.append(rank(t))
        elif el.name in ("p", "div") and is_bold_block(el) and sre.search(t) and len(t) < 300:
            kinds.append(rank(t))
    ranks = sorted(set(kinds))
    level_of = {r: i + 2 for i, r in enumerate(ranks)}
    art_level = min(6, len(ranks) + 2)
    md = []
    title_seen = False
    for el in els:
        t = clean_line(inline(el)).replace("\n", " ")
        plain = norm(el.get_text()).strip()
        if el.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            if not title_seen and plain.rstrip(".").lower() == norm(title).rstrip(".").lower():
                title_seen = True
                continue
            if plain:
                md.append("#" * level_of.get(rank(plain), 2) + " " + t.replace("**", "").strip())
            continue
        if el.name in ("p", "div") and plain and len(plain) < 300 and is_bold_block(el):
            ht = t.replace("**", "").strip()
            if are.search(ht):
                md.append("#" * art_level + " " + ht)
                continue
            if sre.search(plain):
                md.append("#" * level_of.get(rank(plain), 2) + " " + ht)
                continue
        md.extend(blocks(wrap_single(el)))
    return md


def wrap_single(el):
    holder = BeautifulSoup("<div></div>", "lxml").div
    holder.append(el.extract() if el.parent is not None else el)
    return holder


def convert_body(body, title="", en=False):
    strip_noise(body)
    if en:
        for el in body.select("div.notify-wrapper"):
            el.decompose()
        return convert_neko(body, title, en=True)
    neko = body.select_one("div.neko-body")
    if neko is not None:
        return convert_neko(neko, title)
    children = [c for c in body.children if isinstance(c, Tag)]

    # structural levels present
    ranks = sorted({heading_rank(clean_line(inline(c))) for c in children
                    if "TV212" in (c.get("class") or []) and "P218" not in (c.get("class") or [])})
    level_of = {r: i + 2 for i, r in enumerate(ranks)}
    art_level = min(6, (len(ranks) + 2))

    md = []
    annex = False
    for c in children:
        cls = c.get("class") or []
        main = cls[0] if cls else ""
        pfx = c.get("data-pfx") or ""
        if main == "TV207":
            continue  # title, rendered as H1 from metadata
        if main in ("TV214", "TV403", "TV218"):
            t = clean_line(inline(c)).replace("\n", " ")
            if t:
                md.append("## " + t)
            annex = main == "TV218"
            if main == "TV214":
                annex = False
            continue
        if main == "TV212":
            # heading text without its amendment note
            notes = [n.extract() for n in c.find_all("p", class_="labojumu_pamats")]
            t = clean_line(inline(c)).replace("\n", " ")
            if t:
                if annex or "P218" in cls:
                    lvl = 3
                else:
                    lvl = level_of.get(heading_rank(t), 3)
                md.append("#" * lvl + " " + t)
            for n in notes:
                nt = clean_line(inline(n))
                if nt:
                    md.append(wrap(nt, "*"))
            continue
        if main == "TV213" and pfx == "p" and not annex:
            first = c.find("p", class_="TVP")
            if first is not None:
                bold = first.find(["b", "strong"])
                full = clean_line(inline(first))
                if bold is not None:
                    bt = clean_line(inline(bold))
                    rest = norm(first.get_text()).strip()
                    if bt and norm(bold.get_text()).strip() == rest and re.search(r"pants", bt):
                        md.append("#" * art_level + " " + bt.replace("\n", " "))
                        first.decompose()
            md.extend(blocks(c))
            continue
        md.extend(blocks(c))
    return md


# ---------------------------------------------------------------- metadata

def parse_pase(soup):
    meta = {}
    pase = None
    for el in soup.find_all(string=re.compile("Tiesību akta pase")):
        pase = el.find_parent(["div", "td"])
        break
    container = pase.parent if pase is not None else soup
    for f in container.find_all("font", class_="fclg2"):
        label = norm(f.get_text()).strip().rstrip(":").strip()
        span = f.find_parent("span")
        if span is None:
            continue
        val = norm(span.get_text(" ")).strip()
        val = val[len(norm(f.get_text()).strip()):].strip()
        val = re.sub(r"\s+([,.;:])", r"\1", val)
        if label and label not in meta:
            meta[label] = val
    return meta


def dmy(s):
    m = re.search(r"(\d{2})\.(\d{2})\.(\d{4})", s or "")
    if not m:
        return None
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}"


def last_amended(html, doc_id):
    dates = []
    for y, mo, d in re.findall(rf"/ta/id/{doc_id}-[^/'\"]*/redakcijas-datums/(\d{{4}})/(\d{{2}})/(\d{{2}})", html):
        try:
            dt = datetime.date(int(y), int(mo), int(d))
        except ValueError:
            continue
        if dt <= TODAY:
            dates.append(dt)
    return max(dates).isoformat() if dates else None


def yq(s):
    s = (s or "").replace("\\", "\\\\").replace('"', '\\"')
    return f'"{s}"'


def slugify(s):
    import unicodedata
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def out_path(category, row, slug, en=False):
    doc_id = row["doc_id"]
    root = os.path.join(REPO, "en") if en else REPO
    if doc_id == SATVERSME_ID:
        return os.path.join(root, "satversme", "latvijas-republikas-satversme.md" if not en
                            else "the-constitution-of-the-republic-of-latvia.md")
    year = (row.get("izd_dat_date") or "")[-4:] or "unknown"
    name = f"{doc_id}-{slug}"[:96].rstrip("-") + ".md"
    return os.path.join(root, category, year, name)


def convert(category, row, en=False):
    doc_id = row["doc_id"]
    html = read_cache("en" if en else "html", doc_id)
    if html is None or html.startswith("NO-OFFICIAL-TRANSLATION"):
        return None
    if not en and not has_body(html):
        print(f"  empty body: {doc_id}", flush=True)
        return None
    soup = BeautifulSoup(html, "lxml")
    body = soup.select_one("div.doc-body")
    if body is None:
        return None
    meta = parse_pase(soup)
    title = norm(meta.get("Nosaukums") or meta.get("Title") or "").strip()
    if not title:
        t = soup.find("title")
        title = norm(t.get_text()).strip() if t else ""
    m = re.search(r"href='/ta/id/" + doc_id + r"-([a-z0-9-]+)'", html)
    lv_slug = m.group(1) if m else slugify(title)
    if en:
        em = re.search(r"/ta/en/en/id/" + doc_id + r"-([a-z0-9-]+)", html)
        slug = em.group(1) if em else lv_slug
    else:
        slug = lv_slug
    path = out_path(category, row, slug, en)

    title_lv = title
    tr_note = None
    if en:
        nm = body.select_one("div.notify-msg")
        if nm is not None:
            tr_note = norm(nm.get_text(" ")).strip()
            tr_note = re.sub(r"\s+([,.;:])", r"\1", tr_note)
        h = body.find(["h2", "h3"])
        if h is not None and norm(h.get_text()).strip():
            title = norm(h.get_text()).strip()
    md_body = convert_body(body, title, en)
    if doc_id == SATVERSME_ID:
        dtype = "constitution"
    else:
        dtype = TYPES[category]
    date = dmy(meta.get("Pieņemts") or meta.get("Adoption")) or dmy(row.get("izd_dat"))
    in_force = dmy(meta.get("Stājas spēkā") or meta.get("Entry into force")) or dmy(row.get("sst_dat"))
    amended = last_amended(html, doc_id)
    number = (row.get("numurs_txt") or row.get("numurs") or "").strip()
    src = f"{BASE}/ta/{'en/en/' if en else ''}id/{doc_id}-{slug}"
    fm = ["---", f"title: {yq(title)}",
          f"identifier: {yq(('MK noteikumi Nr. ' + number) if category == 'mk-noteikumi' and number else 'likumi.lv ' + doc_id)}",
          f"likumi_lv_id: {doc_id}",
          f"type: {dtype}",
          "jurisdiction: lv",
          f"language: {'en' if en else 'lv'}"]
    if en:
        fm.append("translation: true")
        fm.append(f"translation_of: {yq(BASE + '/ta/id/' + doc_id + '-' + lv_slug)}")
        fm.append(f"title_lv: {yq(title_lv)}")
        fm.append(f"translator: {yq('Valsts valodas centrs (State Language Centre)')}")
        if tr_note:
            fm.append(f"translation_note: {yq(tr_note)}")
    if number:
        fm.append(f"number: {yq(number)}")
    if meta.get("Izdevējs") or meta.get("Issuer"):
        fm.append(f"issuer: {yq(meta.get('Izdevējs') or meta.get('Issuer'))}")
    if date:
        fm.append(f"date: {date}")
    if in_force:
        fm.append(f"entry_into_force: {in_force}")
    if amended and not en:
        fm.append(f"last_amended: {amended}")
    pub = meta.get("Publicēts") or meta.get("Published")
    if pub:
        fm.append(f"published: {yq(pub)}")
    fm += ["status: in_force", f"source: {yq(src)}", f"retrieved: {TODAY.isoformat()}", "---", ""]
    text = "\n".join(fm) + "\n# " + title + "\n\n" + "\n\n".join(md_body) + "\n"
    text = re.sub(r"\n{3,}", "\n\n", text)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return path


def main():
    args = sys.argv[1:]
    en = "--en" in args
    only = None
    if "--only" in args:
        only = args[args.index("--only") + 1]
    names = [a for a in args if not a.startswith("--") and a != only] or ["likumi", "mk-noteikumi"]
    skip = robots_disallowed_ids()
    for name in names:
        rows = json.load(open(os.path.join(RAW, "lists", f"{name}.json"), encoding="utf-8"))
        done = missing = 0
        for row in rows:
            if only and row["doc_id"] != only:
                continue
            if row["doc_id"] in skip:
                continue
            try:
                p = convert(name, row, en)
            except Exception as e:
                print(f"  ERROR {row['doc_id']}: {e!r}", flush=True)
                raise
            if p:
                done += 1
            else:
                missing += 1
        print(f"{name}{' (en)' if en else ''}: {done} converted, {missing} not cached", flush=True)


if __name__ == "__main__":
    main()
