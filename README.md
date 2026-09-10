# casper-llms

[![validate](https://github.com/msanlisavas/casper-llms/actions/workflows/validate.yml/badge.svg)](https://github.com/msanlisavas/casper-llms/actions/workflows/validate.yml)
[![regenerate](https://github.com/msanlisavas/casper-llms/actions/workflows/regenerate.yml/badge.svg)](https://github.com/msanlisavas/casper-llms/actions/workflows/regenerate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

The home for AI capabilities on the Casper Network:

- [llms.txt](https://llmstxt.org) indexes of Casper documentation, in a form LLM tools can read;
- guides to what has changed since the official docs were written;
- a checked directory of the MCP servers, agent skills, APIs and SDKs built for agents, from
  across the ecosystem;
- a Claude Code plugin marketplace.

**Point an agent at one URL:**

```
https://raw.githubusercontent.com/msanlisavas/casper-llms/main/llms.txt
```

That index links everything below. Each link fetches markdown or plain text, and the URL after
the colon is where a person reads it.

## Directory

Every capability with its endpoint, authentication, pricing and networks is in
[directory.md](directory.md), generated from [catalog.json](catalog.json). A
[weekly check](.github/workflows/check.yml) confirms that each one still answers, and keeps one
[tracking issue](https://github.com/msanlisavas/casper-llms/issues?q=is%3Aissue+label%3Aweekly-check)
open while any does not. Listing is not an endorsement or a security audit: many entries are
early projects that run only on testnet, and some carry a caution worth reading first. To list
yours, see [CONTRIBUTING.md](CONTRIBUTING.md#listing-an-ai-capability).

<!-- catalog:start -->
| Capability | Kind | Publisher | Access |
|---|---|---|---|
| [AstralBeam docs llms.txt](directory.md#astralbeam-docs-llmstxt) | llms.txt | MAKE Software | Free |
| [Casper JS SDK llms.txt](directory.md#casper-js-sdk-llmstxt) | llms.txt | Casper Ecosystem | Free |
| [CSPR.click docs llms.txt](directory.md#csprclick-docs-llmstxt) | llms.txt | MAKE Software | Free |
| [CSPR.cloud docs llms.txt](directory.md#csprcloud-docs-llmstxt) | llms.txt | MAKE Software | Free |
| [CSPR.market docs llms.txt](directory.md#csprmarket-docs-llmstxt) | llms.txt | MAKE Software | Free |
| [Odra framework llms.txt](directory.md#odra-framework-llmstxt) | llms.txt | Odra.dev | Free |
| [AgentGate](directory.md#agentgate) | MCP server | mdlog | no key; free |
| [AgentPay (Casper x402 charge checker)](directory.md#agentpay-casper-x402-charge-checker) | MCP server | Timidan | no key, API key, x402 per call; free and paid |
| [Casper MCP Python Server](directory.md#casper-mcp-python-server) | MCP server | Jiu-hong | no key; free |
| [Casper Network MCP Server (Tairon.ai)](directory.md#casper-network-mcp-server-taironai) | MCP server | Tairon.ai | API key; free and paid |
| [casper-mcp](directory.md#casper-mcp) | MCP server | msanlisavas | API key; free and paid |
| [casper-mcp-py](directory.md#casper-mcp-py) | MCP server | Tmalone1250 | API key; free and paid |
| [casper-rust-wasm-sdk MCP server](directory.md#casper-rust-wasm-sdk-mcp-server) | MCP server | Interchouette - ITC | no key; free |
| [CasperAI MCP server](directory.md#casperai-mcp-server) | MCP server | msanlisavas | no key, API key, x402 per call; free and paid |
| [CasperFlow MCP server](directory.md#casperflow-mcp-server) | MCP server | emmgr23 | API key; free and paid |
| [ceps-rust-ts-client MCP server](directory.md#ceps-rust-ts-client-mcp-server) | MCP server | Interchouette ITC | no key; free |
| [CSPR.AI MCP server](directory.md#csprai-mcp-server) | MCP server | Blockchain-Oracle | no key, API key; free |
| [CSPR.cloud MCP server](directory.md#csprcloud-mcp-server) | MCP server | MAKE Software | API key; free and paid |
| [CSPR.trade MCP server](directory.md#csprtrade-mcp-server) | MCP server | MAKE Software | no key; free |
| [Mr Mainspring](directory.md#mr-mainspring) | MCP server | Micoh18 | no key; free |
| [Sluice](directory.md#sluice) | MCP server | Unity Nodes | no key; free and paid |
| [Casper testnet deploy skill (casper-js-sdk)](directory.md#casper-testnet-deploy-skill-casper-js-sdk) | Agent skill | TerexitariusStomp | Free |
| [CSPR.click SDK integration skill](directory.md#csprclick-sdk-integration-skill) | Agent skill | MAKE Software | Free and paid |
| [CSPR.cloud AI skill](directory.md#csprcloud-ai-skill) | Agent skill | MAKE Software | Free and paid |
| [CSPR.trade DEX assistant skill](directory.md#csprtrade-dex-assistant-skill) | Agent skill | MAKE Software | Free |
| [Fund402 agent skills](directory.md#fund402-agent-skills) | Agent skill | nickthelegend | Free and paid |
| [Odra Casper testnet deploy skill](directory.md#odra-casper-testnet-deploy-skill) | Agent skill | t9fiction | Free |
| [Casper plugin for ElizaOS](directory.md#casper-plugin-for-elizaos) | Plugin | xinminsu | Free |
| [Casper plugin for Hermes Agent](directory.md#casper-plugin-for-hermes-agent) | Plugin | xinminsu | Free |
| [Casper plugin for OpenClaw](directory.md#casper-plugin-for-openclaw) | Plugin | xinminsu | Free |
| [Odra Claude Code plugin (odradev-plugins)](directory.md#odra-claude-code-plugin-odradev-plugins) | Plugin | Odra.dev | Free |
| [CasperAI API](directory.md#casperai-api) | API | msanlisavas | API key, x402 per call; paid |
| [CSPR.cloud x402 facilitator](directory.md#csprcloud-x402-facilitator) | API | MAKE Software | API key; free and paid |
| [Magen3 Agent Gateway](directory.md#magen3-agent-gateway) | API | zicjoe | API key; free |
| [Tab402](directory.md#tab402) | API | Eienel | x402 per call; paid |
| [CasCet](directory.md#cascet) | SDK | mericcintosun | Free |
| [Casper x402 (casper-x402)](directory.md#casper-x402-casper-x402) | SDK | MAKE Software | Free |
| [casper-eip-712](directory.md#casper-eip-712) | SDK | Casper Ecosystem | Free |
| [casper-trust](directory.md#casper-trust) | SDK | Bekirerdem | Free |
| [casper-webrtc-stream x402 SDK](directory.md#casper-webrtc-stream-x402-sdk) | SDK | nickthelegend | Free |
| [castAI](directory.md#castai) | SDK | fozagtx | Free |
| [CSPR.Cloud.Net](directory.md#csprcloudnet) | SDK | msanlisavas | Free and paid |
| [Fund402 SDK](directory.md#fund402-sdk) | SDK | nickthelegend | Free and paid |
| [r402-casper (Rust)](directory.md#r402-casper-rust) | SDK | qntx | Free |
| [x402-casper](directory.md#x402-casper) | SDK | rajkaria | Free |
| [x402.Client.Casper](directory.md#x402clientcasper) | SDK | Michiel Post | Free |
<!-- catalog:end -->

## Guides

The official documentation describes Casper 2.0; mainnet has moved on. These guides cover
what the documentation does not. Every factual sentence links a pinned source, such as a
release tag or a commit, and each claim was re-derived from its source by an independent
verifier before publication. Each guide names the releases it was verified against, and the
weekly check flags it when a newer one ships.

<!-- guides:start -->
- [Where the Casper 2.0 docs differ from mainnet today](guides/casper-2.0-docs-vs-mainnet.md). Verified against casper-node v2.2.2 and docs.casper.network 2.0.0 on 2026-09-10.
- [What changed in Casper 2.1 and 2.2](guides/casper-2.1-and-2.2.md). Verified against casper-node v2.2.2 on 2026-09-10.
- [casper-client 5.x: sending transactions on Casper 2.x](guides/casper-client-5.md). Verified against casper-client-rs v5.0.1 on 2026-09-10.
<!-- guides:end -->

## Plugins and the casper skill

```
/plugin marketplace add msanlisavas/casper-llms
/plugin install casper@casper-llms
```

| Plugin | What it adds | Needs |
|---|---|---|
| `casper` | The casper skill: where current Casper documentation lives, what changed since 2.0, casper-client 5.x commands, and which tool answers what | Nothing |
| `cspr-trade` | The public CSPR.trade MCP server (MAKE): DEX market data, quotes and non-custodial swap building | Nothing |
| `cspr-cloud` | The hosted CSPR.cloud MCP servers (MAKE) for mainnet and testnet | `CSPR_CLOUD_API_KEY` |
| `casperai` | CasperAI's MCP server: cited answers (paid per call) and casper-client command building (free) | `CASPERAI_API_KEY` |
| `odra-plugin` | Odra's own plugin for writing, testing and deploying Odra contracts, installed from its repository | Nothing |

Keys are read from your environment and never stored in this repository: each server may read
only its own key variable, and `validate.py` refuses anything else. Odra's plugin is installed from
its own repository at a pinned commit, moved only after its changes are reviewed; because its
version number decides updates, existing installs pick up a new pin only when Odra bumps it.
The skill in
[`plugins/casper/skills/casper`](plugins/casper/skills/casper/SKILL.md) uses the open
[Agent Skills](https://agentskills.io) format, so any agent that reads `SKILL.md` can use it.

## Documentation indexes

`docs.casper.network` publishes no llms.txt: it answers every unknown path, `/llms.txt`
included, with its HTML homepage. Most Casper repositories keep their documentation as markdown
on GitHub with no index at all. Each index here lists that markdown as raw links an ingester can
fetch, grouped into sections.

<!-- indexes:start -->
| Index | Pages | Covers |
|---|---|---|
| [`casper-docs/llms.txt`](casper-docs/llms.txt) | 221 | The official Casper Network documentation (docs.casper.network), indexed from its source repository casper-network/docs-redux |
| [`casper-guides/llms.txt`](casper-guides/llms.txt) | 3 | Guides written for this repository on what the official Casper documentation does not cover yet |
| [`casper-node-tools/llms.txt`](casper-node-tools/llms.txt) | 29 | Operator and integrator references for the Casper node software |
| [`casper-sdks/llms.txt`](casper-sdks/llms.txt) | 183 | Developer documentation for the Casper SDKs |
| [`casper-standards/llms.txt`](casper-standards/llms.txt) | 28 | Reference implementations and guides for Casper's token standards from the casper-ecosystem organization |
| [`casper-ceps/llms.txt`](casper-ceps/llms.txt) | 45 | The Casper Enhancement Proposals from casper-network/ceps |
| [`odra/llms.txt`](odra/llms.txt) | 53 | Documentation for Odra, the Rust framework for writing, testing and deploying Casper smart contracts |
| [`casper-x402/llms.txt`](casper-x402/llms.txt) | 21 | The x402 pay-per-request protocol on Casper |
| [`casper-agent-tools/llms.txt`](casper-agent-tools/llms.txt) | 30 | Agent skills, MCP servers and plugins for Casper |
<!-- indexes:end -->

Point a tool at any raw file, e.g.
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

The directory follows the same rule: it does not list a tool that asks users to send a secret
key or seed phrase to a remote service.

## Freshness

The indexes link branches, not commits, so edits to an existing page reach anything that
re-reads it. On a versioned Docusaurus site (docs.casper.network, odra.dev) the generator reads
the site's own `versions.json` and `lastVersion` and indexes the version the site serves by
default. The plain `docs/` folder is the unreleased "next" version, and indexing it would put
unreleased text under the released page's link. New and removed pages need the indexes
regenerated: a [weekly workflow](.github/workflows/regenerate.yml) does that and commits any
change. Each index names the upstream commits it was generated from.

The official documentation itself is frozen at Casper 2.0 (last content change September
2025) while the network runs 2.2.x, and some standard-implementation tutorials still use
casper-client 1.x `put-deploy` syntax. The guides above exist for exactly that gap.

## Regenerating

```
GITHUB_TOKEN=$(gh auth token) python scripts/generate.py     # everything: crawl, then render
python scripts/generate.py --catalog-only                     # catalog.json or guides/ changed: render only, offline
python scripts/validate.py                                    # the check every pull request must pass
python -m unittest discover -s scripts/tests                  # the scripts' own tests
```

Python 3.10+ and nothing else. Every link is fetched during the crawl: pages that 404, come back
as HTML, or are stubs under 300 bytes are left out and reported. The set of repositories and
paths for each index lives in `build_indexes()` in [`scripts/generate.py`](scripts/generate.py);
the root `llms.txt`, `directory.md`, the guides index and the tables in this README are rendered
by [`scripts/catalog.py`](scripts/catalog.py).

## Contributing

Listing a capability, suggesting a documentation source, and reporting broken or stale links are
all welcome; see [CONTRIBUTING.md](CONTRIBUTING.md). The indexes and the directory are
generated, so changes go through `catalog.json` or the generator rather than hand edits.
Security problems, including a link or a listed tool that leads somewhere malicious, go through
the [security policy](SECURITY.md).

## License

The generator, the catalog, the guides and the plugins are [MIT](LICENSE). The indexes contain
only page titles and URLs; the documentation they point at, and the products the directory
describes, belong to their publishers and stay under their own licenses.
