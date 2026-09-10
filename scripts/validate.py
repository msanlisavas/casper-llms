#!/usr/bin/env python3
"""Check every */llms.txt against the grammar LLM ingesters actually parse. Offline and fast.

The rules mirror CasperAI's LlmsTxtParser, the strictest consumer these indexes have. Each one
is a way a page silently disappears at ingestion rather than failing loudly:

- the file must start with an H1 ("# ") and contain no HTML;
- a link counts only as an unindented  - [title](url)  line under an H2 ("## ") heading - a
  link line that does not match that grammar is ignored;
- a relative or non-https URL fails the whole index in some ingesters, so every URL is absolute;
- the text after the colon is the citation URL and must be an absolute https URL;
- a section whose heading contains "(latest)" makes CasperAI drop other versioned sections;
- no fetch URL is listed twice, and no index exceeds 1000 links (CasperAI reads no further).

It also checks what is written by hand or rendered from it:

- catalog.json must satisfy catalog.schema.json, and each guide must open with its H1 and its
  "Verified against ..." line;
- the root llms.txt, directory.md, the README blocks and casper-guides/llms.txt must match what
  catalog.json, guides/ and the indexes render - a hand edit to any of them is overwritten.

Usage:  python scripts/validate.py        exit status 1 if anything breaks a rule.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import catalog

ROOT = Path(__file__).resolve().parent.parent
LINK = re.compile(r"^-\s*\[(?P<title>[^\]]+)\]\((?P<url>[^)\s]+)\)(\s*:\s*(?P<notes>.+))?\s*$")
HTTPS = re.compile(r"^https://[^\s/]+\S*$")
MAX_LINKS = 1000


def check(path: Path) -> list[str]:
    return check_text(path.read_text(encoding="utf-8"), path.relative_to(ROOT).as_posix())


def check_text(text: str, name: str) -> list[str]:
    errors: list[str] = []
    if text.startswith(chr(0xFEFF)):
        errors.append(f"{name}: starts with a byte-order mark")
    if not text.lstrip().startswith("# "):
        errors.append(f"{name}: does not start with an H1 ('# ')")
    if re.search(r"<(html|body|div|script)\b", text, re.I):
        errors.append(f"{name}: contains HTML")

    section = None
    seen: dict[str, int] = {}
    links = 0
    for number, line in enumerate(text.splitlines(), 1):
        where = f"{name}:{number}"
        if line.startswith("## "):
            section = line[3:].strip()
            if "(latest)" in section.lower():
                errors.append(f"{where}: section heading contains '(latest)', which drops other versioned sections")
            continue
        if not line.lstrip().startswith("- ["):
            continue
        if line != line.lstrip():
            errors.append(f"{where}: indented link line is ignored by ingesters")
            continue
        match = LINK.match(line)
        if not match:
            errors.append(f"{where}: link line does not match  - [title](url): citation")
            continue
        if section is None:
            errors.append(f"{where}: link appears before the first '## ' section and is ignored")
        url, notes = match.group("url"), (match.group("notes") or "").strip()
        if not HTTPS.match(url):
            errors.append(f"{where}: fetch URL is not absolute https: {url}")
        citation = notes.split()[0] if notes else ""
        if not HTTPS.match(citation):
            errors.append(f"{where}: missing or non-https citation URL after the colon")
        if url in seen:
            errors.append(f"{where}: fetch URL already listed on line {seen[url]}: {url}")
        seen.setdefault(url, number)
        links += 1

    if links == 0:
        errors.append(f"{name}: has no links")
    if links > MAX_LINKS:
        errors.append(f"{name}: {links} links; ingesters stop reading at {MAX_LINKS}")
    return errors


def main() -> int:
    root_index = ROOT / "llms.txt"
    files = ([root_index] if root_index.exists() else []) + sorted(ROOT.glob("*/llms.txt"))
    errors = [] if root_index.exists() else ["llms.txt: missing; run python scripts/generate.py --catalog-only"]
    errors += [error for path in files for error in check(path)]
    catalog_errors = catalog.check_all(ROOT)
    errors += catalog_errors
    if not catalog_errors:
        errors += [f"{path}: does not match catalog.json, guides/ and the indexes; "
                   "run python scripts/generate.py --catalog-only" for path in catalog.stale_outputs(ROOT)]
    for error in errors:
        print(error)
    total = sum(1 for p in files for l in p.read_text(encoding="utf-8").splitlines() if l.startswith("- ["))
    print(f"{len(files)} indexes, {total} links, {len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
