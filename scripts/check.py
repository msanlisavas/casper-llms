#!/usr/bin/env python3
"""The weekly check: is every catalogued capability still reachable, and was every guide
verified against the latest releases? Read-only - it never edits the catalog or a guide.

Prints a markdown report and exits 1 when anything needs attention; the check workflow turns
that into one tracking issue.

Usage:  GITHUB_TOKEN=$(gh auth token) python scripts/check.py [--report report.md]
"""
from __future__ import annotations

import concurrent.futures
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

import catalog
from generate import UA, fetch_markdown, http_get, latest_release, released_docs_dir, version_of

INITIALIZE = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
    "protocolVersion": "2025-06-18", "capabilities": {},
    "clientInfo": {"name": "casper-llms-check", "version": "1.0"}}}).encode()

# How to find the latest release of each component a guide can be verified against.
LATEST = {
    "casper-node": lambda: latest_release("casper-network/casper-node"),
    "casper-client-rs": lambda: latest_release("casper-ecosystem/casper-client-rs"),
    "docs.casper.network": lambda: version_of(released_docs_dir("casper-network/docs-redux", "main")),
}

REPO_PAGE = re.compile(r"^https://github\.com/[^/]+/[^/#?]+/?$")

# Package pages that answer bots badly are checked on their registry's API instead.
REGISTRY_APIS = [
    (re.compile(r"^https://www\.nuget\.org/packages/([^/?#]+)"),
     lambda m: f"https://api.nuget.org/v3-flatcontainer/{m[1].lower()}/index.json"),
    (re.compile(r"^https://www\.npmjs\.com/package/((?:@[^/]+/)?[^/?#]+)"), lambda m: f"https://registry.npmjs.org/{m[1]}"),
    (re.compile(r"^https://crates\.io/crates/([^/?#]+)"), lambda m: f"https://crates.io/api/v1/crates/{m[1]}"),
    (re.compile(r"^https://pypi\.org/project/([^/?#]+)"), lambda m: f"https://pypi.org/pypi/{m[1]}/json"),
]


def http_post_json(url: str, body: bytes) -> tuple[int, str, str]:
    """POST and read until the first JSON-RPC line: a Streamable HTTP server may answer with an
    event stream that need not close promptly."""
    request = urllib.request.Request(url, data=body, method="POST", headers={
        "User-Agent": UA, "Content-Type": "application/json", "Accept": "application/json, text/event-stream"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            seen = []
            for raw in response:
                line = raw.decode("utf-8", errors="replace")
                seen.append(line)
                if '"jsonrpc"' in line or sum(map(len, seen)) > 65536:
                    break
            return response.status, response.headers.get("Content-Type", ""), "".join(seen)
    except urllib.error.HTTPError as error:
        return error.code, error.headers.get("Content-Type", "") if error.headers else "", ""
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        return 0, "", str(error)


def probe_mcp(url: str, post=http_post_json) -> str | None:
    status, content_type, body = post(url, INITIALIZE)
    if status in (401, 402, 403):      # alive: it wants credentials or a payment
        return None
    if status == 200 and '"jsonrpc"' in body:
        return None
    if status == 0:
        return f"{url} unreachable ({body})"
    return f"{url} answered initialize with HTTP {status} {content_type}".rstrip()


def probe_repo(url: str, get=http_get) -> str | None:
    match = re.match(r"^https://github\.com/([^/]+/[^/#?]+)", url)
    if not match:
        status, _, _ = get(url)
        return None if status == 200 else f"{url}: HTTP {status}"
    status, _, body = get(f"https://api.github.com/repos/{match[1].removesuffix('.git')}", api=True)
    if status != 200:
        return f"{url}: repository answered HTTP {status}"
    return "repository is archived" if json.loads(body or "{}").get("archived") else None


def probe_package(url: str, get=http_get) -> str | None:
    for pattern, api in REGISTRY_APIS:
        match = pattern.match(url)
        if match:
            status, _, _ = get(api(match))
            return None if status == 200 else f"{url}: package registry answered HTTP {status}"
    status, _, _ = get(url)
    return None if status == 200 else f"{url}: HTTP {status}"


def probe_entry(entry: dict, get=http_get, post=http_post_json, fetch=fetch_markdown) -> list[str]:
    problems = []
    body, why = fetch(entry["docs"]["fetch"])
    if body is None:
        problems.append(f"documentation {entry['docs']['fetch']}: {why}")
    status, _, _ = get(entry["docs"]["cite"])
    if status != 200:
        problems.append(f"documentation page {entry['docs']['cite']}: HTTP {status}")
    kind, problem = entry["kind"], None
    if kind == "mcp-server" and entry.get("hosting") == "hosted":
        problem = probe_mcp(entry["url"], post)
    elif kind in ("mcp-server", "plugin"):
        # Its repository if it has one; else its package, checked on the registry API because
        # npmjs.com and crates.io turn scripted requests away.
        if entry.get("source") or not any(p.match(entry["url"]) for p, _ in REGISTRY_APIS):
            problem = probe_repo(entry.get("source") or entry["url"], get)
        else:
            problem = probe_package(entry["url"], get)
    elif kind in ("llms-txt", "agent-skill") and entry["url"] != entry["docs"]["fetch"]:
        if REPO_PAGE.match(entry["url"]):    # a repository of several skills: its page is HTML by design
            problem = probe_repo(entry["url"], get)
        else:
            body, why = fetch(entry["url"])
            problem = None if body is not None else f"{entry['url']}: {why}"
    elif kind == "api":
        status, _, _ = get(entry["url"])
        problem = None if 0 < status < 500 else f"{entry['url']}: HTTP {status}"
    elif kind == "sdk":
        problem = probe_package(entry["url"], get)
    return problems + ([problem] if problem else [])


def stale_guides(guides: list[catalog.Guide], latest: dict[str, str]) -> list[str]:
    return [f"{g.path}: verified against {name} {version}; the latest is {latest[name]}"
            for g in guides for name, version in g.versions.items()
            if name in latest and latest[name].lstrip("v") != version.lstrip("v")]


def main(argv: list[str]) -> int:
    entries = catalog.load_json(catalog.ROOT / "catalog.json")["capabilities"]
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(probe_entry, entries))
        # One retry for anything that failed, so a single slow response is not a weekly issue.
        retry = [i for i, problems in enumerate(results) if problems]
        for i, problems in zip(retry, pool.map(probe_entry, [entries[i] for i in retry])):
            results[i] = problems
    guides, _ = catalog.local_guides()
    needed = {name for g in guides for name in g.versions}
    stale = stale_guides(guides, {name: LATEST[name]() for name in needed if name in LATEST})

    failing = [(e, p) for e, p in zip(entries, results) if p]
    lines = ["# Weekly check", "", "## Capabilities that did not answer", ""]
    lines += [f"- **{e['name']}** (`{e['id']}`): " + "; ".join(p) for e, p in failing] or ["None."]
    lines += ["", "## Guides to re-verify", ""]
    lines += [f"- {s}" for s in stale] or ["None."]
    counted = f"{len(entries)} capabilit{'y' if len(entries) == 1 else 'ies'} and {len(guides)} guide{'' if len(guides) == 1 else 's'}"
    lines += ["", f"Checked {counted}. Nothing is edited automatically: fix catalog.json, or re-verify the guide "
              "and update its verification line."]
    report = "\n".join(lines) + "\n"
    print(report)
    if "--report" in argv:
        Path(argv[argv.index("--report") + 1]).write_text(report, encoding="utf-8")
    return 1 if failing or stale else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
