## What this changes

<!-- A new or changed capability, a new source, a removed page, a guide, a version or branch correction... -->

## Checklist

- [ ] I changed the sources (`catalog.json`, `guides/`, or `build_indexes()` in `scripts/generate.py`), not a generated file by hand.
- [ ] I ran `python scripts/generate.py` (or `--catalog-only` for catalog and guide changes) and committed the rendered files with the change.
- [ ] `python scripts/validate.py` and `python -m unittest discover -s scripts/tests` pass.

### For a catalog entry

- [ ] It meets every listing rule in CONTRIBUTING.md, including: never asks users to send a secret key or seed phrase to a remote service.
- [ ] `docs.fetch` returns markdown or plain text, and every URL was opened.

### For a documentation source

- [ ] New sources are the **released** documentation, not a development branch.
- [ ] Every new citation URL was confirmed to show the same content as the fetched file.

### For a guide

- [ ] Every factual sentence links a pinned source (a tag or a full commit SHA), and the verification line names the releases it was checked against.

## Generator report

<!-- Paste the generator's summary and any "skipped" or "no public page found" lines. -->
