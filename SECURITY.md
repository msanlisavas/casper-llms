# Security policy

## Reporting a vulnerability

Please report security problems privately, through GitHub's
[private vulnerability reporting](https://github.com/msanlisavas/casper-llms/security/advisories/new),
not in a public issue. Reports are handled privately by the maintainer.

## What is in scope

- **The generator** (`scripts/`) and the **GitHub Actions workflows** (`.github/workflows/`),
  for example a way to make the scheduled workflow run untrusted code or push unreviewed content.
- **An index pointing somewhere it should not**: a link or citation URL that leads to a hijacked,
  squatted or malicious page, or to content other than what its title describes. An LLM that
  ingests these indexes trusts what they point at, so this matters even though the pages
  themselves belong to others.
- **A listed capability that endangers its users**: a tool in the directory, or a plugin in the
  marketplace, that asks users for a secret key or seed phrase, sends keys or credentials
  somewhere it should not, installs something other than what its entry describes, or carries
  instructions aimed at the agents that read it. Report it here so the entry can be removed or
  given a caution quickly; report the flaw itself to its publisher too.

## What is not in scope

The documentation the indexes point at, and the tools the directory lists, belong to their
publishers. Errors in that content, or vulnerabilities in the software it describes, should be
reported to the project that publishes it (for example `casper-network`, `casper-ecosystem`,
`make-software` or `odradev` on GitHub). What is in scope here is only whether this repository
should keep pointing at it.

## Supported versions

Only the current `main` branch is maintained. There are no releases.
