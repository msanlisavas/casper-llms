# Contributing

Thanks for helping keep Casper's documentation readable by LLM tools.

## The one rule: the indexes are generated

Never edit a `*/llms.txt` file by hand. Every index is produced by
[`scripts/generate.py`](scripts/generate.py), and the weekly workflow regenerates all of them,
so a hand edit is overwritten on the next run.

To add, remove or change what an index covers, change `build_indexes()` in the generator.
Each index there lists the repositories, branch or tag, path pattern and citation logic it is
built from.

## Proposing a change

1. Fork the repository and create a branch.
2. Edit `build_indexes()` in `scripts/generate.py`.
3. Regenerate and validate:

   ```
   GITHUB_TOKEN=$(gh auth token) python scripts/generate.py
   python scripts/validate.py
   ```

   The generator fetches every link and reports anything it left out and why: pages that
   404, come back as HTML, or are stubs under 300 bytes.
4. Commit the generator change **and** the regenerated indexes together, and open a pull
   request. The template asks for the generator's report.

The `validate` check must pass. Every pull request needs approval from the code owner before
it can be merged.

## What makes a good source

- **Markdown an ingester can fetch as text.** HTML-only sites cannot be indexed; that is why
  this repository points at source repositories.
- **The version people actually use.** Index the released documentation, not a development
  branch. On a versioned Docusaurus site the generator already follows `versions.json` and
  `lastVersion`.
- **A verifiable published location** for the citation URL, or the file on GitHub when there
  is none. Never add a citation URL that has not been confirmed to show the same content.

Not sure something belongs? Open a "Suggest a documentation source" issue first.

## Reporting a broken or stale link

Use the "Report a broken, stale or wrong link" issue form. Security-relevant problems, such
as a link to a hijacked or malicious page, go through the [security policy](SECURITY.md)
instead.

## Conduct and licensing

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md). By contributing you agree
that your contributions are licensed under the [MIT License](LICENSE).
