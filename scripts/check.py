#!/usr/bin/env python3
"""The weekly check: is every catalogued capability still reachable, and was every guide
verified against the latest releases? Read-only - it never edits the catalog or a guide.

Prints a markdown report. Exit status 0: nothing to fix. 3: findings, written to the report.
Anything else is a crash, which the check workflow reports as a failed run rather than as
findings. Every probe has a wall-clock deadline and a size cap, and a probe that raises is
reported as a finding, so one misbehaving host cannot take the whole report down.

Usage:  GITHUB_TOKEN=$(gh auth token) python scripts/check.py [--report report.md]
"""
from __future__ import annotations

import concurrent.futures
import http.client
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import catalog
from generate import UA, fetch_markdown, latest_release, media_type, released_docs_dir, version_of

FINDINGS = 3
PROBE_SECONDS = 45      # whole-request budget for one probe
READ_TIMEOUT = 15       # per socket read
MAX_BYTES = 2_000_000   # enough to judge any documentation page

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

NETWORK_ERRORS = (urllib.error.URLError, OSError, http.client.HTTPException)


def plain(text: object, limit: int = 120) -> str:
    """Remote-influenced text as it may appear in the issue body: no markdown, no line breaks."""
    return re.sub(r"[^A-Za-z0-9 .,:/_-]", "", str(text))[:limit] or "no detail"


def location(headers) -> str:
    value = (headers.get("Location", "") if headers else "") or ""
    return value if re.fullmatch(r"https?://[A-Za-z0-9._~:/?#@!$&*+,;=%-]{1,300}", value) else "another location"


def read_bounded(response, until: bytes | None, seconds: int, cap: int) -> bytes:
    deadline = time.monotonic() + seconds
    buf = b""
    while len(buf) <= cap and (until is None or until not in buf):
        if time.monotonic() > deadline:
            raise TimeoutError(f"no complete response within {seconds} s")
        chunk = response.read1(65536)
        if not chunk:
            break
        buf += chunk
    return buf


def bounded_get(url: str, api: bool = False, seconds: int = PROBE_SECONDS) -> tuple[int, str, str]:
    headers = {"User-Agent": UA}
    token = os.environ.get("GITHUB_TOKEN")
    if api and token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=READ_TIMEOUT) as response:
            body = read_bounded(response, None, seconds, MAX_BYTES)
            return response.status, response.headers.get("Content-Type", ""), body.decode("utf-8", "replace")
    except urllib.error.HTTPError as error:
        return error.code, error.headers.get("Content-Type", "") if error.headers else "", ""
    except NETWORK_ERRORS as error:
        return 0, "", plain(f"{type(error).__name__} {error}")


def fetch(url: str) -> tuple[str | None, str]:
    return fetch_markdown(url, bounded_get)


class _McpRedirects(urllib.request.HTTPRedirectHandler):
    """MCP clients follow 307/308 with the POST body intact; urllib would refuse. A 301/302/303
    would turn the POST into a GET, so it surfaces as a move to report rather than a probe."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if code in (307, 308):
            return urllib.request.Request(newurl, data=req.data, method="POST", headers=dict(req.header_items()))
        raise urllib.error.HTTPError(req.full_url, code, msg, headers, fp)


_MCP_OPENER = urllib.request.build_opener(_McpRedirects)


def http_post_json(url: str, body: bytes, seconds: int = PROBE_SECONDS) -> tuple[int, str, str]:
    """POST and read until the first JSON-RPC line: a Streamable HTTP server may answer with an
    event stream that need not close promptly."""
    request = urllib.request.Request(url, data=body, method="POST", headers={
        "User-Agent": UA, "Content-Type": "application/json", "Accept": "application/json, text/event-stream"})
    try:
        with _MCP_OPENER.open(request, timeout=READ_TIMEOUT) as response:
            text = read_bounded(response, b'"jsonrpc"', seconds, 65536)
            return response.status, response.headers.get("Content-Type", ""), text.decode("utf-8", "replace")
    except urllib.error.HTTPError as error:
        moved = location(error.headers) if error.code in (301, 302, 303) else ""
        return error.code, error.headers.get("Content-Type", "") if error.headers else "", moved
    except NETWORK_ERRORS as error:
        return 0, "", plain(f"{type(error).__name__} {error}")


def http_get_stream(url: str, seconds: int = 30) -> tuple[int, str, str]:
    """GET a legacy HTTP+SSE endpoint and read until its 'event: endpoint' line. The stream never
    ends by itself; leaving the with-block closes it."""
    request = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/event-stream"})
    try:
        with urllib.request.urlopen(request, timeout=READ_TIMEOUT) as response:
            text = read_bounded(response, b"event: endpoint", seconds, 65536)
            return response.status, response.headers.get("Content-Type", ""), text.decode("utf-8", "replace")
    except urllib.error.HTTPError as error:
        return error.code, error.headers.get("Content-Type", "") if error.headers else "", ""
    except NETWORK_ERRORS as error:
        return 0, "", plain(f"{type(error).__name__} {error}")


def probe_mcp(url: str, post=http_post_json) -> str | None:
    status, content_type, body = post(url, INITIALIZE)
    if status in (401, 402, 403):      # alive: it wants credentials or a payment
        return None
    if status == 200 and '"jsonrpc"' in body:
        return None
    if status in (301, 302, 303):
        return f"{url} moved to `{body}`; update catalog.json"
    if status == 0:
        return f"{url} unreachable ({plain(body)})"
    return f"{url} answered initialize with HTTP {status} ({media_type(content_type)})"


def probe_sse(url: str, stream=http_get_stream) -> str | None:
    status, content_type, body = stream(url)
    if status in (401, 402, 403):
        return None
    if status == 200 and "event: endpoint" in body:
        return None
    if status == 0:
        return f"{url} unreachable ({plain(body)})"
    return f"{url} answered with HTTP {status} ({media_type(content_type)}) and no endpoint event"


def probe_repo(url: str, get=bounded_get) -> str | None:
    match = re.match(r"^https://github\.com/([^/]+/[^/#?]+)", url)
    if not match:
        status, _, _ = get(url)
        return None if status == 200 else f"{url}: HTTP {status}"
    status, _, body = get(f"https://api.github.com/repos/{match[1].removesuffix('.git')}", api=True)
    if status != 200:
        return f"{url}: repository answered HTTP {status}"
    return "repository is archived" if json.loads(body or "{}").get("archived") else None


def probe_package(url: str, get=bounded_get) -> str | None:
    for pattern, api in REGISTRY_APIS:
        match = pattern.match(url)
        if match:
            status, _, _ = get(api(match))
            return None if status == 200 else f"{url}: package registry answered HTTP {status}"
    status, _, _ = get(url)
    return None if status == 200 else f"{url}: HTTP {status}"


def probe_entry(entry: dict, get=bounded_get, post=http_post_json, fetch=fetch, stream=http_get_stream) -> list[str]:
    problems = []
    body, why = fetch(entry["docs"]["fetch"])
    if body is None:
        problems.append(f"documentation {entry['docs']['fetch']}: {why}")
    status, _, _ = get(entry["docs"]["cite"])
    if status != 200:
        problems.append(f"documentation page {entry['docs']['cite']}: HTTP {status}")
    kind, problem = entry["kind"], None
    if kind == "mcp-server" and entry.get("hosting") == "hosted":
        # A legacy HTTP+SSE server listens for a GET on its /sse URL; only Streamable HTTP takes the POST.
        remote = "streamable-http" in entry.get("transport", [])
        problem = probe_mcp(entry["url"], post) if remote else probe_sse(entry["url"], stream)
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


def safe_probe(entry: dict, probe=probe_entry) -> list[str]:
    """A probe that raises is one more finding, retried and reported like any other failure."""
    try:
        return probe(entry)
    except Exception as error:
        return [f"probe failed: {type(error).__name__}"]


def latest_versions(names: set[str], lookups=LATEST) -> tuple[dict[str, str], list[str]]:
    """Latest release of each component, and the ones that could not be looked up. A lookup
    that fails is reported: comparing a guide against a guess would flag it falsely."""
    latest, problems = {}, []
    for name in sorted(names):
        try:
            latest[name] = lookups[name]()
        except (Exception, SystemExit) as error:    # latest_release and released_docs_dir exit on HTTP errors
            problems.append(f"could not determine the latest {name}: {plain(error)}")
    return latest, problems


def stale_guides(guides: list[catalog.Guide], latest: dict[str, str]) -> list[str]:
    return [f"{g.path}: verified against {name} {version}; the latest is {latest[name]}"
            for g in guides for name, version in g.versions.items()
            if name in latest and latest[name].lstrip("v") != version.lstrip("v")]


def main(argv: list[str]) -> int:
    entries = catalog.load_json(catalog.ROOT / "catalog.json")["capabilities"]
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(safe_probe, entries))
        # One retry for anything that failed, so a single slow response is not a weekly issue.
        retry = [i for i, problems in enumerate(results) if problems]
        for i, problems in zip(retry, pool.map(safe_probe, [entries[i] for i in retry])):
            results[i] = problems
    guides, _ = catalog.local_guides()
    latest, lookup_problems = latest_versions({name for g in guides for name in g.versions if name in LATEST})
    stale = stale_guides(guides, latest) + lookup_problems

    failing = [(e, p) for e, p in zip(entries, results) if p]
    lines = ["# Weekly check", "", "## Capabilities that did not answer", ""]
    lines += [f"- **{e['name']}** (`{e['id']}`): " + "; ".join(p) for e, p in failing] or ["None."]
    lines += ["", "## Guides to re-verify", ""]
    lines += [f"- {s}" for s in stale] or ["None."]
    counted = (f"{len(entries)} capabilit{'y' if len(entries) == 1 else 'ies'} and "
               f"{len(guides)} guide{'' if len(guides) == 1 else 's'}")
    lines += ["", f"Checked {counted}. Nothing is edited automatically: fix catalog.json, or re-verify the guide "
              "and update its verification line."]
    report = "\n".join(lines) + "\n"
    print(report)
    if "--report" in argv:
        Path(argv[argv.index("--report") + 1]).write_text(report, encoding="utf-8")
    return FINDINGS if failing or stale else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
