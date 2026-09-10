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
- the plugin marketplace must be well formed, and nothing a plugin ships can run a command or leak
  a credential: only remote MCP servers on reviewed hosts, each header reading only that host's
  key variable, no credentials or ${...} in URLs, no hooks or commands, a token scan over every
  shipped file, and plugins from other repositories pinned to a reviewed commit.

Usage:  python scripts/validate.py        exit status 1 if anything breaks a rule.
"""
from __future__ import annotations

import json
import re
import sys
import urllib.parse
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
SHA = re.compile(r"^[0-9a-f]{40}$")
# A header value names an environment variable; it never carries the credential itself.
ENV_HEADER = re.compile(r"^(?:Bearer )?\$\{([A-Z][A-Z0-9_]*)\}$")
# Every host a plugin here may connect to, and the only variables its headers may read. Claude
# Code expands ${VAR} from the user's WHOLE environment, so an unlisted variable such as
# ${GITHUB_TOKEN} would be sent to the host. Adding a host is a reviewed change to this table.
HEADER_VARIABLES = {
    "mcp.cspr.trade": set(),
    "mcp.cspr.cloud": {"CSPR_CLOUD_API_KEY"},
    "mcp.testnet.cspr.cloud": {"CSPR_CLOUD_API_KEY"},
    "casperai.ekolsoft.com": {"CASPERAI_API_KEY"},
}
MARKETPLACE_KEYS = {"name", "owner", "metadata", "plugins"}
ENTRY_KEYS = {"name", "source", "description", "category", "tags", "version", "author", "homepage",
              "repository", "license", "keywords"}
MANIFEST_KEYS = {"name", "description", "version", "author", "homepage", "repository", "license", "keywords"}
SERVER_KEYS = {"type", "url", "headers"}
TOKEN = re.compile(r"cai_[A-Za-z0-9_-]{16,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}"
                   r"|xox[abprs]-[A-Za-z0-9-]{10,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----")


def read_json(path: Path, errors: list[str], name: str):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
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


def check_mcp_servers(servers, where: str) -> list[str]:
    """Remote servers only, on a reviewed host, reading only that host's key from the environment."""
    if not isinstance(servers, dict) or not servers:
        return [f"{where}: needs a non-empty mcpServers object"]
    errors = []
    for name, server in servers.items():
        at = f"{where} {name}"
        if not isinstance(server, dict):
            errors.append(f"{at}: must be an object")
            continue
        extra = sorted(set(server) - SERVER_KEYS)
        if extra:    # command/args/env (a local process), headersHelper (runs a command), ...
            errors.append(f"{at}: only type, url and headers are allowed here, not {', '.join(extra)}")
        if server.get("type") != "http":
            errors.append(f"{at}: only remote servers (type http) are shipped here")
        url = urllib.parse.urlsplit(str(server.get("url", "")))
        if url.scheme != "https" or url.username or url.password or url.query or url.fragment or "${" in url.geturl():
            errors.append(f"{at}: url must be a plain https URL with no credentials, query, fragment or ${{...}}")
        host = (url.hostname or "").lower()
        if host not in HEADER_VARIABLES:
            errors.append(f"{at}: {host or 'the url'} is not a reviewed host (add it to HEADER_VARIABLES in validate.py)")
        headers = server.get("headers") or {}
        if not isinstance(headers, dict):
            errors.append(f"{at}: headers must be an object")
            continue
        for header, value in headers.items():
            match = ENV_HEADER.match(str(value))
            if not match:
                errors.append(f"{at}: header {header} must come from an environment variable "
                              "(\"${NAME}\" or \"Bearer ${NAME}\"), never a literal value")
            elif match[1] not in HEADER_VARIABLES.get(host, set()):
                errors.append(f"{at}: header {header} may not read ${{{match[1]}}}; {host} may read only "
                              f"{', '.join(sorted(HEADER_VARIABLES.get(host, set()))) or 'no variable'}")
    return errors


def check_plugin_folder(folder: Path, name: str, root: Path) -> list[str]:
    rel = folder.relative_to(root).as_posix()
    errors: list[str] = []
    # Only a manifest, an MCP config and skills: hooks, commands, agents, LSP servers and scripts run
    # code on the user's machine and would need their own review rules before shipping here.
    for file in sorted(p for p in folder.rglob("*") if p.is_file()):
        inside = file.relative_to(folder).as_posix()
        if inside not in (".claude-plugin/plugin.json", ".mcp.json") and not (
                inside.startswith("skills/") and file.suffix == ".md"):
            errors.append(f"{rel}/{inside}: only .claude-plugin/plugin.json, .mcp.json and skills/**/*.md may ship")
        text = file.read_text(encoding="utf-8", errors="replace")
        if TOKEN.search(text):
            errors.append(f"{rel}/{inside}: contains what looks like a credential")
    manifest = folder / ".claude-plugin" / "plugin.json"
    if manifest.exists():
        data = read_json(manifest, errors, f"{rel}/.claude-plugin/plugin.json")
        if isinstance(data, dict):
            if data.get("name") != name:
                errors.append(f"{rel}: plugin.json name {data.get('name')!r} differs from the marketplace entry {name!r}")
            extra = sorted(set(data) - MANIFEST_KEYS)
            if extra:    # mcpServers, hooks, commands, agents... must not arrive by the back door
                errors.append(f"{rel}/.claude-plugin/plugin.json: unexpected keys {', '.join(extra)}")
        elif data is not None:
            errors.append(f"{rel}/.claude-plugin/plugin.json: must be an object")
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
        data = read_json(mcp, errors, f"{rel}/.mcp.json")
        if data is not None:
            errors += check_mcp_servers(data.get("mcpServers") if isinstance(data, dict) else None, f"{rel}/.mcp.json")
    if not manifest.exists() and not skills and not mcp.exists():
        errors.append(f"{rel}: has no plugin.json, skill or .mcp.json")
    return errors


def check_plugins(root: Path) -> list[str]:
    """The Claude Code marketplace in .claude-plugin/ and the plugins it ships. `claude plugin
    validate .` checks the same files more fully; this keeps CI free of that dependency, and adds
    what it does not: no credential, command or unreviewed host can ship in a plugin here, and a
    plugin from another repository is pinned to the commit that was reviewed."""
    path = root / ".claude-plugin" / "marketplace.json"
    if not path.exists():
        return []
    errors: list[str] = []
    market = read_json(path, errors, ".claude-plugin/marketplace.json")
    if market is None:
        return errors
    if not isinstance(market, dict):
        return [".claude-plugin/marketplace.json: must be an object"]
    if TOKEN.search(path.read_text(encoding="utf-8")):
        errors.append(".claude-plugin/marketplace.json: contains what looks like a credential")
    extra = sorted(set(market) - MARKETPLACE_KEYS)
    if extra:
        errors.append(f".claude-plugin/marketplace.json: unexpected keys {', '.join(extra)}")
    if not KEBAB.match(str(market.get("name", ""))):
        errors.append(".claude-plugin/marketplace.json: name must be kebab-case")
    if not isinstance(market.get("owner"), dict) or not market["owner"].get("name"):
        errors.append(".claude-plugin/marketplace.json: owner.name is required")
    plugins = market.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        return errors + [".claude-plugin/marketplace.json: plugins must be a non-empty list"]
    base = root.resolve()
    for number, plugin in enumerate(plugins):
        where = f".claude-plugin/marketplace.json plugins[{number}]"
        if not isinstance(plugin, dict):
            errors.append(f"{where}: must be an object")
            continue
        extra = sorted(set(plugin) - ENTRY_KEYS)
        if extra:    # mcpServers, hooks, strict... in an entry would bypass the folder checks
            errors.append(f"{where}: unexpected keys {', '.join(extra)}")
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
            # Unpinned, a plugin from another repository installs whatever its branch holds that day,
            # scripts included, and none of it passes this repository's review.
            if not SHA.match(str(source.get("sha", ""))):
                errors.append(f"{where}: a plugin from another repository must be pinned with a 40-character sha")
        else:
            errors.append(f"{where}: source is missing")
    return errors


def main() -> int:
    root_index = ROOT / "llms.txt"
    files = ([root_index] if root_index.exists() else []) + sorted(ROOT.glob("*/llms.txt"))
    errors = [] if root_index.exists() else ["llms.txt: missing; run python scripts/generate.py --catalog-only"]
    errors += [error for path in files for error in check(path)]
    try:
        catalog_errors = catalog.check_all(ROOT)
    except (OSError, UnicodeDecodeError, ValueError) as error:    # JSONDecodeError is a ValueError
        catalog_errors = [f"catalog.json or catalog.schema.json: not readable ({error})"]
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
