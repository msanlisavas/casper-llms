#!/usr/bin/env python3
"""Generate llms.txt indexes for Casper documentation that has no usable llms.txt of its own.

Why this exists: docs.casper.network publishes no llms.txt (it serves its HTML homepage for
every unknown path, /llms.txt included), and most Casper repos keep their docs as markdown
files on GitHub with no index at all. These indexes point at the raw markdown - the only form
an LLM ingester can read - and carry the rendered page as the citation URL after each link:

    - [Accounts](https://raw.githubusercontent.com/.../accounts.md): https://docs.casper.network/concepts/accounts

Every link is fetched while generating, so an index never lists a page that 404s or comes
back as HTML. Public URLs are checked against the site's sitemap where one exists.

Usage:
    GITHUB_TOKEN=$(gh auth token) python scripts/generate.py

Without GITHUB_TOKEN the GitHub API allows 60 requests/hour, which is enough for one run.
"""
from __future__ import annotations

import concurrent.futures
import json
import os
import re
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parent.parent
UA = "casper-llms-generator (+https://github.com/msanlisavas/casper-llms)"
MIN_BYTES = 300  # below this a page is a stub: a title and a link, nothing to answer from


# ----------------------------------------------------------------------------- http

def http_get(url: str, *, api: bool = False) -> tuple[int, str, str]:
    status, content_type, body, _ = http_get_final(url, api=api)
    return status, content_type, body


def http_get_final(url: str, *, api: bool = False) -> tuple[int, str, str, str]:
    """Like http_get, plus the URL the response finally came from after redirects."""
    headers = {"User-Agent": UA}
    token = os.environ.get("GITHUB_TOKEN")
    if api and token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            body = response.read().decode("utf-8", errors="replace")
            return response.status, response.headers.get("Content-Type", ""), body, response.geturl()
    except urllib.error.HTTPError as error:
        return error.code, error.headers.get("Content-Type", "") if error.headers else "", "", url
    except (urllib.error.URLError, TimeoutError) as error:
        return 0, "", str(error), url


def page_title(html: str) -> str:
    match = re.search(r"<title[^>]*>([^<]*)</title>", html, re.I)
    return re.sub(r"\s*\|[^|]*$", "", match.group(1)).strip() if match else ""


def gh_tree(repo: str, ref: str) -> tuple[str, list[str]]:
    status, _, body = http_get(f"https://api.github.com/repos/{repo}/git/trees/{ref}?recursive=1", api=True)
    if status != 200:
        sys.exit(f"GitHub tree for {repo}@{ref} failed with HTTP {status}")
    data = json.loads(body)
    if data.get("truncated"):
        sys.exit(f"GitHub tree for {repo}@{ref} is truncated; this generator would silently miss files")
    return data["sha"], [e["path"] for e in data["tree"] if e["type"] == "blob"]


def raw_url(repo: str, ref: str, path: str) -> str:
    # Quoted: the llms.txt link grammar forbids whitespace and ')' inside a URL.
    return f"https://raw.githubusercontent.com/{repo}/{ref}/{urllib.parse.quote(path, safe='/')}"


def blob_url(repo: str, ref: str, path: str) -> str:
    return f"https://github.com/{repo}/blob/{ref}/{urllib.parse.quote(path, safe='/')}"


# ----------------------------------------------------------------------------- markdown

FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)


def frontmatter(text: str) -> dict[str, str]:
    match = FRONTMATTER.match(text)
    if not match:
        return {}
    fields = {}
    for line in match.group(1).splitlines():
        key, sep, value = line.partition(":")
        if sep and not line.startswith((" ", "\t")):
            fields[key.strip()] = value.strip().strip("'\"")
    return fields


def title_of(text: str, path: str, fm: dict[str, str]) -> str:
    title = fm.get("title")
    if not title:
        body = FRONTMATTER.sub("", text, count=1)
        heading = re.search(r"^#\s+(.+?)\s*#*\s*$", body, re.M)
        title = heading.group(1) if heading else None
    if not title:
        stem = path.rsplit("/", 1)[-1].rsplit(".", 1)[0]
        title = re.sub(r"[-_]+", " ", stem).strip().capitalize()
    # The link grammar is  - [title](url)  with no ']' allowed in the title.
    title = re.sub(r"`", "", title).replace("[", "(").replace("]", ")")
    return re.sub(r"\s+", " ", title).strip() or path


# ----------------------------------------------------------------------------- canonical URLs

Canonical = Callable[[str, dict[str, str]], "str | None"]


def load_sitemap(url: str) -> set[str]:
    status, _, body = http_get(url)
    if status != 200:
        sys.exit(f"sitemap {url} failed with HTTP {status}")
    # docs.casper.network's sitemap lists http:// URLs; the site itself is served over https.
    return {re.sub(r"^http://", "https://", loc).rstrip("/")
            for loc in re.findall(r"<loc>([^<]+)</loc>", body)}


def strip_number_prefix(segment: str) -> str:
    return re.sub(r"^\d+[-_.](?=\D)", "", segment)


def docusaurus(site: str, sitemap: set[str], route_base: str, strip: str,
               allowed: Callable[[str], bool]) -> Canonical:
    """Docusaurus routing, verified against the sitemap - never a bare HTTP 200, because
    docs.casper.network answers every unknown path with 200 and its homepage. In order: the
    computed route if the sitemap lists it; a UNIQUE sitemap URL ending in the same segment;
    for a small section, the sitemap URL whose rendered <title> matches the page's own title
    (the Condor notes are published under names their slugs do not predict); otherwise None,
    and the caller cites the file on GitHub. Never guesses."""
    by_last: dict[str, list[str]] = {}
    for url in sitemap:
        if allowed(url):
            by_last.setdefault(url.rsplit("/", 1)[-1], []).append(url)
    in_scope = sorted(u for urls in by_last.values() for u in urls)
    by_title: dict[str, str] | None = None
    lock = threading.Lock()   # resolve() runs on 16 threads; build the title map once

    def titles() -> dict[str, str]:
        nonlocal by_title
        with lock:
            if by_title is None:
                built: dict[str, str] = {}
                if len(in_scope) <= 60:   # only for small sections: this fetches every page in scope
                    for url in in_scope:
                        built.setdefault(page_title(http_get(url)[2]).casefold(), url)
                by_title = built
        return by_title

    def resolve(path: str, fm: dict[str, str], title: str = "") -> str | None:
        rel = path[len(strip):] if path.startswith(strip) else path
        parts = [strip_number_prefix(p) for p in rel.rsplit(".", 1)[0].split("/")]
        if fm.get("id"):
            parts[-1] = fm["id"]
        if parts[-1] in ("index", "README") or (len(parts) > 1 and parts[-1] == parts[-2]):
            parts = parts[:-1]
        slug = fm.get("slug")
        if slug:
            parts = [p for p in slug.split("/") if p] if slug.startswith("/") else parts[:-1] + [slug]
        candidate = "/".join([site.rstrip("/"), route_base.strip("/"), *parts]).replace("//", "/").replace(":/", "://").rstrip("/")
        if candidate in sitemap:
            return candidate
        matches = by_last.get(candidate.rsplit("/", 1)[-1], [])
        if len(matches) == 1:
            return matches[0]
        return titles().get(title.casefold()) if title else None

    return resolve


def vocs(site: str, pages_root: str) -> Canonical:
    """Vocs (casper-js-sdk) has no sitemap, but GitHub Pages returns a real 404 for unknown
    paths, so each computed URL is requested. The address kept is the one it redirects to,
    so a citation does not bounce through a 301."""
    def resolve(path: str, fm: dict[str, str], title: str = "") -> str | None:
        route = path[len(pages_root):].rsplit(".", 1)[0]
        route = re.sub(r"(^|/)index$", "", route)
        status, _, _, final = http_get_final(f"{site.rstrip('/')}/{route}".rstrip("/"))
        return final if status == 200 else None
    return resolve


# ----------------------------------------------------------------------------- index model

@dataclass
class Collection:
    repo: str
    ref: str
    include: str                 # regex over repo paths
    section: str | Callable[[str], str]
    canonical: Canonical | None = None   # None -> the file on GitHub
    exclude: str | None = None

    def matches(self, path: str) -> bool:
        return bool(re.search(self.include, path)) and not (self.exclude and re.search(self.exclude, path))


@dataclass
class Page:
    """A page that is not in a GitHub repo (e.g. an agent skill served from a product site)."""
    section: str
    fetch: str
    cite: str


@dataclass
class Index:
    file: str
    title: str
    summary: str
    collections: list[Collection] = field(default_factory=list)
    pages: list[Page] = field(default_factory=list)


def by_first_dir(strip: str, names: dict[str, str]) -> Callable[[str], str]:
    def section(path: str) -> str:
        first = path[len(strip):].split("/", 1)[0]
        return names.get(first, first.replace("-", " ").capitalize())
    return section


# ----------------------------------------------------------------------------- the indexes

def build_indexes() -> list[Index]:
    casper_sitemap = load_sitemap("https://docs.casper.network/sitemap.xml")
    odra_sitemap = load_sitemap("https://odra.dev/sitemap.xml")

    def is_v2_doc(url: str) -> bool:
        return not re.search(r"/(next|1\.5\.X|pages|blog|faq)(/|$)", url)

    v2 = "versioned_docs/version-2.0.0/"
    docs_redux = "casper-network/docs-redux"

    return [
        Index(
            file="casper-docs/llms.txt",
            title="Casper Network documentation",
            summary=(
                "The official Casper Network documentation (docs.casper.network), indexed from its source "
                "repository casper-network/docs-redux: the site publishes no llms.txt and answers every "
                "unknown path with its HTML homepage. This is the Casper 2.0 (Condor) documentation the "
                "site serves by default; it has not been updated for Casper 2.1 or 2.2."),
            collections=[
                Collection(docs_redux, "main", rf"^{re.escape(v2)}.+\.mdx?$",
                           by_first_dir(v2, {"concepts": "Concepts", "developers": "Developers",
                                             "operators": "Operators", "users": "Users",
                                             "resources": "Resources", "economics": "Economics"}),
                           docusaurus("https://docs.casper.network", casper_sitemap, "/", v2, is_v2_doc)),
                Collection(docs_redux, "main", r"^condor/[^/]+\.md$", "Casper 2.0 (Condor) release notes",
                           docusaurus("https://docs.casper.network", casper_sitemap, "/pages/condor", "condor/",
                                      lambda u: "/pages/condor" in u and "/jsonrpc-comp/" not in u)),
                Collection(docs_redux, "main", r"^faq/faq\.md$", "FAQ",
                           docusaurus("https://docs.casper.network", casper_sitemap, "/faq", "faq/",
                                      lambda u: "/faq/" in u and "/tags" not in u)),
                Collection("casper-network/condor-info", "main", r"^(articles|faqs|release-notes)/.+\.md$",
                           "Casper 2.0 knowledge base (2024)", exclude=r"/jsonrpc-comp/"),
            ]),
        Index(
            file="casper-ceps/llms.txt",
            title="Casper Enhancement Proposals (CEPs)",
            summary=(
                "The Casper Enhancement Proposals from casper-network/ceps: the specifications behind "
                "Casper's token, NFT and protocol standards, including CEP-18, CEP-78, CEP-95, CEP-2612 "
                "(permits) and CEP-3009 (transfer with authorization, used by x402 payments)."),
            collections=[
                Collection("casper-network/ceps", "master", r"^text/\d{4}-.+\.md$", "Proposals",
                           exclude=r"0000-template"),
            ]),
        Index(
            file="casper-standards/llms.txt",
            title="Casper token and NFT standard implementations",
            summary=(
                "Reference implementations and guides for Casper's token standards from the "
                "casper-ecosystem organization: CEP-18 fungible tokens, CEP-78 enhanced NFTs, CEP-85 "
                "multi-token, and the EIP-712 typed-data toolkit used for off-chain signatures and permits. "
                "Some tutorials still use casper-client 1.x put-deploy syntax."),
            collections=[
                Collection("casper-ecosystem/cep18", "dev", r"^(README\.md|docs/.+\.md|client-js/README\.md|contracts/contract/README\.md)$",
                           "CEP-18 fungible tokens"),
                Collection("casper-ecosystem/cep-78-enhanced-nft", "dev", r"^(README\.md|docs/.+\.md|client-js/README\.md|tutorials/.+\.md)$",
                           "CEP-78 enhanced NFTs", exclude=r"CHANGELOG"),
                Collection("casper-ecosystem/cep-85", "dev", r"^(README\.md|TUTORIAL\.md|docs/.+\.md|client-js/README\.md)$",
                           "CEP-85 multi-token", exclude=r"CHANGELOG"),
                Collection("casper-ecosystem/casper-eip-712", "master",
                           r"^(README\.md|docs/proposal-casper-native-permits\.md|examples/[^/]+/README\.md|go/README\.md|js/README\.md)$",
                           "EIP-712 typed data on Casper"),
            ]),
        Index(
            file="casper-node-tools/llms.txt",
            title="Casper node, sidecar and command-line client",
            summary=(
                "Operator and integrator references for the Casper node software: casper-client at v5.0.1 "
                "(the release CasperAI's commands are pinned to), the casper-sidecar JSON-RPC, SSE and REST "
                "server, node and execution-engine changelogs, the binary port protocol, and the Casper "
                "2.0.0 upgrade notes."),
            collections=[
                Collection("casper-ecosystem/casper-client-rs", "v5.0.1", r"^(README|CHANGELOG)\.md$", "casper-client (v5.0.1)"),
                Collection("casper-network/casper-sidecar", "dev",
                           r"^(USAGE\.md|README\.md|CHANGELOG\.md|LEGACY_SSE_EMULATION\.md|rpc_sidecar/README\.md|json_rpc/README\.md)$",
                           "casper-sidecar"),
                Collection("casper-network/casper-node", "dev",
                           r"^(node/CHANGELOG\.md|execution_engine/CHANGELOG\.md|types/CHANGELOG\.md|node/BINARY_PORT_PROTOCOL\.md)$",
                           "casper-node"),
                Collection("casper-network/casper-protocol-release", "casper", r"^(staging_notes\.md|config/CHANGELOG\.md)$",
                           "Casper 2.0.0 upgrade"),
            ]),
        Index(
            file="casper-sdks/llms.txt",
            title="Casper SDKs",
            summary=(
                "Developer documentation for the Casper SDKs: the JavaScript/TypeScript SDK (per page), "
                "the .NET SDK articles and tutorials, the Go SDK, the Rust/WebAssembly SDK, and the "
                "Casper Wallet SDK for connecting dApps to the Casper Wallet extension."),
            collections=[
                Collection("casper-ecosystem/casper-js-sdk", "dev", r"^site/pages/.+\.mdx$", "JavaScript / TypeScript SDK",
                           vocs("https://casper-ecosystem.github.io/casper-js-sdk", "site/pages/")),
                Collection("casper-ecosystem/casper-js-sdk", "dev", r"^resources/migration-guide-v2-v5\.md$",
                           "JavaScript / TypeScript SDK"),
                Collection("make-software/casper-net-sdk", "master", r"^(README\.md|CHANGELOG\.md|Docs/Articles/.+\.md|Tutorials/.+/README\.md)$",
                           ".NET SDK"),
                Collection("make-software/casper-go-sdk", "master", r"^README\.md$", "Go SDK"),
                Collection("casper-ecosystem/casper-rust-wasm-sdk", "dev", r"^docs/README\.md$", "Rust / WebAssembly SDK"),
                Collection("make-software/casper-wallet-sdk", "master", r"^README\.md$", "Casper Wallet SDK"),
            ]),
        Index(
            file="odra/llms.txt",
            title="Odra smart-contract framework",
            summary=(
                "Documentation for Odra, the Rust framework for writing, testing and deploying Casper smart "
                "contracts, indexed from its source (odradev/odradev.github.io): odra.dev's own llms.txt "
                "links only HTML pages."),
            collections=[
                Collection("odradev/odradev.github.io", "master", r"^docusaurus/docs/.+\.mdx?$",
                           by_first_dir("docusaurus/docs/", {"basics": "Basics", "advanced": "Advanced",
                                                               "tutorials": "Tutorials", "backends": "Backends",
                                                               "examples": "Examples", "migrations": "Migrations"}),
                           docusaurus("https://odra.dev", odra_sitemap, "/docs", "docusaurus/docs/",
                                      lambda u: "/docs/" in u and "/blog/" not in u)),
            ]),
        Index(
            file="casper-x402/llms.txt",
            title="x402 payments on Casper",
            summary=(
                "The x402 pay-per-request protocol on Casper: the protocol specification and its Casper "
                "'exact' scheme from x402-foundation/x402, and the Casper facilitator implementation and "
                "guides from make-software/casper-x402."),
            collections=[
                Collection("x402-foundation/x402", "main",
                           r"^specs/(x402-specification-v2\.md|schemes/exact/scheme_exact(_casper)?\.md|transports-v2/(http|mcp)\.md)$",
                           "x402 specification"),
                Collection("make-software/casper-x402", "master", r"(^|/)(README\.md|docs/.+\.md)$",
                           "Casper x402 facilitator", exclude=r"(CLAUDE|CHANGELOG)\.md$"),
            ]),
        Index(
            file="casper-agent-tools/llms.txt",
            title="Casper agent skills and MCP servers",
            summary=(
                "AI-agent tooling for Casper: the CSPR.cloud, CSPR.click and CSPR.trade agent skills from "
                "MAKE, and casper-mcp, an MCP server with 87 tools for querying and building on Casper."),
            pages=[
                Page("Agent skills", "https://cspr.build/cspr-cloud/skill.md", "https://cspr.cloud/skill.md"),
                Page("Agent skills",
                     "https://raw.githubusercontent.com/make-software/csprclick-examples/master/csprclick-skill/SKILL.md",
                     "https://docs.cspr.click/documentation/ai-agent-skills"),
                Page("Agent skills", "https://mcp.cspr.trade/SKILL.md", "https://mcp.cspr.trade/SKILL.md"),
            ],
            collections=[
                Collection("msanlisavas/casper-mcp", "main",
                           r"^(README\.md|CHANGELOG\.md|docs/writes\.md|observability/README\.md)$", "casper-mcp"),
            ]),
    ]


# ----------------------------------------------------------------------------- generation

@dataclass
class Link:
    section: str
    title: str
    fetch: str
    cite: str
    sort_key: str


def fetch_markdown(url: str) -> tuple[str | None, str]:
    status, content_type, body = http_get(url)
    if status != 200:
        return None, f"HTTP {status}"
    if "html" in content_type.lower():
        return None, f"served as {content_type}"
    if len(body.encode("utf-8")) < MIN_BYTES:
        return None, f"stub ({len(body)} bytes)"
    return body, ""


def generate(index: Index, report: list[str]) -> list[Link]:
    jobs: list[tuple[str, str, Callable[[], Link | None]]] = []
    sources: list[str] = []

    for coll in index.collections:
        sha, paths = gh_tree(coll.repo, coll.ref)
        sources.append(f"{coll.repo}@{sha[:7]}")
        for path in sorted(p for p in paths if coll.matches(p)):
            def job(coll=coll, path=path) -> Link | None:
                fetch = raw_url(coll.repo, coll.ref, path)
                body, why = fetch_markdown(fetch)
                if body is None:
                    report.append(f"  skipped {coll.repo}/{path}: {why}")
                    return None
                fm = frontmatter(body)
                title = title_of(body, path, fm)
                cite = coll.canonical(path, fm, title) if coll.canonical else None
                if coll.canonical and cite is None:
                    report.append(f"  no public page found for {coll.repo}/{path}: citing GitHub instead")
                cite = cite or blob_url(coll.repo, coll.ref, path)
                section = coll.section(path) if callable(coll.section) else coll.section
                return Link(section, title, fetch, cite, path)
            jobs.append((coll.repo, path, job))

    for page in index.pages:
        def job(page=page) -> Link | None:
            body, why = fetch_markdown(page.fetch)
            if body is None:
                report.append(f"  skipped {page.fetch}: {why}")
                return None
            return Link(page.section, title_of(body, page.fetch, frontmatter(body)), page.fetch, page.cite, page.fetch)
        jobs.append(("page", page.fetch, job))

    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
        links = [link for link in pool.map(lambda j: j[2](), jobs) if link]

    # Sections keep the order they are first declared in; links sort by path inside a section.
    order: dict[str, int] = {}
    for link in links:
        order.setdefault(link.section, len(order))
    links.sort(key=lambda l: (order[l.section], l.sort_key))

    lines = [f"# {index.title}", "", f"> {index.summary}", "",
             "Each link fetches the page's raw markdown; the URL after the colon is where it is published.",
             f"Generated by https://github.com/msanlisavas/casper-llms from {', '.join(sorted(set(sources)))}.", ""]
    current = None
    for link in links:
        if link.section != current:
            lines += ([""] if current else []) + [f"## {link.section}", ""]
            current = link.section
        lines.append(f"- [{link.title}]({link.fetch}): {link.cite}")
    out = ROOT / index.file
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return links


def main() -> None:
    summary = []
    for index in build_indexes():
        report: list[str] = []
        links = generate(index, report)
        cited_on_site = sum(1 for l in links if "github.com" not in l.cite)
        summary.append(f"{index.file}: {len(links)} pages ({cited_on_site} cited on their published site)")
        print(summary[-1])
        for line in sorted(report):
            print(line)
    print("\n" + "\n".join(summary))


if __name__ == "__main__":
    main()
