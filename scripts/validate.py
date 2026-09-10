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
  catalog.json, guides/ and the indexes render - a hand edit to any of them is overwritten;
- the plugin marketplace must be well formed, and no plugin may carry a credential: MCP headers
  take their values only from environment variables.

Usage:  python scripts/validate.py        exit status 1 if anything breaks a rule.
"""
from __future__ import annotations

import json
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


KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
# A header value must name an environment variable, never carry the credential itself.
ENV_HEADER = re.compile(r"^(Bearer )?\$\{[A-Z][A-Z0-9_]*\}$")


def read_json(path: Path, errors: list[str], name: str):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"{name}: not readable JSON ({error})")
        return None


def skill_frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.S)
    fields = {}
    for line in (match.group(1).splitlines() if match else []):
        key, sep, value = line.partition(":")
        if sep and not line.startswith((" ", "\t")):
            fields[key.strip()] = value.strip().strip("'\"")
    return fields


def check_plugin_folder(folder: Path, name: str, root: Path) -> list[str]:
    rel = folder.relative_to(root).as_posix()
    errors: list[str] = []
    manifest = folder / ".claude-plugin" / "plugin.json"
    if manifest.exists():
        data = read_json(manifest, errors, f"{rel}/.claude-plugin/plugin.json")
        if data is not None and data.get("name") != name:
            errors.append(f"{rel}: plugin.json name {data.get('name')!r} differs from the marketplace entry {name!r}")
    skills = sorted(folder.glob("skills/*/SKILL.md"))
    for skill in skills:
        where = skill.relative_to(root).as_posix()
        fm = skill_frontmatter(skill.read_text(encoding="utf-8"))
        skill_name = fm.get("name", "")
        if not KEBAB.match(skill_name) or len(skill_name) > 64:
            errors.append(f"{where}: frontmatter name must be lowercase letters, digits and hyphens, at most 64")
        elif skill_name != skill.parent.name:
            errors.append(f"{where}: frontmatter name {skill_name!r} must match its folder {skill.parent.name!r}")
        if not 1 <= len(fm.get("description", "")) <= 1024:
            errors.append(f"{where}: frontmatter description is required, at most 1024 characters")
    mcp = folder / ".mcp.json"
    if mcp.exists():
        data = read_json(mcp, errors, f"{rel}/.mcp.json") or {}
        servers = data.get("mcpServers")
        if not isinstance(servers, dict) or not servers:
            errors.append(f"{rel}/.mcp.json: needs a non-empty mcpServers object")
        for server_name, server in (servers if isinstance(servers, dict) else {}).items():
            where = f"{rel}/.mcp.json {server_name}"
            if server.get("type") not in ("http", "sse"):
                errors.append(f"{where}: only remote servers (type http) are shipped here")
            if not str(server.get("url", "")).startswith("https://"):
                errors.append(f"{where}: url must be https")
            for header, value in (server.get("headers") or {}).items():
                if not ENV_HEADER.match(str(value)):
                    errors.append(f"{where}: header {header} must come from an environment variable "
                                  "(\"${NAME}\" or \"Bearer ${NAME}\"), never a literal value")
    if not manifest.exists() and not skills and not mcp.exists():
        errors.append(f"{rel}: has no plugin.json, skill or .mcp.json")
    return errors


def check_plugins(root: Path) -> list[str]:
    """The Claude Code marketplace in .claude-plugin/ and the plugins it ships. `claude plugin
    validate .` checks the same files more fully; this keeps CI free of that dependency."""
    path = root / ".claude-plugin" / "marketplace.json"
    if not path.exists():
        return []
    errors: list[str] = []
    market = read_json(path, errors, ".claude-plugin/marketplace.json")
    if market is None:
        return errors
    if not KEBAB.match(str(market.get("name", ""))):
        errors.append(".claude-plugin/marketplace.json: name must be kebab-case")
    if not (market.get("owner") or {}).get("name"):
        errors.append(".claude-plugin/marketplace.json: owner.name is required")
    plugins = market.get("plugins") or []
    if not plugins:
        errors.append(".claude-plugin/marketplace.json: lists no plugins")
    base = root.resolve()
    for number, plugin in enumerate(plugins):
        where = f".claude-plugin/marketplace.json plugins[{number}]"
        name, source = str(plugin.get("name", "")), plugin.get("source")
        if not KEBAB.match(name):
            errors.append(f"{where}: name must be kebab-case")
        if isinstance(source, str):
            folder = (root / source).resolve()
            if not source.startswith("./") or not folder.is_relative_to(base) or not folder.is_dir():
                errors.append(f"{where}: source {source} is not a folder in this repository")
            else:
                errors += check_plugin_folder(folder, name, base)
        elif isinstance(source, dict):
            kind = source.get("source")
            if kind not in ("github", "url", "git-subdir"):
                errors.append(f"{where}: source type must be github, url or git-subdir")
            elif kind == "github" and not re.match(r"^[\w.-]+/[\w.-]+$", str(source.get("repo", ""))):
                errors.append(f"{where}: source repo must be owner/name")
            elif kind != "github" and not str(source.get("url", "")).startswith("https://"):
                errors.append(f"{where}: source url must be https")
        else:
            errors.append(f"{where}: source is missing")
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
    errors += check_plugins(ROOT)
    for error in errors:
        print(error)
    total = sum(1 for p in files for l in p.read_text(encoding="utf-8").splitlines() if l.startswith("- ["))
    print(f"{len(files)} indexes, {total} links, {len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
