# casper-llms

[![validate](https://github.com/msanlisavas/casper-llms/actions/workflows/validate.yml/badge.svg)](https://github.com/msanlisavas/casper-llms/actions/workflows/validate.yml)
[![regenerate](https://github.com/msanlisavas/casper-llms/actions/workflows/regenerate.yml/badge.svg)](https://github.com/msanlisavas/casper-llms/actions/workflows/regenerate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

[llms.txt](https://llmstxt.org) indexes for Casper Network documentation that has no usable
llms.txt of its own, so LLM tools can read it.

`docs.casper.network` publishes no llms.txt: it answers every unknown path, `/llms.txt`
included, with its HTML homepage. Most Casper repositories keep their documentation as markdown
on GitHub with no index at all. Each file here lists that markdown as raw links an ingester can
fetch, grouped into sections.

| Index | Pages | Covers |
|---|---|---|
| [`casper-docs/llms.txt`](casper-docs/llms.txt) | 221 | docs.casper.network (Casper 2.0), the Condor release notes, the FAQ, and the parts of the 2024 Casper 2.0 knowledge base with no newer copy |
| [`casper-ceps/llms.txt`](casper-ceps/llms.txt) | 45 | Casper Enhancement Proposals, including CEP-18, CEP-78, CEP-2612 and CEP-3009 |
| [`casper-standards/llms.txt`](casper-standards/llms.txt) | 28 | CEP-18, CEP-78 and CEP-85 reference implementations, the CEP-95 NFT client, and EIP-712 typed data on Casper |
| [`casper-node-tools/llms.txt`](casper-node-tools/llms.txt) | 29 | casper-client v5.0.1, casper-node at its latest release with its changelogs and release notes since 2.0, casper-node-launcher, casper-sidecar, and the 2.0.0 upgrade notes |
| [`casper-sdks/llms.txt`](casper-sdks/llms.txt) | 183 | The JavaScript/TypeScript SDK page by page, plus the .NET, Go, Rust/WebAssembly, Java and Casper Wallet SDKs |
| [`odra/llms.txt`](odra/llms.txt) | 53 | The Odra smart-contract framework, released version (odra.dev's own llms.txt links only HTML, and two of its links 404) |
| [`casper-x402/llms.txt`](casper-x402/llms.txt) | 21 | The x402 specification and transports, its Casper scheme, the hosted CSPR.cloud facilitator API, and the Casper facilitator implementation |
| [`casper-agent-tools/llms.txt`](casper-agent-tools/llms.txt) | 29 | The CSPR.cloud, CSPR.click and CSPR.trade agent skills, the hosted CSPR.cloud and CSPR.trade MCP servers, Odra's Claude Code plugin (6 skills and 11 references), and casper-mcp |

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
its homepage. The site also still renders an older duplicate of the Condor release notes under
`/pages/condor`; the indexes cite the current copies under `/condor`, which are the ones fetched.

## Release notes

casper-node's docs stop at 2.0 and its main changelog at 2.1.2, so the GitHub release notes are
the only published account of the 2.1 and 2.2 protocol changes. A GitHub release page is HTML an
ingester cannot read, so the generator mirrors each release's notes into
[`casper-node-tools/releases/`](casper-node-tools/releases) as markdown, cited at the release
page. Even a one-line note is kept: v2.2.2's is just "Security Release", which still answers
what that release was.

## What is deliberately left out

An LLM repeats what it is given, so these indexes leave out documentation that would make it
wrong, even when the page is real and published:

- **Unreleased text.** Versioned sites are indexed at the version they serve, and repositories at
  their latest release where their development branch runs ahead of it.
- **Client docs for versions npm does not ship.** The CEP-18, CEP-78 and CEP-85 `client-js`
  docs describe versions that are not published, and two of their install lines name packages
  nobody has published - names anyone could claim. They are checked against the npm registry on
  every run and come back automatically once the documented version is published.
- **Code that no longer compiles.** The .NET SDK tutorials still use 2.x APIs that 3.x removed.
- **Superseded drafts,** such as pre-release Condor articles and a permits proposal whose API
  changed before it shipped, and one 2024 article that presents AddressableEntity as Casper 2.0's
  account model although mainnet disables it.

## Freshness

The indexes link branches, not commits, so edits to an existing page reach anything that
re-reads it. On a versioned Docusaurus site (docs.casper.network, odra.dev) the generator reads
the site's own `versions.json` and `lastVersion` and indexes the version the site serves by
default. The plain `docs/` folder is the unreleased "next" version, and indexing it would put
unreleased text under the released page's link. New and removed pages need the indexes regenerated: a
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

Then check the result offline with `python scripts/validate.py`, the same check every pull
request must pass.

## Contributing

Suggestions for new sources and reports of broken or stale links are welcome; see
[CONTRIBUTING.md](CONTRIBUTING.md). The indexes are generated, so changes go through the
generator rather than hand edits. Security problems, including a link that leads somewhere
malicious, go through the [security policy](SECURITY.md).

## License

The generator and the indexes are [MIT](LICENSE). The indexes contain only page titles and
URLs; the documentation they point at belongs to its publishers and stays under their licenses.
