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

## Version 1.2.0

Add `--baseline baseline.json` to `--import-csv edited.csv --format json` for three-way review against the current ledger. In this mode only `id` is required as a CSV header; existing records inherit omitted incoming fields from the supplied baseline, while omitted fields and IDs preserve current values. New IDs require complete valid records. Incoming-only field changes apply; matching concurrent changes agree; divergent changes report baseline/current/incoming conflicts. Identical concurrent additions agree without conflict; divergent supplied values for concurrent new IDs require review. Current deletions require review. IDs cannot move between adaptations. Preview JSON includes conflicts and an inspectable candidate; `--merged-output` refuses any unresolved conflict before writing either output. Omit `--baseline` for the legacy full-row merge. Baseline identity and provenance are author supplied.

## Version 1.2.1: documentation correction

Version 1.2.0 was released on October 15, 2026. Version 1.2.1 corrects its release labels without changing behavior. The original v1.2.0 tag and downloadable artifacts remain unchanged; use v1.2.1 for the corrected packaged documentation.

## Version 1.2.2: reliable validation and packaged examples

Schema versions must be integer `1`; IDs, titles and required descriptions must contain non-whitespace text. Typed adaptation/category/significance values and malformed quoted CSV produce actionable errors. Markdown renders authored HTML and formatting literally. Output creation exclusively reserves a new path, refusing existing files and dangling symbolic links. The wheel now includes the README, changelog, development/testing instructions and synthetic ledger example under `share/doc/adaptation-difference-ledger`.

Run the full suite including `tests/test_gold.py`; test Markdown, JSON, HTML and CSV and a CSV merge with the installed wheel and source distribution. CSV is lossless data interchange: spreadsheet applications may interpret authored cells as formulas, so review untrusted exports as text. Source and baseline identity remain author supplied; no automated creative judgments are made.

Paired report/merged outputs are reserved together before writing. A handled write failure attempts to remove only newly created outputs; an operating-system interruption or cleanup I/O failure can still leave partial output files. Structured Markdown values use single-line text; JSON, HTML and CSV preserve supplied newlines.
