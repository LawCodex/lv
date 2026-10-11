# LawCodex — Latvia (Latvija)

Latvian national legislation **in force**, in consolidated form, converted from
[Likumi.lv](https://likumi.lv) — the official legal-acts portal maintained by the official
publisher *Latvijas Vēstnesis* — to Markdown. Original language: Latvian. Official English
translations by the State Language Centre (Valsts valodas centrs) are included separately in
`en/` where they exist, and are clearly marked as translations.

Retrieved: **2026-10-12**.

## Contents

| Directory | What | Files |
|---|---|---|
| `satversme/` | Latvijas Republikas Satversme (Constitution of 1922, consolidated) | __SAT__ |
| `likumi/<year>/` | Laws (*likumi*) in force, base acts only, consolidated text | __LIK__ |
| `mk-noteikumi/<year>/` | Cabinet regulations (*Ministru kabineta noteikumi*) in force, consolidated | __MK__ |
| `en/` | Official English translations (Valsts valodas centrs) of the above, same layout | __EN__ |

`<year>` is the year of adoption (*pieņemts*). File names are
`<likumi.lv id>-<likumi.lv slug>.md`, e.g. `likumi/1998/88966-kriminallikums.md`.

"Likumi" includes every act of type *likums* that Likumi.lv lists as in force, regardless of the
issuing body: laws of the Saeima, laws of the Supreme Council (Augstākā Padome, 1990–1993),
pre-war laws that were reinstated (e.g. the Civil Law of 1937, published both as a whole and
in its separate parts — Likumi.lv publishes both, and both are kept), the 1920 declaration of the
Constitutional Assembly, and laws ratifying international agreements (*Par ... līgumu*).
Amending laws (*Grozījumi ... likumā*) are not included as separate files, because their
content is already merged into the consolidated text of the act they amend.

## Format

Each file has YAML front matter followed by the text:

```yaml
---
title: "Krimināllikums"
identifier: "likumi.lv 88966"        # MK regulations: "MK noteikumi Nr. 630"
likumi_lv_id: 88966                  # document id on likumi.lv
type: act                            # constitution | act | regulation
jurisdiction: lv
language: lv
number: "630"                        # regulation number (MK noteikumi only)
issuer: "Saeima"
date: 1998-06-17                     # adopted (pieņemts)
entry_into_force: 1999-04-01         # stājas spēkā
last_amended: 2026-07-10             # latest amendment in-force date referenced in the text
published: "Latvijas Vēstnesis, 199/200, 08.07.1998.; ..."
status: in_force
source: "https://likumi.lv/ta/id/88966-kriminallikums"
retrieved: 2026-10-12
---
```

English files additionally carry `translation: true`, `translation_of`, `title_lv`, `translator`
and, when Likumi.lv flags it, `translation_note` (e.g. *"The translation of this document is
outdated. Translation validity: … Amendments not included: …"*). **English translations are
not legally binding and are often older than the Latvian consolidated text.**

Structure mapping: parts (*daļa*), divisions (*sadaļa*/*nodalījums*), chapters (*nodaļa*) and
sub-chapters (*apakšnodaļa*) become Markdown headings in that order; articles (*N. pants*)
become the next heading level; transitional provisions (*Pārejas noteikumi*), the EU-directive
reference note (*Informatīva atsauce uz Eiropas Savienības direktīvām*) and annexes
(*pielikumi*) are level-2 headings. Numbered points of Cabinet regulations stay as paragraphs.
The publisher's editorial amendment notes (e.g. *(Ar grozījumiem, kas izdarīti ar …)*) are kept
in italics, as on Likumi.lv. Simple tables are Markdown tables; tables with merged cells are kept
as minimal HTML. Images (formulas, signs, form samples) are linked to their URL on likumi.lv.

## Not covered

- Acts no longer in force (*zaudējis spēku*) and acts not yet in force (*vēl nav spēkā*).
- Historical versions (*redakcijas*) — only the current consolidated version is stored.
- Other Cabinet instruments: instructions (*instrukcijas*), orders (*rīkojumi*), recommendations,
  protocols; orders of the President and the Prime Minister.
- Regulations of the Bank of Latvia, the former FKTK, SPRK and other authorities; Constitutional
  Court judgments; binding regulations of municipalities (*saistošie noteikumi*).
- International treaties as separate documents (they are reachable through the ratifying laws).
- __GAPS__

## Sources

- Likumi.lv, https://likumi.lv — the consolidated texts (*konsolidētās versijas*) and the act
  metadata. Lists of in-force acts come from the portal's "Tiesību aktu veidi" listings
  (https://likumi.lv/ta/veids/saeima/likumi, https://likumi.lv/ta/veids/ministru-kabinets/noteikumi),
  with the options "in force" and "hide amending acts".
- English translations: Likumi.lv English pages (https://likumi.lv/ta/en/...), translated by
  Valsts valodas centrs (https://vvc.gov.lv).
- Open data: data.gov.lv was checked; it has no bulk dump of consolidated legislation (only the
  TAP portal's monthly lists of adopted acts and annotations, and a non-machine-readable
  translation catalogue), so the HTML portal is used.

Likumi.lv's consolidated texts are informative; the legally binding publication is the official
gazette *Latvijas Vēstnesis* (https://www.vestnesis.lv).

## Licence / copyright

Under Section 6 of the Latvian Copyright Law (*Autortiesību likums*), laws, regulations and
other normative acts and their official translations are not objects of copyright. The texts here
are therefore in the public domain. Consolidation and portal presentation are by Latvijas
Vēstnesis; English translations by Valsts valodas centrs.

## Regenerating

```sh
pip install -r scripts/requirements.txt
cd scripts
python lv_list.py                          # lists of in-force acts -> _raw/lv/lists/
python lv_fetch.py likumi mk-noteikumi     # Latvian pages -> _raw/lv/html/ (cached, gzip)
python lv_fetch.py --en likumi mk-noteikumi  # English pages where linked -> _raw/lv/en/
python lv_convert.py likumi mk-noteikumi   # -> satversme/, likumi/, mk-noteikumi/
python lv_convert.py --en likumi mk-noteikumi  # -> en/
```

The raw cache directory can be set with `LV_RAW`. The fetcher honours likumi.lv's robots.txt
(`Crawl-delay: 1`: a global throttle of one request per ~1.1 s, at most 3 requests in flight;
paths such as `search.php`, `doc.php` and `/redakcijas-datums/` are never requested) and skips the
document ids that robots.txt singles out. It sends the User-Agent
`LawCodex/1.0 (+https://github.com/LawCodex)`. A full run takes roughly 2 hours for the Latvian
texts plus the English pages.
