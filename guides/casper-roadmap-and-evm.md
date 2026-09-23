# Casper roadmap and EVM status: the Casper Manifest item by item against mainnet

Verified against casper-node v2.2.2 and casper-client-rs v5.0.1 on 2026-09-23.

Casper mainnet runs protocol 2.2.2 and has no upgrade scheduled. On 2026-09-23 at 16:31 UTC, `info_get_status` on `https://node.mainnet.casper.network/rpc` returned `"protocol_version": "2.2.2"`, `"build_version": "2.2.2-d4becff"` and `"next_upgrade": null`, and the testnet node `https://node.testnet.casper.network/rpc` returned the same three values. The same day, the lists of staged protocol versions at `https://genesis.casper.network/casper/protocol_versions` and `https://genesis.casper.network/casper-test/protocol_versions` both ended at `2_2_2`. The chainspec that both networks served through `info_get_chainspec` on 2026-09-23 was byte-for-byte the file at the v2.2.2 tag ([mainnet](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml), [testnet](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/testnet/chainspec.toml)). [v2.2.2](https://github.com/casper-network/casper-node/releases/tag/v2.2.2), published 2026-07-01, was the newest casper-node release and the newest tag ([releases](https://github.com/casper-network/casper-node/releases), [tags](https://github.com/casper-network/casper-node/tags), read 2026-09-23). So a feature that is not in v2.2.2 is not on mainnet or testnet.

This guide takes the roadmap at [casper.network/roadmap](https://www.casper.network/roadmap) and the Casper Manifest at [casper.network/news/manifest](https://www.casper.network/news/manifest), both read on 2026-09-23. For each item it states what mainnet runs, what code or proposal exists, and where a website says something the chain does not. It answers the question "does Casper support Solidity or MetaMask today?" directly (no Solidity or EVM; MetaMask only through a Casper Snap), and it covers the unreleased EVM branch, addressable entities, CEP-97, csprUSD and x402.

The sources are not all equally durable:

- The casper.network pages are server-rendered HTML, read on **2026-09-23**. On that day each page carried the comment "Last Published: Tue Sep 22 2026 16:23:08 GMT+0000", which is the site's publish time, not the article's date. Their sizes and SHA-256 digests are under *Sources*.
- The GitHub branches cited here (`feat-evm` and the sidecar and client `evm` branches) are unreleased development branches that can move at any time. On 2026-09-23 their heads were [72d8c57](https://github.com/casper-network/casper-node/commit/72d8c57cb7b9cfc55d8aaea3f8a3fb553d364af7) (2026-09-18), [ecf43cc](https://github.com/casper-network/casper-sidecar/commit/ecf43cc206b33edc0918709df34891b075a755eb) (2026-09-18) and [dc3dfb1](https://github.com/casper-ecosystem/casper-client-rs/commit/dc3dfb14e022e343435b42e67108a88e52a14865) (2026-08-27). They are cited at those commits.
- Pull requests are cited by their page, with the date they were read.
- Live RPC responses are dated in the text, and the next protocol upgrade will change them.
- The weekly check of this repository follows casper-node and casper-client-rs releases. It does not follow the casper.network pages, the branches, the pull requests, the CEPs repository or the x402 package.

Every target date, "In Progress" label and plan below is what the Casper Association published, on the date given. None of them is a fact about what will ship or when. This guide gives no price, prediction or investment advice.

## Does Casper support Solidity, the EVM or MetaMask today?

**No.** As of 2026-09-23, Casper mainnet cannot run Solidity or EVM bytecode, and an Ethereum wallet or tool cannot use it as an Ethereum-style network.

- **One virtual machine, and it runs Wasm.**
  - The v2.2.2 mainnet chainspec sets `vm_casper_v1 = true` and `vm_casper_v2 = false` ([chainspec L204-L207](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L204-L207)), and it has no `[evm]` section ([chainspec](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml)).
  - The v2.2.2 `Transaction` type has two variants, `Deploy` and `V1` ([transaction.rs L136-L150](https://github.com/casper-network/casper-node/blob/v2.2.2/types/src/transaction.rs#L136-L150)).
  - The EVM variant, `Evm(Box<EvmTransaction>)`, exists only on the unreleased `feat-evm` branch ([transaction.rs L145-L156 at 72d8c57](https://github.com/casper-network/casper-node/blob/72d8c57cb7b9cfc55d8aaea3f8a3fb553d364af7/types/src/transaction.rs#L145-L156)).
- **No Ethereum JSON-RPC.**
  - The newest casper-sidecar release, [v2.1.0](https://github.com/casper-network/casper-sidecar/releases/tag/v2.1.0), defines 25 JSON-RPC methods. None of them is an `eth_`, `net_` or `web3_` method ([rpc_schema.json at v2.1.0](https://github.com/casper-network/casper-sidecar/blob/v2.1.0/resources/test/rpc_schema.json)).
  - On 2026-09-23, both `https://node.mainnet.casper.network/rpc` and `https://node.testnet.casper.network/rpc` answered an `eth_chainId` request with error `-32601`, "'eth_chainId' is not a supported json-rpc method on this server".
- **Contracts are Wasm, written mostly in Rust.**
  - The documentation says "Casper Network's development ecosystem supports WebAssembly by design, rather than requiring proprietary languages like Solidity." ([build-on-casper.md L40](https://github.com/casper-network/docs-redux/blob/c78e3c2040d30fd8c42cb95bc8a3b308db9d1a56/versioned_docs/version-2.0.0/resources/build-on-casper.md?plain=1#L40)).
  - It also says Rust contracts "are compiled to WebAssembly (Wasm)" ([L42](https://github.com/casper-network/docs-redux/blob/c78e3c2040d30fd8c42cb95bc8a3b308db9d1a56/versioned_docs/version-2.0.0/resources/build-on-casper.md?plain=1#L42)).
  - Odra's tutorial "Odra for Solidity developers" helps a developer move from Solidity to Odra, "a high-level framework designed to simplify the development of smart contracts for the Casper Network" ([odra-sol.md L11-L15](https://github.com/odradev/odradev.github.io/blob/5af9dfbac32814c1542744a819210d68b1bc0b7d/docusaurus/versioned_docs/version-2.9/tutorials/odra-sol.md?plain=1#L11-L15)). It is a Rust framework, not a Solidity compiler.
- **MetaMask works only through a Snap that signs Casper deploys and Casper 2.x transactions with a separate Casper key.**
  - The Casper Snap, npm package `casper-manager`, describes itself as "Sign deploys and messages for the Casper Blockchain with your Casper account(s)." ([snap.manifest.json L3](https://github.com/casper-ecosystem/casper-manager/blob/casper-manager@2.0.0/packages/snap/snap.manifest.json#L3)).
  - It derives its keys under BIP-44 coin type 506 ([L29](https://github.com/casper-ecosystem/casper-manager/blob/casper-manager@2.0.0/packages/snap/snap.manifest.json#L29)), so the user signs with a separate Casper key, not with their Ethereum account.
  - Its FAQ lists three features: "Get Account", "Sign a deploy" and "Sign a message" ([FAQ.md L21-L25](https://github.com/casper-ecosystem/casper-manager/blob/casper-manager@2.0.0/FAQ.md?plain=1#L21-L25)).
  - Its newest npm version, 2.0.0, was published on 2025-02-20 (`https://registry.npmjs.org/casper-manager`, read 2026-09-23), and its newest commit is dated 2025-05-18 ([d2df190](https://github.com/casper-ecosystem/casper-manager/commit/d2df19082945f6cae88ee1c5ccd42981cef7a118)).
  - The documentation lists it as "Metamask with Casper Snap" ([build-on-casper.md L24](https://github.com/casper-network/docs-redux/blob/c78e3c2040d30fd8c42cb95bc8a3b308db9d1a56/versioned_docs/version-2.0.0/resources/build-on-casper.md?plain=1#L24)).
  - Its FAQ mentions deploys only, but at the same tag the Snap's `casper_sign` method ([index.tsx L634-L643](https://github.com/casper-ecosystem/casper-manager/blob/casper-manager@2.0.0/packages/snap/src/index.tsx#L634-L643)) accepts either a legacy `deployJson` or a `transaction`, and returns a signed `TransactionV1` for the latter ([index.tsx L444-L523](https://github.com/casper-ecosystem/casper-manager/blob/casper-manager@2.0.0/packages/snap/src/index.tsx#L444-L523)). Its helper library documents `signTransaction` with a native-transfer example ([packages/lib/README.md L72-L90](https://github.com/casper-ecosystem/casper-manager/blob/casper-manager@2.0.0/packages/lib/README.md?plain=1#L72-L90)). This guide did not test it against mainnet.
- **A bridge is not EVM support.**
  - AstralBeam's documentation calls it "a secure, bidirectional bridge between **Casper Network** and **EVM-compatible chains** such as Ethereum, Base, and Polygon". It says "Access the public testnet at: https://testnet.astralbeam.io" and "Mainnet launch is planned following thorough testnet validation and security audits." ([docs.astralbeam.io](https://docs.astralbeam.io/), fetched 2026-09-23).
  - A bridge moves tokens between chains. It does not run Solidity on Casper.
- **What is planned.**
  - The roadmap lists "EVM Compatibility" as "In Progress", "Target: 2026 H2", with "Full compatibility with developer toolchains (Foundry, Hardhat) and retail wallets" ([casper.network/roadmap](https://www.casper.network/roadmap), read 2026-09-23).
  - The Manifest's timeline says "EVM execution engine (protocol-level production target by end of 2026)" ([casper.network/news/manifest](https://www.casper.network/news/manifest), read 2026-09-23).
  - The code is an unreleased prototype (see *EVM compatibility* below).
- **How to state it.** "Not today. On 2026-09-23 Casper mainnet ran protocol 2.2.2, which executes Wasm contracts only. EVM support exists as an unreleased prototype branch, and the Casper Association has published a target of 2026 H2 for it. MetaMask can sign Casper transactions only through the Casper Snap, with a separate Casper key; that is not EVM compatibility." Do not give an EVM launch date.

## The roadmap and the Casper Manifest: what was published, and when

- **The Manifest.**
  - Its page is headed "Casper Network Publishes Multi-Year Technical Roadmap, Targeting Compliant Real-World Assets and Machine Commerce" and does not show a date ([casper.network/news/manifest](https://www.casper.network/news/manifest), read 2026-09-23). The site's [sitemap](https://www.casper.network/sitemap.xml), read 2026-09-23, gives it `lastmod` 2026-05-12.
  - An X Space recap dated May 20, 2026 calls it "the newly announced Casper Manifest". The recap says "Michael Steuer, Casper Association President and CTO" walked the community through the roadmap in that session ([X Space recap](https://www.casper.network/news/casper-x-space-recap-may-20-2026-casper-manifest-rwas-and-the-agentic-buildathon), read 2026-09-23).
  - The Manifest names no author.
- **Nine initiatives.**
  - The Manifest says it "comprises nine protocol initiatives" in four areas, and lists them: "Networking Layer Hardening", "EVM Execution Engine", "Native Token Registry", "Gasless Transactions", "Batch Transactions & Smart Accounts", "Compliant Security Tokens (ERC-3643)", "X402 Micropayments", "Transaction Privacy" and "Quantum Safety" ([Manifest](https://www.casper.network/news/manifest), read 2026-09-23).
  - It promises that "Formal protocol enhancement proposals (CEPs) for each initiative in the Casper Manifest will be published." (same page, read 2026-09-23).
- **The Manifest's timeline**, verbatim, read 2026-09-23 ([Manifest](https://www.casper.network/news/manifest)):
  - "2026 H2. … Networking hardening. EVM execution engine (protocol-level production target by end of 2026). X402 production deployment (PoC complete, production hardening underway). ERC-3643 Phase 1 (identity registry and compliance engine, buildable today with no protocol changes)."
  - "2026 H2 through 2027 H1. … Gasless transaction permits (the cryptographic tooling already exists). Batch transactions and account abstraction. Native Token Registry Phase 1."
  - "2027. … Transaction privacy. Post-quantum signing. Continued maturation of the Native Token Registry, networking layer, and gasless infrastructure."
- **The roadmap page.**
  - [casper.network/roadmap](https://www.casper.network/roadmap) has `lastmod` 2026-08-28 in the [sitemap](https://www.casper.network/sitemap.xml), read 2026-09-23.
  - It says "Nine initiatives targeting one goal" but shows eleven cards: it splits "Batch Transactions" and "Smart Accounts" into two cards and adds "Agent Infrastructure" (page read 2026-09-23).
  - It also lists five capabilities under "The Foundation", which it says "already shipped with Casper". Three of the five do not match the chain, and one matches only in part (see *Where casper.network's "already shipped" list contradicts mainnet*).
- **The two sources give different dates** for three items, both read 2026-09-23 ([roadmap](https://www.casper.network/roadmap), [Manifest](https://www.casper.network/news/manifest)):
  - Batch transactions: roadmap "Target: 2027"; Manifest, the "2026 H2 through 2027 H1" tier.
  - Gasless transactions: roadmap "Target: 2026 H2"; Manifest, gasless permits in the "2026 H2 through 2027 H1" tier.
  - Native Token Registry: roadmap "Target: 2026/2027"; Manifest, "Native Token Registry Phase 1" in the "2026 H2 through 2027 H1" tier.
- **An older page, out of date.** [casper.network/protocol-roadmap](https://www.casper.network/protocol-roadmap) (sitemap `lastmod` 2026-07-11) is headed "Discover Casper's Protocol Roadmap".
  - On 2026-09-23 its roadmap was a slider of seven images with no text in the HTML. The first image is a timeline of "1.5.3", "Peregrine", "Juliet" and "Condor", marked "Now" and "2024" ([slide 1](https://cdn.prod.website-files.com/668fef77d8ac075ed5e3f57a/66919e43893cf77d0cb1405b_Slide%201.webp), read 2026-09-23).
  - Its "Peregrine" slide is marked "Status: live" and lists "Shortened block times to 16 seconds" and "99% refund of unspent gas fees on transactions" ([slide 3](https://cdn.prod.website-files.com/668fef77d8ac075ed5e3f57a/66919e3cf23d82e50e8ef247_Slide%203.png), read 2026-09-23). Mainnet today has an [8000 ms minimum block time](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L32) and a [75/100 refund ratio](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L117).
  - Its "Condor" slides are marked "Status: in development" and list "Account & Contract Unification" ([slide 6](https://cdn.prod.website-files.com/668fef77d8ac075ed5e3f57a/66919e3c61a0eb56613e2350_Slide%206.webp), read 2026-09-23).
  - Do not answer from this page. Use [/roadmap](https://www.casper.network/roadmap) instead.

## Roadmap items and their mainnet status on 2026-09-23

The first two columns quote [casper.network/roadmap](https://www.casper.network/roadmap) as read on 2026-09-23. Every "Nothing found" is a search made on 2026-09-23 of the casper-network/casper-node branches (161) and pull requests (the 38 opened since 2026-05-01), and of the casper-network/ceps pull requests. It is not a statement that no work exists.

| Roadmap card | Status and target (read 2026-09-23) | On mainnet (v2.2.2, 2026-09-23) | Public code or proposal (read 2026-09-23) |
| --- | --- | --- | --- |
| EVM Compatibility | "In Progress", "2026 H2" | No. There is no `[evm]` section, and only the Wasm runtime is enabled ([chainspec L204-L207](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L204-L207)). | The unreleased `feat-evm` branch, 91 commits ahead of `dev` ([compare](https://github.com/casper-network/casper-node/compare/f986c0506957c276c691f8f9dbb440c4ae33e9a1...72d8c57cb7b9cfc55d8aaea3f8a3fb553d364af7)), plus sidecar and client `evm` branches. See *EVM compatibility*. |
| Network Layer Hardening | "In Progress", "2026 H2" | No release after [v2.2.2](https://github.com/casper-network/casper-node/releases/tag/v2.2.2). | Nothing found. |
| Native Token Registry | "Planned", "2026/2027" | No. | Nothing found, and no CEP ([ceps pull requests](https://github.com/casper-network/ceps/pulls?q=is%3Apr)). |
| Gasless Transactions | "In Progress", "2026 H2" | The protocol part is not there. `PricingMode::Prepaid` is "for future use, not currently implemented" ([pricing_mode.rs L69-L74](https://github.com/casper-network/casper-node/blob/v2.2.2/types/src/transaction/pricing_mode.rs#L69-L74)), and mainnet has `allow_prepaid = false` ([chainspec L136-L139](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L136-L139)). | Two contract-level standards, both merged on 2026-05-25: [CEP-2612](https://github.com/casper-network/ceps/blob/3748c9017218378e650d8e5731feaf82088657bd/text/2612-permit-extension.md?plain=1#L1-L9), "off-chain approval of CEP-18 token allowances" ([PR #99](https://github.com/casper-network/ceps/pull/99)), and [CEP-3009](https://github.com/casper-network/ceps/blob/3748c9017218378e650d8e5731feaf82088657bd/text/3009-transfer-with-authorization.md?plain=1#L1-L12), "off-chain authorization of CEP-18 token transfers" ([PR #100](https://github.com/casper-network/ceps/pull/100)). Each works only in a token contract that implements it. Draft [CEP PR #103](https://github.com/casper-network/ceps/pull/103) includes "a domain-separated gas-payer authorization". |
| Batch Transactions | "Planned", "2027" | No. | Nothing found. |
| Smart Accounts | "Planned", "2026/2027" | No. The account model it builds on is switched off ([chainspec L177](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L177)). | Draft [CEP PR #103](https://github.com/casper-network/ceps/pull/103), "CEP: Scoped Actors — Protocol-Native Account Abstraction", opened 2026-07-19, which "Extends the `AddressableEntity` account model". |
| Compliant Security Tokens | "In Progress", "2026 H2" | No protocol component. The Manifest calls Phase 1 "buildable today with no protocol changes" ([Manifest](https://www.casper.network/news/manifest), read 2026-09-23). | No public ERC-3643 implementation found under casper-network, casper-ecosystem, odradev or make-software (GitHub repository search). |
| Transaction Privacy | "Planned", "2027" | No. | Nothing found. |
| Quantum Safety | "Planned", "2027" | No. v2.2.2 public keys are `System`, `Ed25519` or `Secp256k1` ([asymmetric_key.rs L480-L492](https://github.com/casper-network/casper-node/blob/v2.2.2/types/src/crypto/asymmetric_key.rs#L480-L492)). | Nothing found. |
| X402 Micropayments | "In Progress", "2026 H2" | Settlement happens in token contracts, not in the node. A facilitator for `casper:casper` is documented; the token question is open (see *x402 on mainnet*). | [CEP-3009](https://github.com/casper-network/ceps/blob/3748c9017218378e650d8e5731feaf82088657bd/text/3009-transfer-with-authorization.md?plain=1#L31-L36) (merged), [make-software/casper-x402](https://github.com/make-software/casper-x402/blob/3ee705ecfff44795bd502b101991964ce4dc037d/README.md?plain=1#L1-L16), and the x402 Foundation's `@x402/casper` 2.27.0 ([constants.ts L40-L55](https://github.com/x402-foundation/x402/blob/npm-@x402/casper@v2.27.0/typescript/packages/mechanisms/casper/src/constants.ts#L40-L55)). |
| Agent Infrastructure | "Planned", "2026/2027" | No. | The card builds on "X402, Smart Accounts, Gassless operations" (the page's spelling); draft [CEP PR #103](https://github.com/casper-network/ceps/pull/103) says it "Directly supports the Casper Manifest's Smart Accounts, Gasless Transactions (Phase 2), and Agent Infrastructure initiatives". |

- **CEPs published since the Manifest.** On 2026-09-23 the CEPs merged after 2026-05-12 were:
  - CEP-2612 and CEP-3009, both on 2026-05-25 ([PR #99](https://github.com/casper-network/ceps/pull/99), [PR #100](https://github.com/casper-network/ceps/pull/100));
  - CEP-97, on 2026-07-02 ([PR #102](https://github.com/casper-network/ceps/pull/102)).

  The only open Manifest-related proposal was the draft [PR #103](https://github.com/casper-network/ceps/pull/103). None of these is a CEP for the EVM, the Native Token Registry, batch transactions, privacy, quantum safety or networking ([ceps pull requests](https://github.com/casper-network/ceps/pulls?q=is%3Apr), read 2026-09-23).

## EVM compatibility: an unreleased prototype

- **Where the code is.**
  - The EVM work lives on the `feat-evm` branch of casper-network/casper-node. The first commit on it that is not on `dev` is "Add first-pass EVM executor foundation", dated 2026-05-05 ([f8d3324](https://github.com/casper-network/casper-node/commit/f8d3324cd411806c98dd7dc26f413c531e02d5da)).
  - On 2026-09-23 the branch head was [72d8c57](https://github.com/casper-network/casper-node/commit/72d8c57cb7b9cfc55d8aaea3f8a3fb553d364af7), dated 2026-09-18. It was 91 commits ahead of `dev` and 2 behind, with 235 files changed ([compare](https://github.com/casper-network/casper-node/compare/f986c0506957c276c691f8f9dbb440c4ae33e9a1...72d8c57cb7b9cfc55d8aaea3f8a3fb553d364af7)).
  - No release or tag contains it ([releases](https://github.com/casper-network/casper-node/releases), read 2026-09-23).
- **What the branch says about itself.**
  - `EVM.md` at 72d8c57 is titled "EVM Support Prototype" ([EVM.md L1](https://github.com/casper-network/casper-node/blob/72d8c57cb7b9cfc55d8aaea3f8a3fb553d364af7/EVM.md?plain=1#L1)).
  - It says: "The current scope is intentionally narrow. Casper node can accept and execute `Transaction::Evm` transactions, store EVM execution results, and serve read-only EVM calls through binary-port speculative execution consumed by sidecar. Native Ethereum JSON-RPC remains a sidecar concern." ([L7-L10](https://github.com/casper-network/casper-node/blob/72d8c57cb7b9cfc55d8aaea3f8a3fb553d364af7/EVM.md?plain=1#L7-L10)).
  - Its last caveat reads: "EVM support is currently a prototype path and still uses local sidecar patches for unreleased node types." ([L1181-L1182](https://github.com/casper-network/casper-node/blob/72d8c57cb7b9cfc55d8aaea3f8a3fb553d364af7/EVM.md?plain=1#L1181-L1182)).
  - Reproducing its Foundry flow requires patching sidecar to a local node checkout "because these EVM types are unreleased" ([L719-L720](https://github.com/casper-network/casper-node/blob/72d8c57cb7b9cfc55d8aaea3f8a3fb553d364af7/EVM.md?plain=1#L719-L720)).
- **What it implements, per `EVM.md`:**
  - an executor "backed by `revm`" ([L56](https://github.com/casper-network/casper-node/blob/72d8c57cb7b9cfc55d8aaea3f8a3fb553d364af7/EVM.md?plain=1#L56));
  - Prague execution, "delegated to `revm`" ([L108](https://github.com/casper-network/casper-node/blob/72d8c57cb7b9cfc55d8aaea3f8a3fb553d364af7/EVM.md?plain=1#L108));
  - native Casper transfers to 20-byte EVM addresses "when `[evm].enabled = true`" ([L60-L61](https://github.com/casper-network/casper-node/blob/72d8c57cb7b9cfc55d8aaea3f8a3fb553d364af7/EVM.md?plain=1#L60-L61));
  - EIP-7702 set-code transactions ([L62-L63](https://github.com/casper-network/casper-node/blob/72d8c57cb7b9cfc55d8aaea3f8a3fb553d364af7/EVM.md?plain=1#L62-L63)).
- **What it rejects or lacks, per `EVM.md`:**
  - blob transactions (EIP-4844) ([L123](https://github.com/casper-network/casper-node/blob/72d8c57cb7b9cfc55d8aaea3f8a3fb553d364af7/EVM.md?plain=1#L123));
  - non-empty access lists ([L151](https://github.com/casper-network/casper-node/blob/72d8c57cb7b9cfc55d8aaea3f8a3fb553d364af7/EVM.md?plain=1#L151));
  - positive priority fees ([L152](https://github.com/casper-network/casper-node/blob/72d8c57cb7b9cfc55d8aaea3f8a3fb553d364af7/EVM.md?plain=1#L152)).
  - It also requires the signed gas price to "equal the configured EVM base fee" ([L146](https://github.com/casper-network/casper-node/blob/72d8c57cb7b9cfc55d8aaea3f8a3fb553d364af7/EVM.md?plain=1#L146)).
  - It notes that one accepted fee shape matches "the fallback transaction shape emitted by MetaMask for custom networks" ([L490-L496](https://github.com/casper-network/casper-node/blob/72d8c57cb7b9cfc55d8aaea3f8a3fb553d364af7/EVM.md?plain=1#L490-L496)).
  - And: "EVM does not support Casper custom payment or refund-purse selection in this prototype." ([L527-L531](https://github.com/casper-network/casper-node/blob/72d8c57cb7b9cfc55d8aaea3f8a3fb553d364af7/EVM.md?plain=1#L527-L531)).
- **The branch's own chainspec leaves the EVM off.**
  - Its mainnet chainspec adds an `[evm]` section that begins `enabled = false` ([chainspec L512-L513 at 72d8c57](https://github.com/casper-network/casper-node/blob/72d8c57cb7b9cfc55d8aaea3f8a3fb553d364af7/resources/mainnet/chainspec.toml#L512-L513)).
  - It proposes EIP-155 chain ID `1_129_533_441`, from the pattern `0x435350NN` with "mainnet=0x01, testnet=0x02" ([L514-L517](https://github.com/casper-network/casper-node/blob/72d8c57cb7b9cfc55d8aaea3f8a3fb553d364af7/resources/mainnet/chainspec.toml#L514-L517)), and `1_129_533_442` for testnet ([testnet chainspec L518-L519](https://github.com/casper-network/casper-node/blob/72d8c57cb7b9cfc55d8aaea3f8a3fb553d364af7/resources/testnet/chainspec.toml#L518-L519)).
  - It also sets `spec = 'prague'`, `block_gas_limit = 30_000_000` and `base_fee = 5_000` motes per EVM gas, with the comment "A standard 21,000-gas transfer costs 0.105 CSPR" ([L518-L525](https://github.com/casper-network/casper-node/blob/72d8c57cb7b9cfc55d8aaea3f8a3fb553d364af7/resources/mainnet/chainspec.toml#L518-L525)).
  - These are values in an unreleased branch, not network parameters. Casper has no live EVM chain ID. A release may change any of them.
- **Sidecar.**
  - The `evm` branch of casper-network/casper-sidecar was at [ecf43cc](https://github.com/casper-network/casper-sidecar/commit/ecf43cc206b33edc0918709df34891b075a755eb) (2026-09-18) on 2026-09-23, 29 commits ahead of `dev` ([compare](https://github.com/casper-network/casper-sidecar/compare/62c9522eac936c8940a7b723b74c49fb5b0bddae...ecf43cc206b33edc0918709df34891b075a755eb)). Its first commit is "Add Ethereum JSON-RPC support for EVM transactions", dated 2026-05-11 ([b6e5d86](https://github.com/casper-network/casper-sidecar/commit/b6e5d86f74b4b79990336ccf6ca86a8f01686d07)).
  - Its schema lists 35 Ethereum-style methods, among them `web3_clientVersion`, `eth_chainId`, `net_version`, `eth_sendRawTransaction`, `eth_call`, `eth_getLogs` and `eth_getTransactionByHash` ([rpc_schema.json at ecf43cc](https://github.com/casper-network/casper-sidecar/blob/ecf43cc206b33edc0918709df34891b075a755eb/resources/test/rpc_schema.json)).
  - A second branch, `geth-compatible-messages`, has open [PR #474](https://github.com/casper-network/casper-sidecar/pull/474), "geth-compatible error message", into `evm`, opened 2026-09-01.
- **Client.**
  - The `evm` branch of casper-ecosystem/casper-client-rs was at [dc3dfb1](https://github.com/casper-ecosystem/casper-client-rs/commit/dc3dfb14e022e343435b42e67108a88e52a14865) (2026-08-27) on 2026-09-23: 2 commits ahead of `dev` and 45 behind ([compare](https://github.com/casper-ecosystem/casper-client-rs/compare/10329ed947bbf851b612a207729c3d68a784c896...dc3dfb14e022e343435b42e67108a88e52a14865)).
  - Its CHANGELOG lists under "Unreleased": "Native transaction transfers now accept `0x`-prefixed 20-byte EVM addresses via `--target`." ([CHANGELOG.md L12-L15](https://github.com/casper-ecosystem/casper-client-rs/blob/dc3dfb14e022e343435b42e67108a88e52a14865/CHANGELOG.md?plain=1#L12-L15)).
  - Its README gives a `put-transaction transfer` example with a `0x…` target ([README.md L166-L184](https://github.com/casper-ecosystem/casper-client-rs/blob/dc3dfb14e022e343435b42e67108a88e52a14865/README.md?plain=1#L166-L184)).
  - The newest client release is still [v5.0.1](https://github.com/casper-ecosystem/casper-client-rs/releases/tag/v5.0.1), from 2026-03-16.
- **Open pull requests on 2026-09-23** (GitHub, read that day):
  - [#5442](https://github.com/casper-network/casper-node/pull/5442) "Evm nonce error fix", opened 2026-09-17;
  - [#5443](https://github.com/casper-network/casper-node/pull/5443) "CORE-299 Adding EVM transaction lanes", opened 2026-09-21;
  - [#5445](https://github.com/casper-network/casper-node/pull/5445) "Add EVM access-list support", opened 2026-09-23;
  - [#5446](https://github.com/casper-network/casper-node/pull/5446) "Reconcile EVM rounding dust through mint contract", opened 2026-09-23;
  - [#5448](https://github.com/casper-network/casper-node/pull/5448) "Reject missing referenced EVM bytecode", opened 2026-09-23;
  - [#5438](https://github.com/casper-network/casper-node/pull/5438) "WIP: ContractRuntime::execute_finalized_block and adjacent", opened 2026-08-24;
  - [#5433](https://github.com/casper-network/casper-node/pull/5433), the addressable-entity migration, opened 2026-07-20.

  On 2026-09-23, [#5446](https://github.com/casper-network/casper-node/pull/5446) targeted the branch of [#5445](https://github.com/casper-network/casper-node/pull/5445) (`evm-access-lists`), and [#5448](https://github.com/casper-network/casper-node/pull/5448) targeted the branch of #5446 (`evm-burn-dust`). The rest targeted `feat-evm` (pull request pages, read 2026-09-23).
- **`EVM.md` lags the code**, so treat it as a snapshot.
  - It lists `eth_getTransactionByHash` as not implemented ([L91](https://github.com/casper-network/casper-node/blob/72d8c57cb7b9cfc55d8aaea3f8a3fb553d364af7/EVM.md?plain=1#L91)) and "Missing" ([L165](https://github.com/casper-network/casper-node/blob/72d8c57cb7b9cfc55d8aaea3f8a3fb553d364af7/EVM.md?plain=1#L165)). But the sidecar branch added it on 2026-08-06 in "Add eth_getTransactionByHash and full block transactions" ([c9e2d92](https://github.com/casper-network/casper-sidecar/commit/c9e2d92cf23ca1ffeca8dc85d4150797b002aaf5)).
  - Its caveats say `eth_getBalance`, `eth_getCode` and `eth_estimateGas` "are not implemented yet" ([L1178-L1180](https://github.com/casper-network/casper-node/blob/72d8c57cb7b9cfc55d8aaea3f8a3fb553d364af7/EVM.md?plain=1#L1178-L1180)). Its own table says all three are "Implemented in sidecar" ([L161-L163](https://github.com/casper-network/casper-node/blob/72d8c57cb7b9cfc55d8aaea3f8a3fb553d364af7/EVM.md?plain=1#L161-L163)).
- **The claims about the future.**
  - The Manifest says: "After the Manifest ships, that same developer opens MetaMask, connects to Casper, and deploys her contracts with the toolchain she already knows. Existing Solidity contracts work without modification." It also says the EVM "becomes the third VM in Casper's dispatch layer, executing Solidity bytecode against the same global state as WASM contracts" ([Manifest](https://www.casper.network/news/manifest), read 2026-09-23).
  - The May 20, 2026 recap says "Michael confirmed that EVM compatibility is planned for the end of the year" ([X Space recap](https://www.casper.network/news/casper-x-space-recap-may-20-2026-casper-manifest-rwas-and-the-agentic-buildathon), read 2026-09-23).
  - These are plans. The code above is what existed on 2026-09-23.
- **How to state it.** "There is no EVM on Casper mainnet or testnet as of 2026-09-23. casper-node has an unreleased prototype on the `feat-evm` branch; it executes EVM transactions through revm and is paired with unreleased sidecar and client branches. Even that branch's mainnet chainspec ships the EVM disabled. The Casper Association's published target is 2026 H2 (roadmap) or the end of 2026 (Manifest)." Do not quote the branch's chain ID or fees as live values.

## Addressable entities: off on mainnet, migration work on the EVM branch

- **The setting.** Mainnet has `enable_addressable_entity = false` ([chainspec L177](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L177)).
  - Its comment says that with the flag off, "all Account records will be present under Key::Account and Contracts and their associated ContractPackage will be written underneath Key::Hash" ([L167-L169](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L167-L169)).
  - It also says: "Enabling of the AddressableEntity feature is one-way" ([L175-L176](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L175-L176)).
- **What the chain returns.** On 2026-09-23 at mainnet block 9,028,365:
  - `state_get_package` for package `23036be872bd574590a2c43d4a4eff76b18b4bca815790742841002fdab22cee` returned a `ContractPackage`;
  - `query_global_state` for its contract returned a `Contract`.

  Both are the pre-2.0 record types, not entity records.
- **The migration work.**
  - [PR #5433](https://github.com/casper-network/casper-node/pull/5433), "One time AddressableEntity migration at protocol upgrade", targets `feat-evm`. It was opened 2026-07-20, last updated 2026-08-28, and still open on 2026-09-23. Its description reads "Changed protocol upgrade logic to perform a one time migration of accounts and contracts to AE" and "Changed protocol upgrade logic to write the enable_addressable_entity_flag to global state during the upgrade".
  - The branch's own mainnet chainspec still has `enable_addressable_entity = false` ([chainspec L177 at 72d8c57](https://github.com/casper-network/casper-node/blob/72d8c57cb7b9cfc55d8aaea3f8a3fb553d364af7/resources/mainnet/chainspec.toml#L177)).
- **A known upgrade bug when the flag is on.**
  - odradev published a reproduction on 2026-08-13 ([README L3-L7](https://github.com/odradev/casper_ae_upgrade_bug/blob/9b4fd4638e265daa4d673b9642e092a6475767c4/README.md?plain=1#L3-L7)). It says that calling `add_contract_version` on a package "installed *before* `enable_addressable_entity` was switched on — and that has not yet been migrated by a contract call — **silently loses the added version**".
  - The bug comes from lazy migration "on the first contract call" ([L38-L41](https://github.com/odradev/casper_ae_upgrade_bug/blob/9b4fd4638e265daa4d673b9642e092a6475767c4/README.md?plain=1#L38-L41)). The bypass given is to make any successful contract call before upgrading ([L63-L67](https://github.com/odradev/casper_ae_upgrade_bug/blob/9b4fd4638e265daa4d673b9642e092a6475767c4/README.md?plain=1#L63-L67)).
  - It cannot occur on mainnet while the flag is off ([chainspec L177](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L177)). Whether PR #5433's one-time migration removes it is not stated in either source.
- **Why it matters for the roadmap.** Smart accounts, as drafted in [CEP PR #103](https://github.com/casper-network/ceps/pull/103), extend "the `AddressableEntity` account model". The roadmap's "Unified Account Model" card describes that model as already shipped ([casper.network/roadmap](https://www.casper.network/roadmap), read 2026-09-23).
- **How to state it.** "Addressable entities are disabled on mainnet and testnet (protocol 2.2.2, 2026-09-23). Accounts are `account-hash-…` records and contracts are `hash-…` `Contract`/`ContractPackage` records. A one-time migration is an open pull request against the unreleased EVM branch. Nothing has been released or scheduled." The guide *Where the Casper 2.0 docs differ from mainnet today* in this repository lists the documentation pages that show entity keys.

## CEP-97: accepted as a proposal, not implemented

- **What it proposes.** CEP-97 has two parts ([0097-remove-custom-payment.md L95-L104](https://github.com/casper-network/ceps/blob/3748c9017218378e650d8e5731feaf82088657bd/text/0097-remove-custom-payment.md?plain=1#L95-L104)):
  - remove custom payment: "A transaction that includes Custom Payment wasm is rejected by the node.";
  - lower the minimum main-purse balance and the minimum transfer amount from 2.5 CSPR to "**0.1 CSPR**, aligning it with the current cost of a native CSPR transfer".
- **Its status.**
  - It was merged into casper-network/ceps on 2026-07-02 through [PR #102](https://github.com/casper-network/ceps/pull/102) (merge commit [3748c90](https://github.com/casper-network/ceps/commit/3748c9017218378e650d8e5731feaf82088657bd)). Merging into that repository accepts the text of a proposal; it does not change the node.
  - The newest casper-node release, [v2.2.2](https://github.com/casper-network/casper-node/releases/tag/v2.2.2), was published on 2026-07-01, the day before.
- **Mainnet still uses 2.5 CSPR.**
  - `baseline_motes_amount = 2_500_000_000`, described as "the penalty payment amount, the lowest cost, and the minimum balance amount" ([chainspec L178-L179](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L178-L179)).
  - `native_transfer_minimum_motes = 2_500_000_000`, "The minimum amount in motes for a valid native transfer" ([L199-L200](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L199-L200)).
  - Custom payment is still part of the transaction format: `PricingMode::PaymentLimited` carries `standard_payment: bool` ([pricing_mode.rs L43-L52](https://github.com/casper-network/casper-node/blob/v2.2.2/types/src/transaction/pricing_mode.rs#L43-L52)). casper-client 5.0.1 describes its `--standard-payment` flag as "Flag to determine if this transaction uses standard or custom payment." ([creation_common.rs L399-L413](https://github.com/casper-ecosystem/casper-client-rs/blob/v5.0.1/src/transaction/creation_common.rs#L399-L413)).
- **Not on the EVM branch either.**
  - The `feat-evm` mainnet chainspec keeps both values at 2.5 CSPR ([L179](https://github.com/casper-network/casper-node/blob/72d8c57cb7b9cfc55d8aaea3f8a3fb553d364af7/resources/mainnet/chainspec.toml#L179), [L200](https://github.com/casper-network/casper-node/blob/72d8c57cb7b9cfc55d8aaea3f8a3fb553d364af7/resources/mainnet/chainspec.toml#L200) at 72d8c57).
  - The only related code is the WIP pull request [#5438](https://github.com/casper-network/casper-node/pull/5438), opened 2026-08-24 against `feat-evm` (read 2026-09-23). Its description says it "removes custom payment", among other changes.
- **Statements that present it as done.**
  - casper.network's csprUSD article says "Casper addressed this challenge with the adoption of CEP-97, reducing the minimum transaction cost from 2.5 CSPR to just 0.1 CSPR" ([Introducing csprUSD](https://www.casper.network/news/introducing-csprusd-the-stablecoin-of-the-machine-economy), read 2026-09-23).
  - The press release of 2026-07-29 says "With the recent acceptance of CEP-97, Casper reduces the network's minimum transaction cost from 2.5 CSPR to just 0.1 CSPR" ([Chainwire](https://chainwire.org/2026/07/29/csprusd-launching-as-caspers-standard-stablecoin-rebuilt-for-the-machine-economy/), read 2026-09-23).
  - casper.network's "How Casper Solves the AI Commerce Bottleneck", which its news list dates to August 12, 2026, lists "CEP-97 (Micro-Fees): Network execution costs are reduced" as one part of what it calls Casper's "coordinated execution architecture" ([article](https://www.casper.network/news/how-casper-solves-the-ai-commerce-bottleneck), [casper.network/news](https://www.casper.network/news), both read 2026-09-23).
  - None of the three matches the chainspec that mainnet served on 2026-09-23, where the lowest cost and the minimum transfer are still 2.5 CSPR ([L178-L179](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L178-L179), [L199-L200](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L199-L200)).
- **What does cost 0.1 CSPR today.**
  - A native transfer is charged `mint_costs.transfer = 100_000_000` motes, which is 0.1 CSPR ([chainspec L473](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L473)), and a delegation `2_500_000_000` motes ([L453](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L453)). So the Manifest's "A native CSPR transfer costs exactly 0.1 CSPR. A delegation costs exactly 2.5 CSPR." matches mainnet ([Manifest](https://www.casper.network/news/manifest), read 2026-09-23).
  - The smallest amount a native transfer can move is still 2.5 CSPR ([L199-L200](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L199-L200)).
  - A contract call that pays less than `baseline_motes_amount` is refused ([deploy.rs L556-L572](https://github.com/casper-network/casper-node/blob/v2.2.2/types/src/transaction/deploy.rs#L556-L572), [meta_transaction_v1.rs L568-L570](https://github.com/casper-network/casper-node/blob/v2.2.2/node/src/types/transaction/meta_transaction/meta_transaction_v1.rs#L568-L570)).
- **How to state it.** "CEP-97 was accepted as a proposal on 2026-07-02. No casper-node release implements it. On mainnet (protocol 2.2.2, 2026-09-23) the minimum transfer amount, the minimum balance and the smallest payment a contract call may carry are still 2.5 CSPR, and custom payment still exists. A native transfer costs 0.1 CSPR to execute, as it did before CEP-97."

## csprUSD: an upgraded contract on testnet, the 2024 contract on mainnet

- **The announcement.**
  - casper.network's news list dates "Introducing csprUSD: The Stablecoin of the Machine Economy" to July 29, 2026 ([casper.network/news](https://www.casper.network/news), read 2026-09-23).
  - The article says "First launched by Sarson Funds in 2024, csprUSD is now being updated as the Casper ecosystem's standard dollar stablecoin". It says "The upgrade makes csprUSD the default settlement asset for Casper's x402 payment infrastructure" and "csprUSD also implements CEP-3009". It gives no contract hash ([Introducing csprUSD](https://www.casper.network/news/introducing-csprusd-the-stablecoin-of-the-machine-economy), read 2026-09-23).
- **The timing it gave.** The press release published the same day, 2026-07-29 (`article:published_time` 2026-07-29T13:04:59+00:00), says:
  - "The upgraded contract will complete a new security audit before deployment, extending the Halborn audit that covered the original."
  - "The upgraded csprUSD contract is expected to reach Casper Mainnet later in Q3, following Testnet validation, security auditing, and regulatory compliance." ([Chainwire](https://chainwire.org/2026/07/29/csprusd-launching-as-caspers-standard-stablecoin-rebuilt-for-the-machine-economy/), read 2026-09-23).
- **An older testnet announcement.** An undated casper.network article says Sarson Funds' csprUSD "is now live on the Casper Network testnet" and "The mainnet launch of csprUSD will be a major milestone" ([Sarson Funds csprUSD Stablecoin Live on Casper Network Testnet](https://www.casper.network/news/sarson-funds-csprusd-stablecoin-live-on-casper-network-testnet), read 2026-09-23).
- **Which contract is csprUSD.** The x402 Foundation's TypeScript package `@x402/casper` 2.27.0 names two packages:
  - "csprUSD package address on Mainnet" `23036be872bd574590a2c43d4a4eff76b18b4bca815790742841002fdab22cee`;
  - on testnet, `0cb6f94834c60510d532b0ae077b18b4100874a4c867396d61c2b13c790ead52`.

  Both have 6 decimals ([constants.ts L40-L55](https://github.com/x402-foundation/x402/blob/npm-@x402/casper@v2.27.0/typescript/packages/mechanisms/casper/src/constants.ts#L40-L55)). The package makes them its default assets on each network ([defaultAssets.ts L24-L44](https://github.com/x402-foundation/x402/blob/npm-@x402/casper@v2.27.0/typescript/packages/mechanisms/casper/src/defaultAssets.ts#L24-L44)). No Casper Association or Sarson Funds page read for this guide gives a contract hash.
- **Mainnet, read on 2026-09-23 at block 9,028,365.**
  - `state_get_package` for `23036be8…2cee` returned one contract version, `bfcc7bb8e1966873dce870fe7aac94230dfea851dce663a4daab629210d4c6a5`, under protocol major version 1, with `"lock_status": "Unlocked"`.
  - `query_global_state` for that contract returned `"protocol_version": "1.5.6"`. Its `name` and `symbol` named keys read `csprUSD`, its `decimals` 6 and its `total_supply` 250000000000 (250,000 csprUSD at 6 decimals).
  - Its 32 entry points include none of CEP-3009's four: `transfer_with_authorization`, `receive_with_authorization`, `cancel_authorization` and `authorization_state` ([CEP-3009 L31-L36](https://github.com/casper-network/ceps/blob/3748c9017218378e650d8e5731feaf82088657bd/text/3009-transfer-with-authorization.md?plain=1#L31-L36)).
- **Testnet, read on 2026-09-23 at block 9,269,744.**
  - `state_get_package` for `0cb6f948…ad52` returned two versions, with version 1 disabled.
  - The current contract, `a5a6f9baaff9cc2dc3157a350a2ee9b18bfa0ec8af8b5e9ae5572405866e2d38`, returned `"protocol_version": "2.2.2"` and has 41 entry points, including all four CEP-3009 entry points. Its `total_supply` read 30000000000.
- **No mainnet announcement.** On 2026-09-23 casper.network's news list showed posts from June 5 to September 22, 2026. None after July 29 announced csprUSD on mainnet ([casper.network/news](https://www.casper.network/news), read 2026-09-23).
- **How to state it.** "As of 2026-09-23 no mainnet deployment of the upgraded csprUSD had been announced, and the mainnet package that `@x402/casper` 2.27.0 uses as csprUSD had no CEP-3009 entry points. The upgraded contract, with CEP-3009 authorized transfers and meant for x402, was on testnet. Mainnet has a csprUSD contract installed under protocol 1.5.6, which cannot accept CEP-3009 authorizations. On 2026-07-29 the Casper Association and Sarson Funds said the upgrade was expected on mainnet later in Q3 2026, after an audit." The mainnet package is unlocked, so it could gain a new version under the same package hash. Whether the upgrade will use that package or a new one has not been published.

## x402 on mainnet: a facilitator, and which token it can settle

- **What the Casper Association says.**
  - The roadmap card reads "X402 Micropayments", "In Progress", "Target: 2026 H2", "Casper will be the first WASM-native L1 with X402 in production" ([casper.network/roadmap](https://www.casper.network/roadmap), read 2026-09-23).
  - The Manifest said in May: "Production hardening and facilitator integration are weeks away from completion." ([Manifest](https://www.casper.network/news/manifest), read 2026-09-23).
  - On 2026-07-29 the csprUSD article said "Casper already supports this model on Mainnet through its official x402 Facilitator." ([Introducing csprUSD](https://www.casper.network/news/introducing-csprusd-the-stablecoin-of-the-machine-economy), read 2026-09-23). The press release said "an x402 facilitator is live on Casper Mainnet today" ([Chainwire](https://chainwire.org/2026/07/29/csprusd-launching-as-caspers-standard-stablecoin-rebuilt-for-the-machine-economy/), read 2026-09-23).
- **What the facilitator documents.**
  - CSPR.cloud's page for its facilitator's `GET /supported` gives an example response with the networks `casper:casper` and `casper:casper-test`. It says the call "Requires an `Authorization` header with a valid CSPR.cloud access token." ([docs.cspr.cloud: Supported](https://docs.cspr.cloud/x402-facilitator-api/supported), fetched 2026-09-23).
  - This guide did not call that endpoint.
- **What a payment needs.**
  - make-software's implementation settles "on-chain using CEP-18 tokens authorized via EIP-712 signatures" through "the same CEP-18 `transfer_with_authorization` entry point" ([casper-x402 README L3-L16](https://github.com/make-software/casper-x402/blob/3ee705ecfff44795bd502b101991964ce4dc037d/README.md?plain=1#L3-L16)). So a mainnet x402 payment needs a mainnet token that has that entry point.
  - The default mainnet asset in `@x402/casper` 2.27.0 is the csprUSD package ([defaultAssets.ts L24-L34](https://github.com/x402-foundation/x402/blob/npm-@x402/casper@v2.27.0/typescript/packages/mechanisms/casper/src/defaultAssets.ts#L24-L34)). On 2026-09-23 that package had no such entry point (previous section).
  - Read together, the code and the chain say that a payment relying on that default could not settle on mainnet until that contract package gains CEP-3009 or `@x402/casper` changes its default mainnet asset. That is this guide's inference. The x402 Foundation and CSPR.cloud do not say it.
- **How to state it.** "The Casper Association has said since July 2026 that an x402 facilitator is live on mainnet. Settlement needs a CEP-18 token with `transfer_with_authorization`. As of 2026-09-23 the mainnet package that `@x402/casper` 2.27.0 uses as csprUSD had no such entry point, and no mainnet csprUSD contract that has one had been announced."

## Where casper.network's "already shipped" list contradicts mainnet

The roadmap page introduces five capabilities with "These are the capabilities that already shipped with Casper, and now form the bedrock that Casper Manifest builds on." ([casper.network/roadmap](https://www.casper.network/roadmap), read 2026-09-23). Each is checked here against the v2.2.2 mainnet chainspec that mainnet served on 2026-09-23, with other casper.network statements after them.

| Claim (quoted as read on 2026-09-23) | Where | What mainnet runs (v2.2.2) | Result |
| --- | --- | --- | --- |
| "Multi-VM Execution … WASM and EVM contracts share the same global state, same finality, same block — a true polyglot execution layer." | [/roadmap](https://www.casper.network/roadmap), "The Foundation" | Only `vm_casper_v1` is enabled, and there is no EVM ([chainspec L204-L207](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L204-L207), [transaction.rs L136-L150](https://github.com/casper-network/casper-node/blob/v2.2.2/types/src/transaction.rs#L136-L150)). A VM2 transaction is rejected with `InvalidTransactionRuntime` ([meta_transaction_v1.rs L63-L77](https://github.com/casper-network/casper-node/blob/v2.2.2/node/src/types/transaction/meta_transaction/meta_transaction_v1.rs#L63-L77)). The v2.0.3 notes call VM2 "not intended to be turned on for mainnet as part of this rollout" ([v2.0.3](https://github.com/casper-network/casper-node/releases/tag/v2.0.3)). | Contradicted: one VM runs, and no EVM contract can exist. |
| "Unified Account Model: Accounts and contracts merged into a single entity type. Every account can hold code; every contract can hold keys." | [/roadmap](https://www.casper.network/roadmap), "The Foundation" | `enable_addressable_entity = false`: accounts stay under `Key::Account` and contracts under `Key::Hash` ([chainspec L165-L177](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L165-L177)). | Contradicted: the code exists in the node but is switched off. |
| "Pluggable Crypto … Ed25519 and secp256k1 today, with a clear path to post-quantum schemes — no hard fork required." | [/roadmap](https://www.casper.network/roadmap), "The Foundation" | Public keys are `System`, `Ed25519` or `Secp256k1` ([asymmetric_key.rs L480-L492](https://github.com/casper-network/casper-node/blob/v2.2.2/types/src/crypto/asymmetric_key.rs#L480-L492)). | The "today" part matches. "No hard fork required" is a claim about the future. |
| "Fixed Costs: Deterministic, chainspec-defined pricing for all transaction types. No gas auctions, no fee spikes." | [/roadmap](https://www.casper.network/roadmap), "The Foundation" | The gas price is pinned at 1 (`max_gas_price = 1`, `min_gas_price = 1`, [L509-L510](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L509-L510)), and native transfers and delegations have fixed costs ([L453](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L453), [L473](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L473)). But pricing is `payment_limited`, where "senders of transaction self-specify how much they pay", not `fixed`, where "costs are fixed, per the cost table" ([L129-L135](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L129-L135)). A Wasm transaction pays according to gas used and its payment amount, with 75% of the unused part refunded ([L114-L117](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L114-L117)). | Partly: there are no gas auctions or spikes, but not every transaction type has a fixed chainspec price. |
| "Fee Delegation: Native delegation-based gas models built into the protocol. Third parties can sponsor transaction fees at the protocol level — not via wrapper contracts." | [/roadmap](https://www.casper.network/roadmap), "The Foundation" | `PricingMode::Prepaid` is "for future use, not currently implemented" ([pricing_mode.rs L69-L74](https://github.com/casper-network/casper-node/blob/v2.2.2/types/src/transaction/pricing_mode.rs#L69-L74)), and `allow_prepaid = false` ([L136-L139](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L136-L139)). The Manifest puts protocol fee delegation in the future: "Phase two brings fee delegation directly into the protocol through two mechanisms: a gas_payer field on transactions, and PricingMode::Prepaid" ([Manifest](https://www.casper.network/news/manifest)). | Contradicted, by the chain and by the Manifest. |
| "With Casper 2.0, the network introduced unified accounts and contracts at the protocol level. Accounts are no longer just key pairs." | [X Space recap, May 20, 2026](https://www.casper.network/news/casper-x-space-recap-may-20-2026-casper-manifest-rwas-and-the-agentic-buildathon) | As for the Unified Account Model row ([chainspec L177](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L177)). | Contradicted. |
| "Casper addressed this challenge with the adoption of CEP-97, reducing the minimum transaction cost from 2.5 CSPR to just 0.1 CSPR" | [Introducing csprUSD](https://www.casper.network/news/introducing-csprusd-the-stablecoin-of-the-machine-economy) | `baseline_motes_amount` and `native_transfer_minimum_motes` are both 2.5 CSPR ([L178-L179](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L178-L179), [L199-L200](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L199-L200)). | Contradicted (see *CEP-97*). |
| "CEP-97 (Micro-Fees): Network execution costs are reduced" | ["How Casper Solves the AI Commerce Bottleneck"](https://www.casper.network/news/how-casper-solves-the-ai-commerce-bottleneck), dated August 12, 2026 on the [news list](https://www.casper.network/news) | CEP-97 is a merged proposal that no release implements, and the 2.5 CSPR minimums it would lower are unchanged ([L178-L179](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L178-L179), [L199-L200](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L199-L200)). | Contradicted (see *CEP-97*). |
| "Account and contract unification", the first of "five design decisions already available in Casper's protocol"; near its end the page refers to "the six design decisions already live on mainnet" | [Manifest](https://www.casper.network/news/manifest) | `enable_addressable_entity = false` ([chainspec L177](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L177)). | Contradicted as a mainnet claim: the code exists in the node but is switched off. |

- **Where the Manifest's wording matches mainnet.** Both quotes are from the [Manifest](https://www.casper.network/news/manifest), read 2026-09-23.
  - It says Casper 2.0 "moved the protocol toward a unified model where user accounts and smart contracts are treated as the same kind of first-class object".
  - It says of multiple VMs: "Today that means WASM. Tomorrow it can mean EVM alongside WASM."

  Both match mainnet. But the same page lists account and contract unification, which is switched off on mainnet ([chainspec L177](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L177)), among "five design decisions already available in Casper's protocol", and later refers to "the six design decisions already live on mainnet" (same page, read 2026-09-23; see the table above). The page does not say which six.
- **"An activation rather than a migration."** The Manifest's Smart Accounts section says that because Casper 2.0 "already moved toward a unified account and contract model at the data layer", upgrading a basic account into a smart account "becomes an activation rather than a migration" ([Manifest](https://www.casper.network/news/manifest), read 2026-09-23). The open pull request [#5433](https://github.com/casper-network/casper-node/pull/5433) on the unreleased EVM branch performs "a one time migration of accounts and contracts to AE" at a protocol upgrade (read 2026-09-23; see *Addressable entities*).
- **Consistent with mainnet.**
  - The Manifest says "Casper 2.1 cut block time from 16 seconds to 8 and introduced protocol-level fee burning" ([Manifest](https://www.casper.network/news/manifest), read 2026-09-23). Mainnet has `fee_handling = { type = 'burn' }` ([chainspec L126](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L126)) and an [8000 ms minimum block time](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L32).
  - The press release's "a multi-VM execution layer supporting both WebAssembly and soon EVM smart contracts" also matches ([Chainwire](https://chainwire.org/2026/07/29/csprusd-launching-as-caspers-standard-stablecoin-rebuilt-for-the-machine-economy/), read 2026-09-23).

## What nobody has published

An honest refusal beats a guess. As of 2026-09-23 none of the following appeared in the sources above. None should be answered from memory:

- **A release, version or date for the EVM** on mainnet or testnet. The published targets are "2026 H2" ([roadmap](https://www.casper.network/roadmap), read 2026-09-23) and "by end of 2026" ([Manifest](https://www.casper.network/news/manifest), read 2026-09-23). Nobody has said which casper-node version will carry it, and there is no live EVM chain ID.
- **When addressable entities will be enabled**, and whether the one-time migration of [PR #5433](https://github.com/casper-network/casper-node/pull/5433) ships with the EVM.
- **A casper-node release that implements CEP-97**, or a date when the 2.5 CSPR minimums change.
- **The upgraded csprUSD's mainnet contract.** Also missing: its new audit report, whether it will be a new version of package `23036be8…2cee` or a new package, and its centralized exchange listings, which the press release says "have already been confirmed" without naming them ([Chainwire](https://chainwire.org/2026/07/29/csprusd-launching-as-caspers-standard-stablecoin-rebuilt-for-the-machine-economy/), read 2026-09-23).
- **Which tokens the mainnet x402 facilitator settles**, and how many x402 payments have settled on mainnet.
- **CEPs or public code** for networking hardening, the Native Token Registry, batch transactions, transaction privacy or quantum safety, or an official ERC-3643 implementation. The Manifest promises CEPs "for each initiative" ([Manifest](https://www.casper.network/news/manifest), read 2026-09-23).
- **The Manifest's author and date.** The page shows neither. The date above comes from the sitemap and the May 20 recap.
- **A change log for the roadmap page.** It shows no "last updated" date; only the sitemap's `lastmod` (2026-08-28) dates it.

## How to check this yourself

```bash
# Protocol version and any scheduled upgrade ("next_upgrade": null means none)
curl -s -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"info_get_status"}' \
  https://node.mainnet.casper.network/rpc

# Protocol versions staged for mainnet (a 2_3_* or 3_* line means an upgrade is staged)
curl -s https://genesis.casper.network/casper/protocol_versions

# Newest casper-node release tag
gh api repos/casper-network/casper-node/releases/latest --jq .tag_name

# The chainspec mainnet is running: look for [evm], enable_addressable_entity and the 2.5 CSPR minimums
curl -s -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"info_get_chainspec"}' \
  https://node.mainnet.casper.network/rpc \
  | python -c "import json,sys; print(bytes.fromhex(json.load(sys.stdin)['result']['chainspec_bytes']['chainspec_bytes']).decode())" \
  | grep -n -E '^\[evm\]|enable_addressable_entity|vm_casper_v2|baseline_motes_amount|native_transfer_minimum_motes'

# Does the node speak Ethereum JSON-RPC? (error -32601 means no)
curl -s -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"eth_chainId","params":[]}' \
  https://node.mainnet.casper.network/rpc

# How far the EVM branch is from dev
gh api repos/casper-network/casper-node/compare/dev...feat-evm --jq '"ahead \(.ahead_by), behind \(.behind_by)"'

# The csprUSD package on mainnet: its versions, then its current contract's entry points
curl -s -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"state_get_package","params":{"package_identifier":{"ContractPackageHash":"contract-package-23036be872bd574590a2c43d4a4eff76b18b4bca815790742841002fdab22cee"}}}' \
  https://node.mainnet.casper.network/rpc
curl -s -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"query_global_state","params":{"state_identifier":null,"key":"hash-bfcc7bb8e1966873dce870fe7aac94230dfea851dce663a4daab629210d4c6a5","path":[]}}' \
  https://node.mainnet.casper.network/rpc \
  | python -c "import json,sys; c=json.load(sys.stdin)['result']['stored_value']['Contract']; print(sorted(e['name'] for e in c['entry_points']))"
```

If the package gains a version, the last entry of `versions` in the first response names the contract to query in the second.

## Sources

Pinned sources (tags and commits), read 2026-09-23:

- casper-node [v2.2.2](https://github.com/casper-network/casper-node/releases/tag/v2.2.2):
  - [resources/mainnet/chainspec.toml](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml) and [resources/testnet/chainspec.toml](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/testnet/chainspec.toml);
  - [types/src/transaction.rs](https://github.com/casper-network/casper-node/blob/v2.2.2/types/src/transaction.rs#L136-L150), [types/src/transaction/pricing_mode.rs](https://github.com/casper-network/casper-node/blob/v2.2.2/types/src/transaction/pricing_mode.rs#L36-L75), [types/src/crypto/asymmetric_key.rs](https://github.com/casper-network/casper-node/blob/v2.2.2/types/src/crypto/asymmetric_key.rs#L480-L492) and [types/src/transaction/deploy.rs](https://github.com/casper-network/casper-node/blob/v2.2.2/types/src/transaction/deploy.rs#L556-L572);
  - [node/src/types/transaction/meta_transaction/meta_transaction_v1.rs](https://github.com/casper-network/casper-node/blob/v2.2.2/node/src/types/transaction/meta_transaction/meta_transaction_v1.rs#L63-L77);
  - the [v2.0.3 release notes](https://github.com/casper-network/casper-node/releases/tag/v2.0.3).
- casper-node branch `feat-evm` at [72d8c57cb7b9cfc55d8aaea3f8a3fb553d364af7](https://github.com/casper-network/casper-node/tree/72d8c57cb7b9cfc55d8aaea3f8a3fb553d364af7) (2026-09-18):
  - [EVM.md](https://github.com/casper-network/casper-node/blob/72d8c57cb7b9cfc55d8aaea3f8a3fb553d364af7/EVM.md?plain=1), 58,977 bytes, SHA-256 `4ab5068cfa47e9b1f89c41bf2d865ac61a79da5042a2308584dd7f5c325df7cf`;
  - [resources/mainnet/chainspec.toml](https://github.com/casper-network/casper-node/blob/72d8c57cb7b9cfc55d8aaea3f8a3fb553d364af7/resources/mainnet/chainspec.toml), [resources/testnet/chainspec.toml](https://github.com/casper-network/casper-node/blob/72d8c57cb7b9cfc55d8aaea3f8a3fb553d364af7/resources/testnet/chainspec.toml) and [types/src/transaction.rs](https://github.com/casper-network/casper-node/blob/72d8c57cb7b9cfc55d8aaea3f8a3fb553d364af7/types/src/transaction.rs#L145-L156);
  - the comparison with `dev` at [f986c05](https://github.com/casper-network/casper-node/compare/f986c0506957c276c691f8f9dbb440c4ae33e9a1...72d8c57cb7b9cfc55d8aaea3f8a3fb553d364af7);
  - its first commit, [f8d3324](https://github.com/casper-network/casper-node/commit/f8d3324cd411806c98dd7dc26f413c531e02d5da).
- casper-sidecar:
  - [v2.1.0 rpc_schema.json](https://github.com/casper-network/casper-sidecar/blob/v2.1.0/resources/test/rpc_schema.json);
  - branch `evm` at [ecf43cc](https://github.com/casper-network/casper-sidecar/blob/ecf43cc206b33edc0918709df34891b075a755eb/resources/test/rpc_schema.json), [compared with `dev` at 62c9522](https://github.com/casper-network/casper-sidecar/compare/62c9522eac936c8940a7b723b74c49fb5b0bddae...ecf43cc206b33edc0918709df34891b075a755eb);
  - commits [b6e5d86](https://github.com/casper-network/casper-sidecar/commit/b6e5d86f74b4b79990336ccf6ca86a8f01686d07) and [c9e2d92](https://github.com/casper-network/casper-sidecar/commit/c9e2d92cf23ca1ffeca8dc85d4150797b002aaf5).
- casper-client-rs:
  - [v5.0.1 creation_common.rs](https://github.com/casper-ecosystem/casper-client-rs/blob/v5.0.1/src/transaction/creation_common.rs#L399-L413);
  - branch `evm` at [dc3dfb1](https://github.com/casper-ecosystem/casper-client-rs/tree/dc3dfb14e022e343435b42e67108a88e52a14865): [CHANGELOG.md](https://github.com/casper-ecosystem/casper-client-rs/blob/dc3dfb14e022e343435b42e67108a88e52a14865/CHANGELOG.md?plain=1#L12-L15) and [README.md](https://github.com/casper-ecosystem/casper-client-rs/blob/dc3dfb14e022e343435b42e67108a88e52a14865/README.md?plain=1#L166-L184), [compared with `dev` at 10329ed](https://github.com/casper-ecosystem/casper-client-rs/compare/10329ed947bbf851b612a207729c3d68a784c896...dc3dfb14e022e343435b42e67108a88e52a14865).
- casper-network/ceps at [3748c90](https://github.com/casper-network/ceps/tree/3748c9017218378e650d8e5731feaf82088657bd) (2026-07-02): [text/0097-remove-custom-payment.md](https://github.com/casper-network/ceps/blob/3748c9017218378e650d8e5731feaf82088657bd/text/0097-remove-custom-payment.md?plain=1), [text/3009-transfer-with-authorization.md](https://github.com/casper-network/ceps/blob/3748c9017218378e650d8e5731feaf82088657bd/text/3009-transfer-with-authorization.md?plain=1) and [text/2612-permit-extension.md](https://github.com/casper-network/ceps/blob/3748c9017218378e650d8e5731feaf82088657bd/text/2612-permit-extension.md?plain=1).
- x402-foundation/x402 at tag `npm-@x402/casper@v2.27.0` (commit `71eb9a55e081e7b81ba3046d0bd17c3eb9c7bf81`):
  - [constants.ts](https://github.com/x402-foundation/x402/blob/npm-@x402/casper@v2.27.0/typescript/packages/mechanisms/casper/src/constants.ts#L40-L55) and [defaultAssets.ts](https://github.com/x402-foundation/x402/blob/npm-@x402/casper@v2.27.0/typescript/packages/mechanisms/casper/src/defaultAssets.ts#L24-L44);
  - the npm tarball `https://registry.npmjs.org/@x402/casper/-/casper-2.27.0.tgz` (SHA-256 `92785b14b4b19db9c3669ec22870a539e61516875fc154ce99b09580c9db751d`) contains the same mainnet package hash.
- make-software/casper-x402 at [3ee705e](https://github.com/make-software/casper-x402/blob/3ee705ecfff44795bd502b101991964ce4dc037d/README.md?plain=1#L1-L16).
- casper-ecosystem/casper-manager at tag `casper-manager@2.0.0`: [snap.manifest.json](https://github.com/casper-ecosystem/casper-manager/blob/casper-manager@2.0.0/packages/snap/snap.manifest.json), [FAQ.md](https://github.com/casper-ecosystem/casper-manager/blob/casper-manager@2.0.0/FAQ.md?plain=1#L21-L25), [packages/snap/src/index.tsx](https://github.com/casper-ecosystem/casper-manager/blob/casper-manager@2.0.0/packages/snap/src/index.tsx#L444-L523) and [packages/lib/README.md](https://github.com/casper-ecosystem/casper-manager/blob/casper-manager@2.0.0/packages/lib/README.md?plain=1#L72-L90); newest commit [d2df190](https://github.com/casper-ecosystem/casper-manager/commit/d2df19082945f6cae88ee1c5ccd42981cef7a118).
- casper-network/docs-redux at [c78e3c2](https://github.com/casper-network/docs-redux/blob/c78e3c2040d30fd8c42cb95bc8a3b308db9d1a56/versioned_docs/version-2.0.0/resources/build-on-casper.md?plain=1): `resources/build-on-casper.md`.
- odradev/odradev.github.io at [5af9dfb](https://github.com/odradev/odradev.github.io/blob/5af9dfbac32814c1542744a819210d68b1bc0b7d/docusaurus/versioned_docs/version-2.9/tutorials/odra-sol.md?plain=1): "Odra for Solidity developers".
- odradev/casper_ae_upgrade_bug at [9b4fd46](https://github.com/odradev/casper_ae_upgrade_bug/blob/9b4fd4638e265daa4d673b9642e092a6475767c4/README.md?plain=1) (2026-08-13).

Websites read 2026-09-23. The digests let a reader tell whether a later copy is the same file.

- [https://www.casper.network/roadmap](https://www.casper.network/roadmap): 189,649 bytes, SHA-256 `7f278a25dc1e7154166c350161661818c0f340538ee7bdc58038beab0ed449be`.
- [https://www.casper.network/news/manifest](https://www.casper.network/news/manifest): 224,613 bytes, SHA-256 `a7cd0b29e870a2733c26fa43850c4cfdc2b47480458063b9282764decfb69bba`.
- [X Space recap, May 20, 2026](https://www.casper.network/news/casper-x-space-recap-may-20-2026-casper-manifest-rwas-and-the-agentic-buildathon): 221,262 bytes, SHA-256 `3da2b129a7aba6c4db8cddee2de02519d78f9c0dc7db07ceb0e1428796bb144e`.
- [Introducing csprUSD](https://www.casper.network/news/introducing-csprusd-the-stablecoin-of-the-machine-economy): 207,336 bytes, SHA-256 `4f32b15f0c9394c02fa856a50c4213e0e8bd86a3fd907be64f189026390f03e3`.
- [How Casper Solves the AI Commerce Bottleneck](https://www.casper.network/news/how-casper-solves-the-ai-commerce-bottleneck): 208,526 bytes, SHA-256 `0ea7f5543be4fe381534d229ce584cc17b0361387c2e3db0213b71321dcf1eb9`.
- [Sarson Funds csprUSD Stablecoin Live on Casper Network Testnet](https://www.casper.network/news/sarson-funds-csprusd-stablecoin-live-on-casper-network-testnet): 204,246 bytes, SHA-256 `bd590c3b1dd8d539286af1a1bff6ce2f19e5f5ec1ca692718b46ad3e201c3790`.
- [https://www.casper.network/protocol-roadmap](https://www.casper.network/protocol-roadmap): 182,655 bytes, SHA-256 `2bb8600bddab1a7003bde200429ab9244d19e2ea7e5f3e6ad01b7af021f3f740`. Its slide images, served under fixed names:
  - [Slide 1](https://cdn.prod.website-files.com/668fef77d8ac075ed5e3f57a/66919e43893cf77d0cb1405b_Slide%201.webp): 30,806 bytes, SHA-256 `c95fda6122b3c7a3de435ac72da9979a292a5e96453b97b33a1f73d6fceb8467`.
  - [Slide 3](https://cdn.prod.website-files.com/668fef77d8ac075ed5e3f57a/66919e3cf23d82e50e8ef247_Slide%203.png): 41,364 bytes, SHA-256 `96ab23b8fdd8311743dde9f76ce2c4f8a8a0d0112dbf5caad348c1fabb323b44`.
  - [Slide 6](https://cdn.prod.website-files.com/668fef77d8ac075ed5e3f57a/66919e3c61a0eb56613e2350_Slide%206.webp): 53,106 bytes, SHA-256 `bc08dd1d5b6c0eb964774effc371c8b61ca2bf6151116bd747b4661ac4d66a74`.
- [https://www.casper.network/news](https://www.casper.network/news): 227,654 bytes, SHA-256 `d2fb054a6b46d07efd4d1e0ec366659a77ea83d1c624956b10cd36d52c8d0048`.
- [https://www.casper.network/sitemap.xml](https://www.casper.network/sitemap.xml): 72,940 bytes, SHA-256 `d04e89ea8027f078e82a9da957f3abd348c53409a71f8b56a626ff7122fc2bd0`.
- casper.network's `robots.txt` read 2026-09-23 contained only a `Sitemap` line.
- [Chainwire press release of 2026-07-29](https://chainwire.org/2026/07/29/csprusd-launching-as-caspers-standard-stablecoin-rebuilt-for-the-machine-economy/): 119,337 bytes, SHA-256 `6ada21ad5b16e067011b31d02d2e8e60bfc2d6250dc75d9c833ca0a9fc8ed639`.
- [docs.cspr.cloud: Supported](https://docs.cspr.cloud/x402-facilitator-api/supported), fetched as markdown (`https://docs.cspr.cloud/x402-facilitator-api/supported.md`): 3,993 bytes, SHA-256 `6f43c4cfa84665a580b3d6d840efaf53054ef9c6fa6b22cfad76f3483cb8af10`. That response wraps the page in a header line and an "Agent Instructions" footer that GitBook adds; without the wrapper the page is 2,458 bytes, SHA-256 `43547124296c47e368eb2b0164fe2de628b501ab7b0f691a6740c93058d650c9`. A change in GitBook's wrapper alone changes the first digest.
- [docs.astralbeam.io](https://docs.astralbeam.io/), fetched as markdown: 5,641 bytes, SHA-256 `66cfebdf913c3826b22f4446ebb00900c7fa6225e5f80f4702ba7b1e9e8ab30e`.

Live and unpinnable, read 2026-09-23 between 16:30 and 16:43 UTC. Every figure taken from these is dated in the text above.

- `https://node.mainnet.casper.network/rpc` and `https://node.testnet.casper.network/rpc`:
  - `info_get_status`;
  - `info_get_chainspec` (mainnet 22,797 bytes, SHA-256 `1475bf5329f9138fc0a2209a80237cc59a301f1c8f75d43ac48266768e750d68`, identical to the v2.2.2 file);
  - `eth_chainId`;
  - `state_get_package` and `query_global_state` at mainnet block 9,028,365 and testnet block 9,269,744.
- `https://genesis.casper.network/casper/protocol_versions` and `https://genesis.casper.network/casper-test/protocol_versions`.
- The GitHub API for the casper-node, casper-sidecar and casper-client-rs releases, tags, branches and pull requests. Also the GitHub API for the casper-network/ceps pull requests and for repository searches.
- Pull request pages: casper-node [#5433](https://github.com/casper-network/casper-node/pull/5433), [#5438](https://github.com/casper-network/casper-node/pull/5438), [#5442](https://github.com/casper-network/casper-node/pull/5442), [#5443](https://github.com/casper-network/casper-node/pull/5443), [#5445](https://github.com/casper-network/casper-node/pull/5445), [#5446](https://github.com/casper-network/casper-node/pull/5446) and [#5448](https://github.com/casper-network/casper-node/pull/5448); casper-sidecar [#474](https://github.com/casper-network/casper-sidecar/pull/474); ceps [#99](https://github.com/casper-network/ceps/pull/99), [#100](https://github.com/casper-network/ceps/pull/100), [#102](https://github.com/casper-network/ceps/pull/102) and [#103](https://github.com/casper-network/ceps/pull/103).
- The npm registry for `casper-manager` and `@x402/casper`.
