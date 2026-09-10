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

## What is not in scope

The documentation the indexes point at belongs to its publishers. Errors in that content, or
vulnerabilities in the software it describes, should be reported to the project that
publishes it (for example `casper-network`, `casper-ecosystem`, `make-software` or `odradev`
on GitHub).

## Supported versions

Only the current `main` branch is maintained. There are no releases.
