# AstralBeam, the Casper-EVM bridge: launch status, roadmap, audit and public testnet

Verified against astralbeam.io shell-0d177dc86bed, testnet.astralbeam.io shell-624443a40eb2 and docs.astralbeam.io 2026.09.21 on 2026-09-23.

AstralBeam is a bridge between the Casper Network and EVM chains. Its testnet app describes it as "a bidirectional bridge between Casper Network and EVM chains, enabling ERC-20 token transfers to and from CEP-18 tokens using M-of-N multi-signature attestation" ([testnet app, How beaming works](https://testnet.astralbeam.io/assets/index-D6E7VKGw.js)), and its documentation adds the other direction: "For Casper-origin wCSPR and sCSPR, the CEP-18 token is locked on Casper and its wrapper minted on EVM" ([docs.astralbeam.io: Supported Tokens](https://docs.astralbeam.io/using-astralbeam/supported-tokens)). How the bridge works — contracts, relayers, verification, the public API, supported networks and tokens, fees, tracking and troubleshooting — is documented at [docs.astralbeam.io](https://docs.astralbeam.io/), which publishes an [llms.txt index](https://docs.astralbeam.io/llms.txt) of 46 markdown pages (fetched 2026-09-23). Answer those questions from the documentation. This guide covers what it does not: the launch date, roadmap, compliance claims and audit claims on the marketing site [astralbeam.io](https://astralbeam.io/), the site's public-testnet playbook, what the testnet app tells its users, and where the site, the app, the documentation and the audit report disagree. Both sites credit "MAKE Technology LLC" in their footer and link "Powered by MAKE" to `https://make.services/` ([site bundle](https://astralbeam.io/assets/index-DSzftkm_.js), [testnet app footer](https://testnet.astralbeam.io/assets/BeamTopBar-DjAXEuhj.js)). The documentation names no company; its repository links point at the `make-software` GitHub organisation ([docs.astralbeam.io: Local Development](https://docs.astralbeam.io/for-developers/local-development)).

Four kinds of source appear below, and they are not equally durable. The two websites are single-page applications, read on **2026-09-23**: astralbeam.io answers every path with one 2,537-byte HTML shell (`/testnet-playbook` has its own 2,684-byte copy with a different title and description), and all of its visible text is in one JavaScript file named after a hash of its content, `https://astralbeam.io/assets/index-DSzftkm_.js` (802,843 bytes); testnet.astralbeam.io works the same way, with content-hashed files for each page. Those file names change on the operator's next deploy, and an old file name does not return 404: on 2026-09-23 both hosts answered a request for a missing `/assets/` file with HTTP 200 and the current HTML shell. The documentation pages were fetched on 2026-09-23, when the newest page edit in the [docs sitemap](https://docs.astralbeam.io/sitemap-pages.xml) was dated 2026-09-21. The audit report is a PDF that astralbeam.io serves under a fixed name, so it can be replaced without its URL changing. Live testnet API responses were read on 2026-09-23 at about 14:38 UTC and can change at any time. The SHA-256 of every file quoted is under *Sources*. This repository's weekly check follows the two sites' HTML shells and the documentation's newest edit date; it does not follow the PDF or the API.

A launch date, a roadmap item or a token described below is the website's statement on the date given. None of them is a fact about what will happen, and none should be repeated without its source and date.

## AstralBeam launch status: a public testnet, with mainnet announced for October 2026

- **What the website says.** On 2026-09-23 the meta description of [astralbeam.io](https://astralbeam.io/) read "Instant finality, ERC-3643 compliance rails, Halborn audited. Public testnet live — mainnet October 2026." The home page's opening paragraph ends "Public Testnet is live — Mainnet launches this October.", and its testnet section says "shape AstralBeam before mainnet launches in October." ([site bundle](https://astralbeam.io/assets/index-DSzftkm_.js)).

- **The roadmap entry.** The site's roadmap dates "Mainnet launch" to "October 2026" with the text "Real assets, real value. AstralBeam goes live on mainnet with full bidirectional bridging across all supported chains." Of its six items, only "Public testnet launch" (September 2026) carries the page's live marker, `live:!0` in the bundle ([site bundle](https://astralbeam.io/assets/index-DSzftkm_.js)).

- **The documentation gives no date.** It says "Mainnet launch is planned following thorough testnet validation and security audits." ([docs.astralbeam.io: Introduction](https://docs.astralbeam.io/)), "Mainnet launch is coming soon, following testnet validation and security audits." ([Supported Networks](https://docs.astralbeam.io/using-astralbeam/supported-networks)) and "Mainnet is not available in this public-testnet deployment." ([Contracts](https://docs.astralbeam.io/smart-contracts/contracts)). On 2026-09-23 the words "October", "Q4" and "roadmap" appeared on none of the 46 pages its [llms.txt](https://docs.astralbeam.io/llms.txt) lists.

- **No mainnet contract has been published.** The documentation lists public-testnet addresses only ([Contracts](https://docs.astralbeam.io/smart-contracts/contracts)). The testnet app's compiled table of EVM locker addresses holds the zero address `0x0000000000000000000000000000000000000000` for chain IDs 1, 8453, 137, 42161 and 56 and has no entry for 4663; its testnet entries do not match the testnet locker the documentation and the live API give, so the table is not a deployment record ([testnet app entry file](https://testnet.astralbeam.io/assets/index-vwphA1W3.js), read 2026-09-23).

- **How to state it.** The website said on 2026-09-23 that mainnet launches in October 2026; the documentation names no date; no mainnet contract address has been published. Do not give a day, and do not present October 2026 as a fact.

## AstralBeam networks: named on the website, running on the testnet

- **The website** says "AstralBeam connects Casper with Ethereum, Base, Polygon, and Robinhood Chain." ([site bundle](https://astralbeam.io/assets/index-DSzftkm_.js), 2026-09-23).

- **The testnet.** On 2026-09-23 `https://api.testnet.astralbeam.io/api/v1/chains` returned six EVM chains. Four had `"isEnabled": true`: Ethereum Sepolia (11155111, the only one with `"isPrimary": true`), Base Sepolia (84532), Polygon Amoy (80002) and Robinhood Testnet (46630), each with `"lockerAddress": "0x06d4eF8d1b2969aA8713F3748D8304AafDC4d5d7"`. Two had `"isEnabled": false` and `"lockerAddress": null`: Arbitrum Sepolia (421614) and BNB Smart Chain Testnet (97). The documentation lists the same four as active, and lists Arbitrum Sepolia, BNB Smart Chain Testnet and Robinhood Chain (4663) under "Coming Soon" ([Supported Networks](https://docs.astralbeam.io/using-astralbeam/supported-networks)).

- **Mainnet networks.** Nobody has published a list. The roadmap promises "full bidirectional bridging across all supported chains" without naming them ([site bundle](https://astralbeam.io/assets/index-DSzftkm_.js)). The documentation says of Robinhood Chain "Mainnet (chain ID `4663`) support is planned." ([Glossary](https://docs.astralbeam.io/reference/glossary)). The testnet app's code maps the mainnet chain IDs of Ethereum (1), Base (8453), Polygon (137), Arbitrum (42161), BNB Smart Chain (56) and Robinhood Chain (4663) ([testnet app entry file](https://testnet.astralbeam.io/assets/index-vwphA1W3.js)); that is a table in code, not an announcement.

## AstralBeam tokenized stocks and sCSPR: website claims and the testnet catalog

- **The website's claim.** A card headed "Tokenized stocks, unlocked" reads "Beam tokenized stocks and real-world assets between Robinhood Chain, Base, and Casper — then put them to work in DeFi strategies: collateral, vaults, and yield beyond the walled garden." ([site bundle](https://astralbeam.io/assets/index-DSzftkm_.js), 2026-09-23).

- **The testnet catalog.** On 2026-09-23 the stock tokens AMD, AMZN, NFLX, PLTR and TSLA had an EVM address on `robinhood-testnet` only, and none on Base Sepolia, both in the documentation's catalog ([Supported Tokens](https://docs.astralbeam.io/using-astralbeam/supported-tokens)) and in `https://api.testnet.astralbeam.io/api/v1/tokens`. The app's Faucet page says of them: "They're test tokens, not real shares." ([testnet app, Faucet](https://testnet.astralbeam.io/assets/index-COLtLEBg.js)).

- **sCSPR.** The live API names it "Wrapped Staked CSPR" and gives it `"originChain": "casper"` (`/api/v1/tokens`, 2026-09-23). The documentation lists it as a Casper-origin token with 9 decimals and never says what it is ([Supported Tokens](https://docs.astralbeam.io/using-astralbeam/supported-tokens)). The site's roadmap mentions it under AstralYield: "convert into sCSPR, and earn 10%+ yield through liquid staking" ([site bundle](https://astralbeam.io/assets/index-DSzftkm_.js)). The testnet playbook gets it by swapping CSPR on testnet.cspr.trade (step 9 below). None of AstralBeam's own sources says who issues sCSPR or how its staking works.

## AstralBeam roadmap as published on 2026-09-23

The roadmap on [astralbeam.io](https://astralbeam.io/), headed "The path of the beam.", lists six items. The text below is verbatim from the [site bundle](https://astralbeam.io/assets/index-DSzftkm_.js):

| When | Item | The site's text |
| --- | --- | --- |
| September 2026 | Public testnet launch | "AstralBeam opens to everyone. Beam test assets between Casper, Ethereum, Base, Polygon, and Robinhood Chain — and help us battle-test the rails before mainnet." |
| October 2026 | Mainnet launch | "Real assets, real value. AstralBeam goes live on mainnet with full bidirectional bridging across all supported chains." |
| Q4 2026 | T-REX Ledger integration | "Native connectivity with T-REX Ledger via ERC-7786 cross-chain messaging — extending ERC-3643 compliant tokenized assets across every chain AstralBeam touches." |
| Q4 2026 | AstralIntents | "Our intent framework: declare the outcome you want — the destination, the asset, the yield — and let AstralBeam solve the route across chains for you." |
| Q1 2027 | AstralYield | "Put idle assets to work. Bring ETH over to Casper, convert into sCSPR, and earn 10%+ yield through liquid staking — then bridge back to your origin chain, or stake, leverage, and deploy sCSPR in DeFi while it keeps yielding." |
| Q1 2027 | AstralToken TGE | "The AstralBeam token generation event — aligning the community, the protocol, and the beam." |

- Only the first item carries the page's live marker ([site bundle](https://astralbeam.io/assets/index-DSzftkm_.js)). The other five are plans the website states.

- None of the six appears in the documentation: on 2026-09-23 "TGE", "token generation", "tokenomics", "airdrop", "AstralToken", "AstralIntents", "AstralYield", "yield" and "staking" had no match on any of the 46 pages its [llms.txt](https://docs.astralbeam.io/llms.txt) lists, and "intent" matched only the word "intentionally".

- **The token generation event.** The roadmap row above is everything AstralBeam had published about a token on 2026-09-23. Its title is "AstralToken TGE"; nothing says whether "AstralToken" is the token's name. No ticker, supply, allocation, price, chain, eligibility rule, airdrop or date more precise than "Q1 2027" appears on the site, in the testnet app or in the documentation.

- **"10%+ yield".** The site gives no source, calculation or provider for the figure ([site bundle](https://astralbeam.io/assets/index-DSzftkm_.js)).

## AstralBeam compliance claims: ERC-3643, T-REX Ledger and ERC-7786

- **What the website says**, all read on 2026-09-23 from the [site bundle](https://astralbeam.io/assets/index-DSzftkm_.js) unless noted. The meta description of [astralbeam.io](https://astralbeam.io/) says "ERC-3643 compliance rails". The home page's opening paragraph says "More than a conventional bridge, it transports both value and the compliance frameworks that govern it." Its "Why AstralBeam" section opens "Conventional bridges move value but leave compliance data behind. AstralBeam is built on rails designed for finality, continuous compliance, and institutional-grade security."

- **The "Dual-layer RWA infrastructure" card** reads, in the present tense: "AstralBeam carries a second layer of information alongside the asset itself. Using the ERC-7786 messaging standard, it synchronizes with the T-REX Ledger, ensuring ERC-3643 regulated assets maintain their legal and compliance frameworks across every chain they enter." The words "ERC-3643" link to `https://www.erc3643.org/`, the only outside source the site gives for any of this. The shell's social-preview image is described as "AstralBeam T-REX hub connected to five blockchain nodes" (`og:image:alt`, [astralbeam.io](https://astralbeam.io/)).

- **The site contradicts itself on timing.** The card describes the T-REX Ledger link as working now; the roadmap lists "T-REX Ledger integration" as a Q4 2026 item ([site bundle](https://astralbeam.io/assets/index-DSzftkm_.js)).

- **Nothing else AstralBeam publishes mentions it.** On 2026-09-23 "ERC-3643", "T-REX", "ERC-7786", "compliance", "KYC", "real-world" and "tokeniz" had no match on any of the 46 documentation pages ([llms.txt](https://docs.astralbeam.io/llms.txt)). The testnet app's JavaScript contains none of "ERC-3643", "T-REX" or "ERC-7786"; the only "T-REX" on testnet.astralbeam.io is the same image description in its HTML shell ([testnet.astralbeam.io](https://testnet.astralbeam.io/)).

- **How to state it.** These are the website's descriptions of a feature and of a Q4 2026 plan. As of 2026-09-23 AstralBeam had published no technical documentation, contract, specification or partner statement behind them.

## AstralBeam audit: what the website, the documentation and the report say

The website and the documentation disagree about the audit, and the website says one thing the report does not.

### What the website says (read 2026-09-23)

- A card headed "Audited by Halborn" reads: "AstralBeam completed a rigorous multi-round security audit by Halborn — 100% of findings addressed, zero critical or high issues open — after six months of continuous testnet operation." Its link, "Read the audit report →", points at the PDF the site hosts, `https://astralbeam.io/audit/halborn-cspr-evm-bridge-ssc.pdf` ([site bundle](https://astralbeam.io/assets/index-DSzftkm_.js)).

- The meta description says "Halborn audited" ([astralbeam.io](https://astralbeam.io/)). The footer's "Audit report" link points at `https://www.halborn.com/audits/casper-association/cspr--evm-bridge-00390b` ([site bundle](https://astralbeam.io/assets/index-DSzftkm_.js)); that page answered HTTP 429 to this guide's requests on 2026-09-23 and was not read.

### What the documentation says (fetched 2026-09-23)

- The Audits page, last edited 2026-08-11 according to the [docs sitemap](https://docs.astralbeam.io/sitemap-pages.xml), has one row: "Bridge Security Audit", auditor Halborn, status "Remediation review in progress", report "Link will be published upon completion". It also says "AstralBeam's contracts and off-chain infrastructure undergo independent third-party security review before any mainnet deployment." ([docs.astralbeam.io: Audits](https://docs.astralbeam.io/security/audits)).

- The FAQ says "The bridge contracts have undergone security review." and lists "Smart contract security (audited code)" ([FAQ](https://docs.astralbeam.io/using-astralbeam/faq)).

- So on 2026-09-23 the website called the audit completed and published the report, while the documentation's Audits page still said remediation review was in progress and gave no link to a report.

### What the report says (the PDF, read 2026-09-23)

- **Who and what.** The cover reads "Assurance Assessment", "Feb 16, 2026 - Mar 20, 2026", "CSPR <> EVM Bridge" and "Casper Association" ([report, p. 1](https://astralbeam.io/audit/halborn-cspr-evm-bridge-ssc.pdf#page=1)). It assessed the repository `cspr-bridge` at commit `618f580acfa0f7eaeb357200a04167e8fe414a0e` ([p. 2](https://astralbeam.io/audit/halborn-cspr-evm-bridge-ssc.pdf#page=2), [p. 11](https://astralbeam.io/audit/halborn-cspr-evm-bridge-ssc.pdf#page=11)). Its text never uses the name AstralBeam. That `cspr-bridge` is AstralBeam's code rests on two other sources: the documentation's Build identity page links a release protocol in `make-software/cspr-bridge` ([Build identity](https://docs.astralbeam.io/api-reference/api-reference/api-version)), and the testnet app's source cites "cspr-bridge cli/src/workers/evm2casper.ts" ([bridgeService.ts in the app's source map](https://testnet.astralbeam.io/assets/index-vwphA1W3.js.map)).

- **Scope.** "The assessment covered both on-chain contracts (Solidity on EVM chains and Rust on Casper) and the off-chain bridge infrastructure (relayer/CLI, P2P coordination, API/indexers, and the MySQL-backed persistence layer)." ([p. 2](https://astralbeam.io/audit/halborn-cspr-evm-bridge-ssc.pdf#page=2)).

- **Findings.** 116 in total: Critical 0; High 2, both solved; Medium 17 (15 solved, 2 risk accepted); Low 63 (61 solved, 2 risk accepted); Informational 34 (30 solved, 3 acknowledged, 1 risk accepted). Totals: 108 solved, 5 risk accepted, 3 acknowledged. The page's headline is "100% OF ALL REPORTED FINDINGS HAVE BEEN ADDRESSED" ([p. 2](https://astralbeam.io/audit/halborn-cspr-evm-bridge-ssc.pdf#page=2)).

- **Remediation.** "Halborn re-reviewed all 116 findings against origin/master across three passes", the second at a revision the report marks 2026-08-06 and the third at one it marks 2026-08-07, and reports "Live finding state: 108 Solved; 5 Risk Accepted; 3 Acknowledged. No finding remains partially remediated." ([p. 7](https://astralbeam.io/audit/halborn-cspr-evm-bridge-ssc.pdf#page=7)).

- **The five accepted risks**, in the report's words: HAL-004 and HAL-010 "no on-chain refund, expiry, or user cancellation; recovery is operator mediated"; HAL-034 "signing key held as a process-lifetime string with no remote signer or zeroization"; HAL-062 "duplicate submission under partition remains reachable but is bounded to gas by the on-chain processed-event guards"; HAL-100 "casperStateRoot remains a zero placeholder, with safety resting on the threshold attestation model". The acknowledged three are HAL-088, HAL-094 and HAL-103 ([p. 7](https://astralbeam.io/audit/halborn-cspr-evm-bridge-ssc.pdf#page=7), [p. 8](https://astralbeam.io/audit/halborn-cspr-evm-bridge-ssc.pdf#page=8)).

- **A disclosed incident.** "Post-report disclosure (2026-08-06): the client disclosed a shared AWS IAM policy/instance profile that had briefly let any single compromised host (including the API host and the WireGuard concentrator) read all relayer signing keys, narrowing the M-of-N threshold that HAL-100's risk acceptance relies on toward 1-of-N for the period it existed." The report adds that it "has since been remediated with one IAM role/instance profile per host and a verified, re-runnable isolation probe" and that it was "not visible from source and outside this engagement's review scope" ([p. 8](https://astralbeam.io/audit/halborn-cspr-evm-bridge-ssc.pdf#page=8)).

- **What it did not review.** "code introduced after the remediation rounds was not part of the original assessment and merits separate review, specifically the EVM WebSocket log listener added for fast chains, the Arbitrum Orbit chain onboarding with its CREATE2 deployment path and schema migrations, the codified security group definitions, and the Helm/Kubernetes deployment surface" ([p. 8](https://astralbeam.io/audit/halborn-cspr-evm-bridge-ssc.pdf#page=8)). The documentation calls Robinhood Chain "An Arbitrum Orbit EVM L2" ([Glossary](https://docs.astralbeam.io/reference/glossary)); read together, the two sources suggest the code that onboards the Robinhood Chain route is in the unreviewed part. That is an inference, not a statement either source makes.

### The website's audit claim, checked against the report

- "100% of findings addressed" repeats the report's headline, and the report counts 5 risk-accepted and 3 acknowledged findings among those addressed ([p. 2](https://astralbeam.io/audit/halborn-cspr-evm-bridge-ssc.pdf#page=2)).

- "zero critical or high issues open" matches: 0 critical, and both high findings solved ([p. 2](https://astralbeam.io/audit/halborn-cspr-evm-bridge-ssc.pdf#page=2)).

- "multi-round" matches the initial remediation review and two further passes ([p. 7](https://astralbeam.io/audit/halborn-cspr-evm-bridge-ssc.pdf#page=7)).

- "after six months of continuous testnet operation" is not in the report. Its only "six months" is the closing disclaimer: "Halborn strongly recommends conducting a follow-up assessment of the project either within six months or immediately following any material changes to the codebase, whichever comes first." ([p. 172](https://astralbeam.io/audit/halborn-cspr-evm-bridge-ssc.pdf#page=172)). The report's engagement ran from Feb 16 to Mar 20, 2026, and the site's own roadmap dates the public testnet launch to September 2026 ([site bundle](https://astralbeam.io/assets/index-DSzftkm_.js)).

- **How to answer "Is AstralBeam audited?"** Not with a flat yes. Halborn assessed the bridge code (`cspr-bridge`, commit `618f580`) for Casper Association between Feb 16 and Mar 20, 2026, found 0 critical and 2 high issues, and re-reviewed the fixes in three passes, the last marked 2026-08-07, leaving 5 findings risk-accepted and 3 acknowledged. The website calls the audit completed; on 2026-09-23 the documentation still said remediation review was in progress; the report names code added after remediation as unreviewed.

## AstralBeam public testnet playbook

The playbook is at [astralbeam.io/testnet-playbook](https://astralbeam.io/testnet-playbook). Its introduction reads "Test AstralBeam by beaming assets between Casper and EVM networks. This playbook walks you through connecting your wallets, getting Testnet assets, completing your first beam, and sharing feedback with the team." and it adds "Before you start: You’ll need Casper Wallet and an EVM-compatible wallet. All transactions in this playbook take place on Testnet and use Testnet assets with no real-world value." ([site bundle](https://astralbeam.io/assets/index-DSzftkm_.js), read 2026-09-23). The fourteen steps below are the playbook's own text, verbatim from the same bundle and grouped under its four headings.

**Connect your wallets (steps 1–5)**

1. Install Casper Wallet: https://www.casperwallet.io/

2. Go to the AstralBeam Testnet instance: https://testnet.astralbeam.io/

3. Click the "Connect Casper" button at the top right and follow the prompts.

4. Click the "EVM - Tap to connect" button and follow the prompts to connect your EVM account.

5. Make sure you see both of your accounts (Casper and EVM) connected on the screen.

**Get Testnet assets (steps 6–9)**

6. Visit the "Faucet" page by clicking the navigation item at the top of the page, and get Testnet tokens from their corresponding faucet pages.

7. Go back to the "Beam" page by clicking the navigation item at the top.

8. Make sure you have Casper as FROM and Ethereum Sepolia as TO network by using the switcher button in the middle if needed.

9. Go to https://testnet.cspr.trade and swap a random amount of CSPR to sCSPR, making sure that you have enough CSPR left for the rest of the operations.

**Make your first beam (steps 10–11)**

10. Go back to the AstralBeam tab, select sCSPR from the "Select a token" dropdown, enter a suitable value in the amount box, then click the "Beam It" button, and follow the prompts.

11. Wait until the beaming is complete. Then click the "Done" button, go to the "Activity" tab, and see your completed activity on the list.

**Explore & give feedback (steps 12–14)**

12. Check out the AstralBeam Guide (https://testnet.astralbeam.io/how-it-works) to get more info and see what you can do with it.

13. Continue beaming assets in both directions to explore and test AstralBeam.

14. Fill out the feedback form and help us improve AstralBeam: AstralBeam Public Testnet Feedback Form — the form's title links to `https://docs.google.com/forms/d/e/1FAIpQLSf3pi5e7gH5sQkxCpmpryk2pMud0vszZx1L0LelMpA7GAXsng/viewform` ([site bundle](https://astralbeam.io/assets/index-DSzftkm_.js)).

What the playbook leaves implicit:

- The first beam sends a Casper-origin token, sCSPR, from Casper to Ethereum Sepolia, so it locks sCSPR on Casper and mints a wrapped token on Sepolia ([Supported Tokens](https://docs.astralbeam.io/using-astralbeam/supported-tokens)). The app's "How beaming works" page, which step 12 points to, describes only EVM-origin tokens (lock and mint from an EVM chain, burn and unlock back) and never names sCSPR or wCSPR ([testnet app, How beaming works](https://testnet.astralbeam.io/assets/index-D6E7VKGw.js)).

- The app's Faucet page lists no source of sCSPR or wCSPR ([testnet app, Faucet](https://testnet.astralbeam.io/assets/index-COLtLEBg.js)), which is why step 9 swaps for sCSPR.

- The Casper-side bridge fee was 50 CSPR on 2026-09-23 (next section), so the CSPR left after step 9 has to cover that fee as well as gas.

## AstralBeam testnet app: what it tells users that the documentation does not

### Transfer times: four answers, and the formula the app uses

| Where (read 2026-09-23) | EVM to Casper | Casper to EVM |
| --- | --- | --- |
| Beam page footnote ([app](https://testnet.astralbeam.io/assets/index-l6sAAYo3.js)) | "between 3–45 minutes, depending on the source network" | "under a minute" |
| How beaming works page ([app](https://testnet.astralbeam.io/assets/index-D6E7VKGw.js)) | "~15 minutes (finality)" | "in seconds" |
| Quick Start ([docs](https://docs.astralbeam.io/getting-started/user-guide)) | "~15-20 minutes" | "~1-3 minutes" |
| FAQ ([docs](https://docs.astralbeam.io/using-astralbeam/faq)) | "~13 minutes on Ethereum, much faster on L2 networks" | "~30-60 seconds" |

- The Beam page computes its own estimate per source chain with `` an=64,F=(e,t)=>{if(t)return"< 1 minute";if(!e)return"~14 minutes";const n=Math.max(an,e.confirmations);return`~${Math.ceil(1.5+n*e.blockTime/60)} minutes`} `` ([testnet app entry file](https://testnet.astralbeam.io/assets/index-vwphA1W3.js)). The source behind it explains the 64: "The relayer enforces a global confirmation-depth floor before attesting … FINALITY_CONFIRMATIONS defaults to 64 in the relayer env" ([bridgeService.ts in the app's source map](https://testnet.astralbeam.io/assets/index-vwphA1W3.js.map)).

- With the confirmations and block times `/api/v1/chains` returned on 2026-09-23 (Ethereum Sepolia 6 and 12 s, Base Sepolia 6 and 2 s, Polygon Amoy 32 and 2 s, Robinhood Testnet 6000 and 0.4 s), that formula gives about 15 minutes from Ethereum Sepolia, about 4 from Base Sepolia or Polygon Amoy, and about 42 from Robinhood Chain Testnet. That arithmetic is this guide's, from the app's code and the API's data.

- The documentation's own advice is "Use the selected route's estimate in the interface, not a fixed promise. Casper source finality does not eliminate the destination wait." ([Supported Networks](https://docs.astralbeam.io/using-astralbeam/supported-networks)).

### Fees and gas on a Casper-to-EVM beam

- On 2026-09-23 `https://api.testnet.astralbeam.io/api/v1/stats/bridge-fee` returned `"casper": {"feeMotes": "50000000000", "feeCspr": 50}` and an EVM fee of `"feeWei": "100000000000000"` on each of the four chains, denominated in ETH on Sepolia, Base Sepolia and Robinhood Testnet and in MATIC on Polygon Amoy.

- The Beam page shows the Casper-side gas as a fixed "~15 CSPR" and, when the fee cannot be paid, tells the user "Please ensure you have at least 50 CSPR to cover the bridge fee." (error 60035, `InsufficientBridgeFee`) ([testnet app, Beam page](https://testnet.astralbeam.io/assets/index-l6sAAYo3.js)).

- The documentation's FAQ lists "Casper to EVM: 50 CSPR" ([FAQ](https://docs.astralbeam.io/using-astralbeam/faq)), but its Bridging Casper to EVM page lists only "Casper Burn Gas" at "~2.5 CSPR" and no bridge fee ([Bridging Casper to EVM](https://docs.astralbeam.io/using-astralbeam/bridging-casper-to-evm)).

### Who pays gas on the destination chain

- The app says the user does not: "Gas: you pay gas on the source chain only — relayers cover the destination, included in the bridge operation." ([How beaming works](https://testnet.astralbeam.io/assets/index-D6E7VKGw.js)), and "Relayers handle the destination transaction — you don't need destination gas just to receive a beam. You'll need it if you send tokens onward or beam back." ([Faucet](https://testnet.astralbeam.io/assets/index-COLtLEBg.js)).

- The documentation's Quick Start agrees ("Relayers pay destination chain gas", [Quick Start](https://docs.astralbeam.io/getting-started/user-guide)); its FAQ does not, listing "Gas fees - Transaction costs on source and destination chains" ([FAQ](https://docs.astralbeam.io/using-astralbeam/faq)).

### Faucets for every enabled testnet

The documentation's faucet page covers two networks: "you'll need testnet tokens on both Ethereum Sepolia and Casper Testnet" ([Getting Testnet Tokens](https://docs.astralbeam.io/using-astralbeam/getting-testnet-tokens)). The app's Faucet page lists these, read 2026-09-23 ([testnet app, Faucet](https://testnet.astralbeam.io/assets/index-COLtLEBg.js)):

- Gas: Ethereum Sepolia ETH at `https://www.alchemy.com/faucets/ethereum-sepolia`; Casper Testnet CSPR at `https://testnet.cspr.live/tools/faucet` ("The faucet allows one request per account."); Base Sepolia ETH at `https://faucets.chain.link/base-sepolia`; Polygon Amoy POL at `https://faucets.chain.link/polygon-amoy`; Robinhood Chain Testnet ETH at `https://faucet.testnet.chain.robinhood.com/` ("claims are limited to once every 24 hours").

- Assets: USDC at `https://faucet.circle.com/`; LINK at `https://faucets.chain.link/`; WETH by wrapping ETH on the source network; the test stock tokens AMZN, AMD, NFLX, PLTR and TSLA from the Robinhood Chain Testnet faucet. The page warns: "Faucet availability doesn't guarantee a beamable route — check LINK in AstralBeam's asset picker for your selected network before requesting."

### Leftover names: "CSPR Bridge" and dev.astralbeam.io

- The app introduces itself to wallets as "CSPR Bridge": the runtime config sets `cspr_click_app_name: 'CSPR Bridge'` ([runtime config](https://testnet.astralbeam.io/config.6b682550.js)), and the EVM wallet connection is configured with `appName` "CSPR Bridge", `appDescription` "Multi-chain Casper Bridge" and a fallback URL `https://csprbridge.com` ([testnet app entry file](https://testnet.astralbeam.io/assets/index-vwphA1W3.js)). On 2026-09-23 `https://csprbridge.com` answered HTTP 301 with `Location: https://astralbeam.io/`.

- The app's HTML shell gives `https://dev.astralbeam.io/` as its `og:url` ([testnet.astralbeam.io](https://testnet.astralbeam.io/)); that address answered HTTP 410 on 2026-09-23.

- The app's Terms of Service page is MAKE Technology, LLC's general terms, "Date of Last Revision: July 15, 2025", covering "CSPR.live, CasperWallet.io, CSPR.studio, CSPR.market, CSPR.name, CSPR.cloud, CSPR.trade, and CSPR.click"; "AstralBeam" appears only in the page title and "bridge" not at all ([testnet app, Terms of Service](https://testnet.astralbeam.io/assets/index-CKtGcGDG.js)).

- On 2026-09-23 the app footer showed "AstralBeam Client: v0.2.1 (7d5c208)", built into the footer file as version `0.2.1` and source `7d5c2085d7aa71bab959c056756d4ec9679ce43e` ([testnet app footer](https://testnet.astralbeam.io/assets/BeamTopBar-DjAXEuhj.js)), and `https://api.testnet.astralbeam.io/api/v1/version` returned `{"component":"api","version":"0.5.0","sourceSha":"d7a15295088d2399be0eefae3a12b50e6d7ca0bf"}`.

## AstralBeam links (checked 2026-09-23)

- Website: [astralbeam.io](https://astralbeam.io/). Public testnet playbook: [astralbeam.io/testnet-playbook](https://astralbeam.io/testnet-playbook).

- Testnet app: [testnet.astralbeam.io](https://testnet.astralbeam.io/), with the pages Beam (`/`), Activity (`/transactions`), Status (`/status`), Faucet (`/faucet`) and How beaming works (`/how-it-works`) ([testnet app entry file](https://testnet.astralbeam.io/assets/index-vwphA1W3.js)).

- Documentation: [docs.astralbeam.io](https://docs.astralbeam.io/), and its [llms.txt](https://docs.astralbeam.io/llms.txt) index (46 pages on 2026-09-23). Appending `.md` to a page's URL returns it as markdown, which is the form the llms.txt links.

- Documentation MCP server: `https://docs.astralbeam.io/~gitbook/mcp`. On 2026-09-23 it answered an MCP `initialize` POST, with no key, as "AstralBeam MCP Server" version 0.27.2, and listed four tools: `searchDocumentation`, `getPage`, `askQuestion` and `sendFeedback`. Its tools search and answer from the documentation, so they carry the documentation's audit and fee wording described above.

- Public testnet API: `https://api.testnet.astralbeam.io/api/v1`, documented in [API Overview](https://docs.astralbeam.io/api-reference/api-reference), which says "The public API does not require authentication."

- Audit report: `https://astralbeam.io/audit/halborn-cspr-evm-bridge-ssc.pdf`; Halborn's page: `https://www.halborn.com/audits/casper-association/cspr--evm-bridge-00390b` (not read; HTTP 429).

- Community, from the site footer ([site bundle](https://astralbeam.io/assets/index-DSzftkm_.js)): X `https://x.com/AstralBeam_io`, Telegram `https://t.me/astralbeam_io`, and a link labelled "24/7 support" to `https://t.me/CSPRhub`. The documentation gives `support@astralbeam.io` ([FAQ](https://docs.astralbeam.io/using-astralbeam/faq)) and, for security reports, `security@astralbeam.io` ([Audits](https://docs.astralbeam.io/security/audits)).

- **Not the same thing:** astralbeam.ai. The GitHub repository `AstralBeamAI/astralbeam` describes itself as "The agentic chat widget for your app" with the homepage `https://www.astralbeam.ai` (GitHub API, 2026-09-23). Nothing read for this guide connects it to the bridge.

## Corrections: AstralBeam pages that are out of date

As of 2026-09-23, four statements in the AstralBeam documentation are contradicted by AstralBeam's own sites or by what they link to.

1. **The audit is "in progress".** [Audits](https://docs.astralbeam.io/security/audits) says "Remediation review in progress" and "Link will be published upon completion". The report is published at `https://astralbeam.io/audit/halborn-cspr-evm-bridge-ssc.pdf`, and its remediation review ended with a third pass at a revision the report marks 2026-08-07 ([report, p. 7](https://astralbeam.io/audit/halborn-cspr-evm-bridge-ssc.pdf#page=7)).

2. **The bridge is at astralbeam.io.** The Quick Start says "Navigate to astralbeam.io in your browser." ([Quick Start](https://docs.astralbeam.io/getting-started/user-guide)) and the Security Model says "Always access the bridge at astralbeam.io" ([Security Model](https://docs.astralbeam.io/security/security)). astralbeam.io now serves the marketing site, whose "Start beaming on Testnet" button links to `https://testnet.astralbeam.io` ([site bundle](https://astralbeam.io/assets/index-DSzftkm_.js)); the documentation's own Introduction gives that address: "Access the public testnet at: https://testnet.astralbeam.io" ([Introduction](https://docs.astralbeam.io/)).

3. **A Casper-to-EVM transfer costs about 2.5 CSPR.** The fee table on [Bridging Casper to EVM](https://docs.astralbeam.io/using-astralbeam/bridging-casper-to-evm) omits the 50 CSPR bridge fee that the FAQ, the live API and the app's error 60035 all state (previous section).

4. **The code is public.** The Architecture Overview says "Open Source: All code publicly available" ([Architecture Overview](https://docs.astralbeam.io/for-developers/architecture)), and the Introduction says "This project is licensed under the MIT License." ([Introduction](https://docs.astralbeam.io/)). On 2026-09-23 the GitHub API answered HTTP 404 for `make-software/astralbeam-core` (the repository the documentation tells developers to clone, [Local Development](https://docs.astralbeam.io/for-developers/local-development)), `make-software/cspr-bridge` and `make-software/astralbeam-web`, and the npm registry answered 404 for `@astralbeam-io/protocol`, which the documentation itself calls "the private npm package" ([API ingestion](https://docs.astralbeam.io/operators/api-ingestion)). The `bridge-cli` tool the operator pages use is built from source: its installation is `cd cli`, `npm install`, `npm run build`, `npm link` ([CLI Reference](https://docs.astralbeam.io/operators/cli-reference)), run inside a clone of `make-software/astralbeam-core` ([Local Setup](https://docs.astralbeam.io/operators/local-setup)). The npm package that is named `bridge-cli` is unrelated: the registry describes it as "A simple CLI for creating your projects", last modified 2022-04-12 (`https://registry.npmjs.org/bridge-cli`, 2026-09-23). Never suggest `npm install bridge-cli` for AstralBeam.

## What nobody has published about AstralBeam

An honest refusal beats a guess. As of 2026-09-23 none of the following appeared on astralbeam.io, testnet.astralbeam.io, docs.astralbeam.io or in the audit report, and none should be answered from memory:

- **A mainnet date more precise than "October 2026"**, or any mainnet date in the documentation.

- **Mainnet contract addresses** on any chain, Casper or EVM.

- **The mainnet network list.** The roadmap says "all supported chains"; the documentation says only that Robinhood Chain mainnet support is planned.

- **Mainnet fees, limits and liquidity.** The 50 CSPR and 0.0001 ETH (MATIC on Polygon Amoy) fees above are testnet values read on 2026-09-23. The documentation says the Casper fee is adjustable by the admin up to a 10,000 CSPR ceiling ([Casper TokenFactory](https://docs.astralbeam.io/smart-contracts/casper-token-factory)). It says minimum transfer amounts exist but gives no values ([Security Model](https://docs.astralbeam.io/security/security)), and maximums are "Coming Soon" ([EVM Locker](https://docs.astralbeam.io/smart-contracts/evm-locker)).

- **Anything about a token beyond the roadmap row**: its name, ticker, supply, allocation, price, chain, exact date, eligibility, airdrop or points. Nothing says whether testnet activity will count for anything; the playbook says testnet assets have "no real-world value".

- **AstralYield's "10%+"**: its source, the staking provider behind it, or its risks. **AstralIntents**: any specification.

- **The compliance rails**: any specification, contract, standard version or integration partner for ERC-3643, the T-REX Ledger or ERC-7786, or who operates the T-REX Ledger.

- **What sCSPR is and who issues it**, in any AstralBeam source.

- **Review of code written after the audit**, a second auditor, a bug bounty or insurance. The report itself lists code it did not review.

- **Who runs the relayers.** The documentation says "AstralBeam uses a federated model with 5 independent relayers operated by different entities" with a 3-of-5 threshold, and "Relayers are operated by trusted entities in the Casper ecosystem" ([FAQ](https://docs.astralbeam.io/using-astralbeam/faq)); it names none of them.

- **The source code.** The repositories and the package named in the documentation answered 404 (Corrections, item 4).

- **How Casper Association and MAKE divide responsibility for AstralBeam.** The audit report names Casper Association as its client; the sites credit MAKE Technology LLC; no page read here explains the relationship.

- **Terms of service written for AstralBeam.** The testnet app links MAKE's general terms, which do not mention the bridge.

## Sources for this AstralBeam guide

Website, content-addressed, read 2026-09-23 (the SHA-256 digests let a reader tell whether a later copy is the same file):

- `https://astralbeam.io/`: the HTML shell, 2,537 bytes, SHA-256 `0d177dc86bed62bcaacdb15b7a5caf95ed78f92969f7c020677d44a25fd44607`, `Last-Modified: Tue, 15 Sep 2026 02:59:02 GMT`. `https://astralbeam.io/testnet-playbook`: 2,684 bytes, SHA-256 `7378ebb20527ad4cbaa2823db345403be591dc18627ad8246ff53aad13d23019`.

- [`https://astralbeam.io/assets/index-DSzftkm_.js`](https://astralbeam.io/assets/index-DSzftkm_.js): 802,843 bytes, SHA-256 `286ccd4e889b02d33d49769ad1e422ea560774543052f607b0188e2df715e586`. It holds the text of the pages: the home page, the roadmap, the audit card, the footer and the playbook.

Testnet app, content-addressed, read 2026-09-23:

- `https://testnet.astralbeam.io/`: the HTML shell, 2,777 bytes, SHA-256 `624443a40eb2ebae87dd211d3ac08443860d7b88fcf8334f2e45b4f1416c5ec6`.

- [`config.6b682550.js`](https://testnet.astralbeam.io/config.6b682550.js) (1,152 bytes, SHA-256 `6b682550d3147bfaec588188b25092484b86362fcf076195ab89e845d5efdcd4`), the runtime config.

- [`assets/index-vwphA1W3.js`](https://testnet.astralbeam.io/assets/index-vwphA1W3.js) (45,613 bytes, `bff1f810fd191dc6bbe040def66e0a586fbcdf887b6ab92d80b6a5dd1d993ebf`), the entry file, and its source map [`index-vwphA1W3.js.map`](https://testnet.astralbeam.io/assets/index-vwphA1W3.js.map) (185,790 bytes, `a72973e2a1d3cb57741b97f53b1738a7978d16d31e8dc3b2bc9f297a741a4812`).

- [`assets/index-l6sAAYo3.js`](https://testnet.astralbeam.io/assets/index-l6sAAYo3.js), the Beam page (51,845 bytes, `51d6fadcffb3a10730d369ea5789b6c71c954990566bc85369a8958b80b4678b`); [`assets/index-D6E7VKGw.js`](https://testnet.astralbeam.io/assets/index-D6E7VKGw.js), How beaming works (9,833 bytes, `45da39c5470595702875827819a5b197adf0e01042e4b2dd9cb1288123af4407`); [`assets/index-COLtLEBg.js`](https://testnet.astralbeam.io/assets/index-COLtLEBg.js), Faucet (8,976 bytes, `c0bf85fe1239a898e1af24bf0012bcbdb3ff8d2a8c40aa40d9e88d37704de6bc`).

- [`assets/index-CKtGcGDG.js`](https://testnet.astralbeam.io/assets/index-CKtGcGDG.js), Terms of Service (99,462 bytes, `307959905e87b3ce1bd2d7cec9bd6e2c6815abfe5439e904d7f14811cbff4093`); [`assets/BeamTopBar-DjAXEuhj.js`](https://testnet.astralbeam.io/assets/BeamTopBar-DjAXEuhj.js), the top bar and footer (21,869 bytes, `97419f7447c11c67b64328b29938a47802da46f799f5f564dab314e84ba2366a`).

The audit report, served under a fixed name, read 2026-09-23:

- `https://astralbeam.io/audit/halborn-cspr-evm-bridge-ssc.pdf`: 15,893,538 bytes, 172 pages, SHA-256 `28e4b0d2882d86aaebe360f403dda1ffe61ce71238bd36acd9796125efd274bc`, `Last-Modified: Tue, 15 Sep 2026 02:59:02 GMT`. Page numbers above are the PDF's page positions.

Documentation pages, fetched 2026-09-23 (newest sitemap edit 2026-09-21): [Introduction](https://docs.astralbeam.io/), [Quick Start](https://docs.astralbeam.io/getting-started/user-guide), [Bridging Casper to EVM](https://docs.astralbeam.io/using-astralbeam/bridging-casper-to-evm), [Supported Networks](https://docs.astralbeam.io/using-astralbeam/supported-networks), [Supported Tokens](https://docs.astralbeam.io/using-astralbeam/supported-tokens), [Getting Testnet Tokens](https://docs.astralbeam.io/using-astralbeam/getting-testnet-tokens), [FAQ](https://docs.astralbeam.io/using-astralbeam/faq), [Security Model](https://docs.astralbeam.io/security/security), [Audits](https://docs.astralbeam.io/security/audits), [Architecture Overview](https://docs.astralbeam.io/for-developers/architecture), [Local Development](https://docs.astralbeam.io/for-developers/local-development), [API Overview](https://docs.astralbeam.io/api-reference/api-reference), [Build identity](https://docs.astralbeam.io/api-reference/api-reference/api-version), [Contracts](https://docs.astralbeam.io/smart-contracts/contracts), [EVM Locker](https://docs.astralbeam.io/smart-contracts/evm-locker), [Casper TokenFactory](https://docs.astralbeam.io/smart-contracts/casper-token-factory), [API ingestion](https://docs.astralbeam.io/operators/api-ingestion), [CLI Reference](https://docs.astralbeam.io/operators/cli-reference), [Local Setup](https://docs.astralbeam.io/operators/local-setup), [Glossary](https://docs.astralbeam.io/reference/glossary); the [llms.txt](https://docs.astralbeam.io/llms.txt) index and the [page sitemap](https://docs.astralbeam.io/sitemap-pages.xml). The "no match" counts above were made over the markdown of all 46 pages the llms.txt lists, fetched 2026-09-23.

Live, unpinnable, read 2026-09-23 at about 14:38 UTC; every figure taken from these is dated in the text above:

- `https://api.testnet.astralbeam.io/api/v1/chains`, `/api/v1/tokens`, `/api/v1/stats/bridge-fee` and `/api/v1/version`.

- `https://docs.astralbeam.io/~gitbook/mcp` (`initialize` and `tools/list`).

- `https://csprbridge.com` (HTTP 301 to `https://astralbeam.io/`), `https://dev.astralbeam.io/` (HTTP 410), and Halborn's audit page (HTTP 429, not read).

- The GitHub API for `make-software/astralbeam-core`, `make-software/cspr-bridge`, `make-software/astralbeam-web` and `AstralBeamAI/astralbeam`, and the npm registry for `@astralbeam-io/protocol` and `bridge-cli`.
