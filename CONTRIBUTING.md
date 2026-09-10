# Contributing

Thanks for helping make Casper readable, and usable, by AI tools.

There are three ways in: list an AI capability, suggest a documentation source, or report a
broken or stale link. Not sure which one fits? Open an issue first.

## The one rule: generated files are never edited by hand

These files are generated, and the weekly workflow or the next contributor's run overwrites any
hand edit:

- every `*/llms.txt` index, from `build_indexes()` in [`scripts/generate.py`](scripts/generate.py);
- the root `llms.txt`, `directory.md`, `casper-guides/llms.txt` and the tables between the
  `<!-- ...:start -->` and `<!-- ...:end -->` markers in `README.md`, from
  [`catalog.json`](catalog.json) and `guides/` by [`scripts/catalog.py`](scripts/catalog.py).

`python scripts/validate.py` fails when a rendered file does not match what its sources produce.

## Listing an AI capability

The directory lists what an AI agent can use with the Casper Network: MCP servers, agent skills,
llms.txt documentation indexes, APIs built for agents (including x402 pay-per-call APIs),
SDKs for agent or x402 integration, and agent plugins. Yours is welcome, including a paid one.

A capability is listed when it meets every rule:

1. **It is public and works with Casper** mainnet or testnet, or documents Casper Network
   products.
2. **Its documentation is readable as text**: `docs.fetch` returns markdown or plain text (a raw
   README, a `.md` page, an llms.txt), not HTML.
3. **It is never custodial.** A tool that asks users to send a secret key or seed phrase to a
   remote service is not listed. Signing locally, under the user's control, is fine.
4. **Paid capabilities state their pricing** in `pricingNote`.
5. **It is alive**: a live endpoint, or a commit, release or package publish within the last
   twelve months.
6. **One entry per capability**, not per marketing page. An MCP server with a mainnet and a
   testnet endpoint is one entry.

To add or change an entry:

1. Fork the repository and create a branch.
2. Edit [`catalog.json`](catalog.json). [`catalog.schema.json`](catalog.schema.json) documents
   every field; an editor that reads `$schema` will check as you type. Write the description as
   one or two factual sentences, no marketing.
3. Render and check, offline:

   ```
   python scripts/generate.py --catalog-only
   python scripts/validate.py
   ```

4. Commit `catalog.json` **and** the rendered files together, and open a pull request.

Or open a "List an AI capability" issue and a maintainer will add it. Once listed, the
[weekly check](.github/workflows/check.yml) probes the entry; an entry that stays unreachable is
removed.

## Suggesting a documentation source

1. Fork the repository and create a branch.
2. Edit `build_indexes()` in `scripts/generate.py`. Each index there lists the repositories,
   branch or tag, path pattern and citation logic it is built from.
3. Regenerate and validate:

   ```
   GITHUB_TOKEN=$(gh auth token) python scripts/generate.py
   python scripts/validate.py
   ```

   The generator fetches every link and reports anything it left out and why: pages that
   404, come back as HTML, or are stubs under 300 bytes.
4. Commit the generator change **and** the regenerated files together, and open a pull
   request. The template asks for the generator's report.

What makes a good source:

- **Markdown an ingester can fetch as text.** HTML-only sites cannot be indexed; that is why
  this repository points at source repositories.
- **The version people actually use.** Index the released documentation, not a development
  branch. On a versioned Docusaurus site the generator already follows `versions.json` and
  `lastVersion`.
- **A verifiable published location** for the citation URL, or the file on GitHub when there
  is none. Never add a citation URL that has not been confirmed to show the same content.

## Guides

The guides in [`guides/`](guides) are written here, for what the official documentation does
not cover. An LLM repeats what it is given, so the rules are strict:

- Every factual sentence links a **pinned** source: a release tag or a full commit SHA, never a
  branch. A claim no source supports is cut, not softened.
- Line 1 is the title (`# ...`), line 2 is blank, and line 3 names what the guide was verified
  against: `Verified against casper-node v2.2.2 on 2026-09-10.` The components the weekly check
  can follow are `casper-node`, `casper-client-rs` and `docs.casper.network`.
- No YAML frontmatter and no HTML.
- Command examples use placeholders such as `<PATH-TO-YOUR-SECRET-KEY>` and never real keys.

When the weekly check reports that a newer release has shipped, re-verify the guide against it,
correct what changed, and update the verification line. Run
`python scripts/generate.py --catalog-only` after any change to `guides/`.

## Reporting a broken or stale link

Use the "Report a broken, stale or wrong link" issue form. Security-relevant problems, such
as a link to a hijacked or malicious page or a listed tool that misbehaves, go through the
[security policy](SECURITY.md) instead.

## Checks every pull request must pass

`python scripts/validate.py` and `python -m unittest discover -s scripts/tests`, both run by the
`validate` workflow. Changes to the plugin marketplace should also pass
`claude plugin validate .` locally. Every pull request needs approval from the code owner before
it can be merged.

## Conduct and licensing

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md). By contributing you agree
that your contributions are licensed under the [MIT License](LICENSE).
