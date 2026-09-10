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
2. **Cite.** Every index links raw markdown; the URL after the colon on each line is the page to
   send a person to.
3. **Never handle keys.** Do not ask for, accept, print or store a secret key, seed phrase or
   keystore password, and never pass one to a tool: tool arguments go through the model. Give
   commands as text the user runs, with placeholders such as `<PATH-TO-YOUR-SECRET-KEY>`.
4. **Testnet first.** For anything that moves funds, give the testnet form (chain name
   `casper-test`) before mainnet (`casper`).
5. **Say when sources disagree, or do not cover the question,** instead of filling the gap from
   memory. Casper changed substantially in 2.0, and older answers are often wrong.

## Current mainnet facts the docs get wrong

Each value is from the mainnet chainspec at casper-node v2.2.2. The full comparison, with the
doc statements it corrects, is in
[Where the Casper 2.0 docs differ from mainnet today](https://raw.githubusercontent.com/msanlisavas/casper-llms/main/guides/casper-2.0-docs-vs-mainnet.md).

- **Pricing is payment-limited ("classic").** `--pricing-mode fixed`, which the docs show, is
  rejected on mainnet ([chainspec L135](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L135)).
- **A contract call or install must pay at least 2.5 CSPR** (2,500,000,000 motes); the docs'
  examples use 0.1 CSPR ([L178-L179](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L178-L179)).
- **The maximum TTL is 2 hours**, not 18 ([L192](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L192)).
- **Addressable entities are disabled on mainnet** (`enable_addressable_entity = false`): state
  holds accounts and contracts, not the `entity-…` records the docs show
  ([L177](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L177)).
- **The minimum validator bid is 500 CSPR**, not 10,000
  ([L77](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L77));
  the minimum delegation is 500 CSPR ([L72](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L72)).
- **Fees are burned, and a successful transaction gets 75% of its unused payment back**
  ([L117](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L117),
  [L126](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L126)).
- **Rewards: a sustain purse takes 2/8** of them since 2.2
  ([L184](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L184)).
- **The minimum block time is 8 seconds**, not 16
  ([L32](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L32)),
  and **the contract call stack limit is 12**, not 10
  ([L70](https://github.com/casper-network/casper-node/blob/v2.2.2/resources/mainnet/chainspec.toml#L70)).
- **Amounts are in motes:** 1 CSPR = 1,000,000,000 motes.

What changed release by release since 2.0 is in
[What changed in Casper 2.1 and 2.2](https://raw.githubusercontent.com/msanlisavas/casper-llms/main/guides/casper-2.1-and-2.2.md).

## casper-client

Use casper-client 5.x. Tutorials, including the client's own README, still show 1.x
`put-deploy` syntax. Read
[casper-client 5.x: sending transactions on Casper 2.x](https://raw.githubusercontent.com/msanlisavas/casper-llms/main/guides/casper-client-5.md)
before writing any command. In short:

- Send with `put-transaction` (alias `put-txn`) and its subcommands: `session` takes
  `--wasm-path` and `--install-upgrade`, not the `--transaction-path` and `--category` the docs show.
- Use `classic` pricing on mainnet and testnet.
- In 5.0.1, `--transfer-id` makes `put-transaction transfer` panic; when a recipient needs a
  transfer ID, use the legacy `transfer` command.
- Calling a contract by package name is the `package-name` subcommand.
- Key algorithm values are case-sensitive (`Ed25519`, `secp256k1`).

## Where each answer lives

| Question about | Start from |
|---|---|
| Anything, or which tool exists | [The Casper AI hub](https://raw.githubusercontent.com/msanlisavas/casper-llms/main/llms.txt) and its [directory](https://raw.githubusercontent.com/msanlisavas/casper-llms/main/directory.md) |
| Concepts, accounts, staking, economics, node operation | [Casper Network documentation](https://raw.githubusercontent.com/msanlisavas/casper-llms/main/casper-docs/llms.txt) (2.0; check the guides) |
| Node, sidecar, JSON-RPC, release notes since 2.0 | [Casper node, sidecar and command-line client](https://raw.githubusercontent.com/msanlisavas/casper-llms/main/casper-node-tools/llms.txt) |
| SDKs: JavaScript/TypeScript, .NET, Go, Rust, Java, Casper Wallet | [Casper SDKs](https://raw.githubusercontent.com/msanlisavas/casper-llms/main/casper-sdks/llms.txt) |
| Rust smart contracts | [Odra](https://raw.githubusercontent.com/msanlisavas/casper-llms/main/odra/llms.txt); in Claude Code, Odra's own plugin |
| Token and NFT standards | [CEPs](https://raw.githubusercontent.com/msanlisavas/casper-llms/main/casper-ceps/llms.txt) and [standard implementations](https://raw.githubusercontent.com/msanlisavas/casper-llms/main/casper-standards/llms.txt) |
| x402 pay-per-call payments | [x402 on Casper](https://raw.githubusercontent.com/msanlisavas/casper-llms/main/casper-x402/llms.txt) |
| dApp frontends, wallet connection, signing in the browser | [CSPR.click docs](https://docs.cspr.click/llms.txt) |
| Indexed chain data over REST or streaming | [CSPR.cloud docs](https://docs.cspr.cloud/llms.txt) |

## Live chain data

Use an MCP server for anything about current on-chain state; never answer it from documentation.

| Server | For | Access |
|---|---|---|
| CSPR.cloud MCP, `https://mcp.cspr.cloud/mcp` (testnet: `https://mcp.testnet.cspr.cloud/mcp`) | Accounts, blocks, deploys, validators, contracts, tokens, NFTs | CSPR.cloud API key in `X-CSPR-Cloud-Api-Key` |
| CSPR.trade MCP, `https://mcp.cspr.trade/mcp` | DEX prices, quotes, swaps and liquidity; builds unsigned deploys | No key |
| casper-mcp (self-hosted) | 80+ tools over CSPR.cloud; optional write tools that sign locally in stdio mode | Your CSPR.cloud API key |
| CasperAI, `https://casperai.ekolsoft.com/v1/mcp` | Cited answers (`casper_ask`) and casper-client 5.0.1 commands (`casper_command_build`) | `casper_command_build` is free; `casper_ask` needs an API key or x402 |

The hub's plugin marketplace installs these in Claude Code:
`/plugin marketplace add msanlisavas/casper-llms`.
