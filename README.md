# casper-llms

[llms.txt](https://llmstxt.org) indexes for Casper Network documentation that has no usable
llms.txt of its own, so LLM tools can read it.

`docs.casper.network` publishes no llms.txt: it answers every unknown path, `/llms.txt`
included, with its HTML homepage. Most Casper repositories keep their documentation as markdown
on GitHub with no index at all. Each file here lists that markdown as raw links an ingester can
fetch, grouped into sections.

| Index | Pages | Covers |
|---|---|---|
| [`casper-docs/llms.txt`](casper-docs/llms.txt) | 231 | docs.casper.network (Casper 2.0), the Condor release notes, the FAQ, and the 2024 Casper 2.0 knowledge base |
| [`casper-ceps/llms.txt`](casper-ceps/llms.txt) | 45 | Casper Enhancement Proposals, including CEP-18, CEP-78, CEP-2612 and CEP-3009 |
| [`casper-standards/llms.txt`](casper-standards/llms.txt) | 30 | CEP-18, CEP-78 and CEP-85 reference implementations, and EIP-712 typed data on Casper |
| [`casper-node-tools/llms.txt`](casper-node-tools/llms.txt) | 14 | casper-client v5.0.1, casper-sidecar, node changelogs and the 2.0.0 upgrade notes |
| [`casper-sdks/llms.txt`](casper-sdks/llms.txt) | 175 | The JavaScript/TypeScript SDK page by page, plus the .NET, Go, Rust/WebAssembly and Casper Wallet SDKs |
| [`odra/llms.txt`](odra/llms.txt) | 53 | The Odra smart-contract framework (odra.dev's own llms.txt links only HTML) |
| [`casper-x402/llms.txt`](casper-x402/llms.txt) | 16 | The x402 specification, its Casper scheme, and the Casper facilitator |
| [`casper-agent-tools/llms.txt`](casper-agent-tools/llms.txt) | 7 | The CSPR.cloud, CSPR.click and CSPR.trade agent skills, and casper-mcp |

Point a tool at the raw file, e.g.
`https://raw.githubusercontent.com/msanlisavas/casper-llms/main/casper-docs/llms.txt`.

## Where a page is fetched vs. where it is cited

Every link fetches raw markdown. The URL after the colon is where the page is published:

```
- [Accounts and Keys](https://raw.githubusercontent.com/casper-network/docs-redux/main/versioned_docs/version-2.0.0/concepts/accounts-and-keys.md): https://docs.casper.network/concepts/accounts-and-keys
```

A tool that shows sources should send people to the second URL. Where no published page exists,
the second URL is the file on GitHub.

A published URL is written only when it has been verified: against the site's sitemap for
docs.casper.network and odra.dev, and by requesting it for the JavaScript SDK site. A plain
HTTP 200 is never trusted, because docs.casper.network answers every unknown path with 200 and
its homepage. Two Condor release notes (`devnet-info`, `migration-guide`) exist in the source
repository but are not published on the site, so they cite GitHub.

## Freshness

The indexes link branches, not commits, so edits to an existing page reach anything that
re-reads it. New and removed pages need the indexes regenerated: a
[weekly workflow](.github/workflows/regenerate.yml) does that and commits any change. Each
index names the upstream commits it was generated from.

The official documentation itself is frozen at Casper 2.0 (last content change September
2025) while the network runs 2.2.x, and some standard-implementation tutorials still use
casper-client 1.x `put-deploy` syntax. Those are upstream gaps these indexes cannot fix.

## Regenerating

```
GITHUB_TOKEN=$(gh auth token) python scripts/generate.py
```

Python 3.10+ and nothing else. Every link is fetched during the run: pages that 404, come back
as HTML, or are stubs under 300 bytes are left out and reported. The set of repositories and
paths for each index lives in `build_indexes()` in [`scripts/generate.py`](scripts/generate.py).
