---
name: casper
description: Answer questions about the Casper Network (CSPR) and build on it from current, cited sources. Use for Casper concepts, accounts and keys, staking and delegation, fees and gas, casper-client commands, smart contracts and Odra, token and NFT standards (CEP-18, CEP-78, CEP-95), the Casper SDKs, CSPR.cloud, CSPR.click, x402 payments on Casper, and Casper MCP servers. It says where each kind of answer lives and which official documentation is out of date.
---

# Casper Network

The official documentation at docs.casper.network describes Casper 2.0, and mainnet has moved
on: several values it states are no longer true. This skill says where current answers live and
which facts to check before trusting the docs.

## Rules

1. **Check what changed before answering from the docs.** For fees and pricing, payment
   minimums, staking and delegation limits, rewards, TTL, the account model, or casper-client
   syntax, read the guides below first, and say which release your answer applies to.
2. **Cite.** In this hub's llms.txt indexes, the URL after the colon on each line is the page to
   send a person to; the CSPR.click and CSPR.cloud llms.txt files link every page as markdown, so
   cite those pages without `.md` ([llms.txt](https://raw.githubusercontent.com/msanlisavas/casper-llms/main/llms.txt)).
3. **Never handle keys.** Do not ask for, accept, print or store a secret key, seed phrase or
   keystore password, and never pass one to a tool: tool arguments go through the model. Give
   commands as text the user runs, with placeholders such as `<PATH-TO-YOUR-SECRET-KEY>`.
4. **Testnet first.** For anything that moves funds, give the testnet form (chain name
   `casper-test`) before mainnet (`casper`).
5. **Say when sources disagree, or do not cover the question,** instead of filling the gap from
   memory. Casper changed substantially in 2.0, and older answers are often wrong.

## Current mainnet facts the docs get wrong or leave out

Each value is from the mainnet chainspec at casper-node v2.2.2 unless another source is linked;
[Where the Casper 2.0 docs differ from mainnet today](https://raw.githubusercontent.com/msanlisavas/casper-llms/main/guides/casper-2.0-docs-vs-mainnet.md) has more detail.

- **Pricing is payment-limited, the mode casper-client 5.0.1 builds with `--pricing-mode classic`**
  ([L135](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L135), [parse.rs](https://github.com/casper-ecosystem/casper-client-rs/blob/v5.0.1/lib/cli/parse.rs#L922-L966)); `--pricing-mode fixed`, which the docs show ([installing-contracts.md](https://github.com/casper-network/docs-redux/blob/c78e3c2040d30fd8c42cb95bc8a3b308db9d1a56/versioned_docs/version-2.0.0/developers/cli/installing-contracts.md?plain=1#L39)), is rejected on mainnet ([meta_transaction_v1.rs](https://github.com/casper-network/casper-node/blob/v2.2.2/node/src/types/transaction/meta_transaction/meta_transaction_v1.rs#L577-L584)).
- **Every Wasm transaction (session code, installs included, or a contract call) must declare a
  payment amount of at least 2.5 CSPR** (2,500,000,000 motes), a floor on the amount declared, not
  on the fee ([L178-L179](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L178-L179), [meta_transaction_v1.rs](https://github.com/casper-network/casper-node/blob/v2.2.2/node/src/types/transaction/meta_transaction/meta_transaction_v1.rs#L568-L570), [deploy.rs](https://github.com/casper-network/casper-node/blob/v2.2.2/types/src/transaction/deploy.rs#L556-L572),
  [internal.rs](https://github.com/casper-network/casper-node/blob/v2.2.2/storage/src/system/handle_payment/internal.rs#L100-L116)); several of the docs' contract calls declare 0.1 CSPR
  ([calling-contracts.md L55](https://github.com/casper-network/docs-redux/blob/c78e3c2040d30fd8c42cb95bc8a3b308db9d1a56/versioned_docs/version-2.0.0/developers/cli/calling-contracts.md?plain=1#L55), [L176](https://github.com/casper-network/docs-redux/blob/c78e3c2040d30fd8c42cb95bc8a3b308db9d1a56/versioned_docs/version-2.0.0/developers/cli/calling-contracts.md?plain=1#L176), [L251](https://github.com/casper-network/docs-redux/blob/c78e3c2040d30fd8c42cb95bc8a3b308db9d1a56/versioned_docs/version-2.0.0/developers/cli/calling-contracts.md?plain=1#L251), [L328](https://github.com/casper-network/docs-redux/blob/c78e3c2040d30fd8c42cb95bc8a3b308db9d1a56/versioned_docs/version-2.0.0/developers/cli/calling-contracts.md?plain=1#L328)).
- **The maximum TTL is 2 hours**, not the docs' 18 ([sending-transactions.md](https://github.com/casper-network/docs-redux/blob/c78e3c2040d30fd8c42cb95bc8a3b308db9d1a56/versioned_docs/version-2.0.0/developers/cli/sending-transactions.md?plain=1#L1366), [L192](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L192)).
- **Addressable entities are disabled on mainnet** (`enable_addressable_entity = false`): state
  holds accounts and contracts, not the `entity-…` records the docs show
  ([querying-global-state.md](https://github.com/casper-network/docs-redux/blob/c78e3c2040d30fd8c42cb95bc8a3b308db9d1a56/versioned_docs/version-2.0.0/developers/cli/querying-global-state.md?plain=1#L89), [L167-L177](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L167-L177)).
- **The minimum validator bid is 500 CSPR**, not the docs' 10,000
  ([bonding.md](https://github.com/casper-network/docs-redux/blob/c78e3c2040d30fd8c42cb95bc8a3b308db9d1a56/versioned_docs/version-2.0.0/operators/becoming-a-validator/bonding.md?plain=1#L13), [L77](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L77)).
- **A top-up to an existing delegation has no minimum**, only the validator's maximum; a first
  delegation must reach the validator's own minimum, which it cannot set below 500 CSPR
  ([detail.rs](https://github.com/casper-network/casper-node/blob/v2.2.2/storage/src/system/auction/detail.rs#L853-L873), [L71-L72](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L71-L72), [auction.rs](https://github.com/casper-network/casper-node/blob/v2.2.2/storage/src/system/auction.rs#L113-L117)). The docs say
  every delegation below 500 CSPR is rejected ([delegating.md](https://github.com/casper-network/docs-redux/blob/c78e3c2040d30fd8c42cb95bc8a3b308db9d1a56/versioned_docs/version-2.0.0/users/delegating.md?plain=1#L103)).
- **Fees are burned, and only a successful Wasm transaction (session code or a contract call)
  gets 75% of its unused payment back**; a failed or native one gets nothing back ([L117-L126](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L117-L126),
  [operations.rs L866-L872](https://github.com/casper-network/casper-node/blob/v2.2.2/node/src/components/contract_runtime/operations.rs#L866-L872),
  [operations.rs L237-L241](https://github.com/casper-network/casper-node/blob/v2.2.2/node/src/components/contract_runtime/operations.rs#L237-L241)).
- **Send `put-transaction` native subcommands (transfer, delegate and the other auction calls) with
  `--standard-payment true`**: with `false` the node does not execute them and still charges at
  least the 2.5 CSPR penalty ([meta_transaction.rs](https://github.com/casper-network/casper-node/blob/v2.2.2/node/src/types/transaction/meta_transaction.rs#L117-L135), [operations.rs](https://github.com/casper-network/casper-node/blob/v2.2.2/node/src/components/contract_runtime/operations.rs#L444-L538),
  [guide](https://raw.githubusercontent.com/msanlisavas/casper-llms/main/guides/casper-client-5.md)).
- **With it, a native auction call such as `delegate` is charged its whole payment amount**: that amount is its
  gas limit and, at mainnet's gas price of 1, its cost ([pricing_mode.rs](https://github.com/casper-network/casper-node/blob/v2.2.2/types/src/transaction/pricing_mode.rs#L142-L171), [L509-L510](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L509-L510)), and the node counts that whole limit as consumed, leaving no unused payment to refund ([operations.rs](https://github.com/casper-network/casper-node/blob/v2.2.2/node/src/components/contract_runtime/operations.rs#L693-L715), [types.rs](https://github.com/casper-network/casper-node/blob/v2.2.2/node/src/components/contract_runtime/types.rs#L188-L191)).
  It must declare at least its entry point's chainspec cost ([meta_transaction_v1.rs](https://github.com/casper-network/casper-node/blob/v2.2.2/node/src/types/transaction/meta_transaction/meta_transaction_v1.rs#L522-L567)), so pay exactly that: 2.5 CSPR for `delegate` ([L448-L465](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L448-L465); [guide section 8](https://raw.githubusercontent.com/msanlisavas/casper-llms/main/guides/casper-2.0-docs-vs-mainnet.md)).
- **With it, a native transfer is charged the 0.1 CSPR transfer cost for any payment amount the node accepts**
  ([L473](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L473), [transaction.rs](https://github.com/casper-network/casper-node/blob/v2.2.2/types/src/transaction.rs#L431-L439), [deploy.rs](https://github.com/casper-network/casper-node/blob/v2.2.2/types/src/transaction/deploy.rs#L1496-L1511)), but the Transaction V1 that `put-transaction transfer`
  builds ([casper-client](https://github.com/casper-ecosystem/casper-client-rs/blob/v5.0.1/lib/cli/transaction.rs#L382-L389)) is rejected if it declares less than 0.1 CSPR ([meta_transaction_v1.rs](https://github.com/casper-network/casper-node/blob/v2.2.2/node/src/types/transaction/meta_transaction/meta_transaction_v1.rs#L499-L521)) or more
  than the 812,500,000,000 `block_gas_limit` ([L197-L198](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L197-L198), [meta_transaction_v1.rs](https://github.com/casper-network/casper-node/blob/v2.2.2/node/src/types/transaction/meta_transaction/meta_transaction_v1.rs#L622-L637)).
- **Rewards: a sustain purse takes 2/8** of them since 2.2
  ([L184](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L184)).
- **The minimum block time is 8 seconds**, not the 2^14 ms (about 16 s) in the docs' sample values
  ([rewards.md](https://github.com/casper-network/docs-redux/blob/c78e3c2040d30fd8c42cb95bc8a3b308db9d1a56/versioned_docs/version-2.0.0/concepts/design/rewards.md?plain=1#L63), [L32](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L32)).
- **A call stack can nest at most 11 contracts**, not the docs' 10, a count that likewise excludes
  the initiating session ([callstack.md](https://github.com/casper-network/docs-redux/blob/c78e3c2040d30fd8c42cb95bc8a3b308db9d1a56/versioned_docs/version-2.0.0/concepts/callstack.md?plain=1#L29)): the chainspec's height limit of 12 ([L69-L70](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L69-L70))
  counts the initiating account's frame ([engine_state/mod.rs](https://github.com/casper-network/casper-node/blob/v2.2.2/execution_engine/src/engine_state/mod.rs#L124-L127), [stack.rs](https://github.com/casper-network/casper-node/blob/v2.2.2/execution_engine/src/runtime/stack.rs#L77-L98)), and each
  contract call adds one, including a call to the Mint, which a contract makes to create a purse or
  move CSPR ([runtime/mod.rs](https://github.com/casper-network/casper-node/blob/v2.2.2/execution_engine/src/runtime/mod.rs#L2027-L2082), [Mint calls](https://github.com/casper-network/casper-node/blob/v2.2.2/execution_engine/src/runtime/mod.rs#L3516-L3559)).

Casper counts amounts in motes: 1 CSPR = 1,000,000,000 motes, which the docs state correctly
([M.md](https://github.com/casper-network/docs-redux/blob/c78e3c2040d30fd8c42cb95bc8a3b308db9d1a56/versioned_docs/version-2.0.0/concepts/glossary/M.md?plain=1#L19)).
What changed release by release since 2.0 is in
[What changed in Casper 2.1 and 2.2](https://raw.githubusercontent.com/msanlisavas/casper-llms/main/guides/casper-2.1-and-2.2.md).

## casper-client

Use casper-client 5.0.1: its release note says moving to casper-types 7.0.0 makes it compatible
with the v2.2.0 protocol, while 5.0.0 still depends on casper-types 6.0.1
([release v5.0.1](https://github.com/casper-ecosystem/casper-client-rs/releases/tag/v5.0.1),
[v5.0.0 Cargo.toml L35](https://github.com/casper-ecosystem/casper-client-rs/blob/v5.0.0/Cargo.toml#L35)).
The docs' tutorials still show 1.x-era `put-deploy` commands
([delegate.md](https://github.com/casper-network/docs-redux/blob/c78e3c2040d30fd8c42cb95bc8a3b308db9d1a56/versioned_docs/version-2.0.0/developers/cli/delegate.md?plain=1#L40-L55)). Read
[casper-client 5.x: sending transactions on Casper 2.x](https://raw.githubusercontent.com/msanlisavas/casper-llms/main/guides/casper-client-5.md) before writing any command. In short:

- Send with `put-transaction` (alias `put-txn`) and its subcommands: `session` takes
  `--wasm-path` and `--install-upgrade`, not the `--transaction-path` and `--category` the docs show.
- Use `classic` pricing and `--gas-price-tolerance 1` with `put-transaction` on mainnet and
  testnet: a node rejects any other tolerance on the Transaction V1 that `put-transaction` builds
  ([meta_transaction_v1.rs](https://github.com/casper-network/casper-node/blob/v2.2.2/node/src/types/transaction/meta_transaction/meta_transaction_v1.rs#L100-L128), [mainnet L509-L510](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L509-L510),
  [testnet L511-L512](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/testnet/chainspec.toml#L511-L512)). Raising the tolerance never fixes an out-of-gas
  failure: under `classic` the gas limit is `--payment-amount`, so raise that
  ([parse.rs](https://github.com/casper-ecosystem/casper-client-rs/blob/v5.0.1/lib/cli/parse.rs#L922-L966), [pricing_mode.rs](https://github.com/casper-network/casper-node/blob/v2.2.2/types/src/transaction/pricing_mode.rs#L142-L144)).
- In 5.0.1, `--transfer-id` makes `put-transaction transfer` panic; when a recipient needs a
  transfer ID, use the legacy `transfer` command.
- Calling a contract by package name is the `package-name` subcommand.
- Key algorithm values are case-sensitive (`Ed25519`, `secp256k1`).

## Where each answer lives

| Question about | Start from |
|---|---|
| Anything, or which tool exists | [The Casper AI hub](https://raw.githubusercontent.com/msanlisavas/casper-llms/main/llms.txt) and its [directory](https://raw.githubusercontent.com/msanlisavas/casper-llms/main/directory.md) |
| Concepts, accounts, staking, economics, node operation | [Casper Network documentation](https://raw.githubusercontent.com/msanlisavas/casper-llms/main/casper-docs/llms.txt) (2.0; check the guides) |
| JSON-RPC methods | The JSON-RPC pages of the [Casper Network documentation](https://raw.githubusercontent.com/msanlisavas/casper-llms/main/casper-docs/llms.txt) (2.0; check the guides); a running sidecar lists its RPC methods and their parameters in answer to `rpc.discover` ([rpc_sidecar README L23-L29](https://github.com/casper-network/casper-sidecar/blob/v2.1.0/rpc_sidecar/README.md?plain=1#L23-L29)) |
| Node, sidecar, release notes since 2.0 | [Casper node, sidecar and command-line client](https://raw.githubusercontent.com/msanlisavas/casper-llms/main/casper-node-tools/llms.txt) |
| SDKs: JavaScript/TypeScript, .NET, Go, Rust, Java, Casper Wallet | [Casper SDKs](https://raw.githubusercontent.com/msanlisavas/casper-llms/main/casper-sdks/llms.txt) |
| Rust smart contracts | [Odra](https://raw.githubusercontent.com/msanlisavas/casper-llms/main/odra/llms.txt); in Claude Code, Odra's own plugin |
| Token and NFT standards | [CEPs](https://raw.githubusercontent.com/msanlisavas/casper-llms/main/casper-ceps/llms.txt) and [standard implementations](https://raw.githubusercontent.com/msanlisavas/casper-llms/main/casper-standards/llms.txt) |
| x402 pay-per-call payments | [x402 on Casper](https://raw.githubusercontent.com/msanlisavas/casper-llms/main/casper-x402/llms.txt) |
| dApp frontends, wallet connection, signing in the browser | [CSPR.click docs](https://docs.cspr.click/llms.txt) |
| Indexed chain data over REST or streaming | [CSPR.cloud docs](https://docs.cspr.cloud/llms.txt) |
| Bridging tokens between Casper and EVM chains (AstralBeam) | [AstralBeam docs](https://docs.astralbeam.io/llms.txt) (a public testnet; no mainnet yet); for its announced launch date, roadmap, audit and testnet playbook, the [AstralBeam guide](https://raw.githubusercontent.com/msanlisavas/casper-llms/main/guides/astralbeam.md), which dates every website claim |
| Decoding a failed or rejected transaction: `User error: N`, `Mint error: N`, auction errors, ApiError exit codes, JSON-RPC rejection codes | [Casper execution errors](https://raw.githubusercontent.com/msanlisavas/casper-llms/main/guides/casper-error-codes.md), which links each code to the source line that defines it |
| Casper Wallet: installing it from the right place, the recovery phrase and password, connecting to dApps, signing requests, Ledger, swap and wrap, scams | [Casper Wallet guide](https://raw.githubusercontent.com/msanlisavas/casper-llms/main/guides/casper-wallet.md), pinned to the extension's v2.8.0 source; for connecting a dApp to a wallet, the CSPR.click docs above |
| Liquid staking (sCSPR), WCSPR, CSPR.trade's contracts and fees, the Styks price oracle, Friendly Market, csprUSD | [Liquid staking and DeFi on Casper](https://raw.githubusercontent.com/msanlisavas/casper-llms/main/guides/casper-liquid-staking-and-defi.md), checked against the contracts' source and mainnet state, with a list of what their READMEs get wrong |
| Validator votes CVV001 to CVV010, how on-chain voting works, the Casper Association's delegation policy, board and published accounts | [Casper governance](https://raw.githubusercontent.com/msanlisavas/casper-llms/main/guides/casper-governance.md): each vote's proposal, published outcome, on-chain tally and effect, dated |

## Live chain data

Use an MCP server for anything about current on-chain state; never answer it from documentation.

| Server | For | Access |
|---|---|---|
| CSPR.cloud MCP, `https://mcp.cspr.cloud/mcp` (testnet: `https://mcp.testnet.cspr.cloud/mcp`) | Accounts, blocks, deploys, validators, contracts, tokens, NFTs | CSPR.cloud API key in `X-CSPR-Cloud-Api-Key` |
| CSPR.trade MCP, `https://mcp.cspr.trade/mcp`, mainnet only ([getting-started.md L13](https://github.com/make-software/cspr-trade-mcp/blob/v0.6.0/docs/getting-started.md?plain=1#L13)); for testnet, self-host `@make-software/cspr-trade-mcp` with `CSPR_TRADE_NETWORK=testnet` ([README L65-L81](https://github.com/make-software/cspr-trade-mcp/blob/v0.6.0/README.md?plain=1#L65-L81)) | DEX prices, quotes, swaps and liquidity; builds unsigned deploys | No key |
| casper-mcp (self-hosted) | 80+ tools over CSPR.cloud; optional write tools that sign locally in stdio mode | Your CSPR.cloud API key |
| CasperAI, `https://casperai.ekolsoft.com/v1/mcp` | Cited answers (`casper_ask`) and casper-client 5.0.1 commands (`casper_command_build`) | `casper_command_build` is free; `casper_ask` needs an API key or x402 |

In Claude Code, `/plugin marketplace add msanlisavas/casper-llms` adds the hub's marketplace, and
`/plugin install <name>@casper-llms` installs one of its plugins: `casper` (this skill), `odra-plugin`
(Odra's own), `cspr-trade`, `cspr-cloud` (needs `CSPR_CLOUD_API_KEY` set in your environment) or
`casperai` (needs `CASPERAI_API_KEY`); the last three connect the servers above
([README](https://raw.githubusercontent.com/msanlisavas/casper-llms/main/README.md), [marketplace.json](https://raw.githubusercontent.com/msanlisavas/casper-llms/main/.claude-plugin/marketplace.json)). casper-mcp is not among them; run its
Docker image as its README shows ([Docker](https://github.com/msanlisavas/casper-mcp/blob/v3.2.0/README.md?plain=1#L24-L34), [client configuration](https://github.com/msanlisavas/casper-mcp/blob/v3.2.0/README.md?plain=1#L94-L108)).
