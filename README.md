# Adaptation Difference Ledger

[![CI](https://github.com/loganpendragonmultiverse/adaptation-difference-ledger/actions/workflows/ci.yml/badge.svg)](https://github.com/loganpendragonmultiverse/adaptation-difference-ledger/actions/workflows/ci.yml)

Adaptation Difference Ledger records reviewable differences between a source work and one or more adaptations. It keeps source and adaptation descriptions side by side, categorizes the change, records significance and evidence, and creates deterministic Markdown or JSON reports.

## Three-minute start

Requires Python 3.10 or newer.

```bash
python -m pip install .
adaptation-ledger examples/ledger.json
adaptation-ledger examples/ledger.json --adaptation film --format json
```

The versioned JSON input defines one source, uniquely identified adaptations, and difference records. Categories include character, event, setting, timeline, theme, dialogue, ending, and other. Significance is explicitly supplied as minor, moderate, or major.

Use repeated `--adaptation` flags to focus a report and `--output` to write a new file. Existing outputs are refused.

## Output and privacy

Markdown creates an evidence-oriented comparison by adaptation. JSON adds counts by category, significance, and adaptation. Processing is entirely local with no network requests, telemetry, AI, or content upload.

## Limitations

- The program organizes user-supplied observations; it does not watch, read, scrape, or judge the works.
- Significance is editorial metadata, not an objective score.
- Copyrighted quotations belong in the user's private input only when legally appropriate; examples use invented text.
- The ledger does not determine whether a creative change is good or bad.

## Development and maintenance

Run `python -m pip install -e ".[dev]"`, then `ruff format --check .`, `ruff check .`, `pytest`, and `python -m build`. Contributions go through reviewed pull requests. Version 1.0.0 is feature-complete for structured comparison and reporting.

See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and [SUPPORT.md](SUPPORT.md). Licensed under the [MIT License](LICENSE).

## More open-source projects

This project is part of the [Logan Pendragon Forge open-source collection](https://www.loganpendragonforge.com/open-source/).

## Version 1.1.0: reviewed improvements

Add side-by-side HTML review with scene/chapter anchors and filters, plus previewed stable-ID CSV merging.

```bash
adaptation-ledger examples/ledger.json --format html --output review.html
```

HTML provides search, category/significance filters and local permalink anchors for both source and adaptation descriptions. Optional `source_anchor` and `adaptation_anchor` fields hold author-supplied chapter/scene labels. Export CSV with `--format csv`; preview changes with `--import-csv edited.csv --format json`. Add `--merged-output new-ledger.json` only when ready to write a new ledger. IDs update existing records in place; new IDs append; omitted IDs remain unchanged. Duplicate IDs, malformed rows and attempts to reuse an ID for a different adaptation are rejected. CSV columns are id, adaptation, category, significance, source_version, adaptation_version, source_anchor, adaptation_anchor and evidence. Optional columns not present in the import retain their prior values. No source file is replaced.
