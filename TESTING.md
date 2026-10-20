# Testing

Run `ruff format --check .`, `ruff check .`, `mypy src`, `pytest`, and `python -m build`. CI also audits dependencies and runs the supported OS/Python matrix.

## 1.1.0 regression acceptance

Run the complete existing suite plus the new regression fixtures. Confirm the documented command produces the selected output, malformed input remains actionable, and source files remain unchanged. Add side-by-side HTML review with scene/chapter anchors and filters, plus previewed stable-ID CSV merging.

## 1.2.0 acceptance

Exercise the optional input with the full regression suite, including validation, inclusive boundaries, deterministic ordering and legacy default behavior. Add `--baseline baseline.json` to `--import-csv edited.csv --format json` for three-way review against the current ledger. In this mode only `id` is required as a CSV header; existing records inherit omitted incoming fields from the supplied baseline, while omitted fields and IDs preserve current values. New IDs require complete valid records. Incoming-only field changes apply; matching concurrent changes agree; divergent changes report baseline/current/incoming conflicts. Identical concurrent additions agree without conflict; divergent supplied values for concurrent new IDs require review. Current deletions require review. IDs cannot move between adaptations. Preview JSON includes conflicts and an inspectable candidate; `--merged-output` refuses any unresolved conflict before writing either output. Omit `--baseline` for the legacy full-row merge. Baseline identity and provenance are author supplied.

## Version 1.2.2: reliable validation and packaged examples

Schema versions must be integer `1`; IDs, titles and required descriptions must contain non-whitespace text. Typed adaptation/category/significance values and malformed quoted CSV produce actionable errors. Markdown renders authored HTML and formatting literally. Output creation exclusively reserves a new path, refusing existing files and dangling symbolic links. The wheel now includes the README, changelog, development/testing instructions and synthetic ledger example under `share/doc/adaptation-difference-ledger`.

Run the full suite including `tests/test_gold.py`; test Markdown, JSON, HTML and CSV and a CSV merge with the installed wheel and source distribution. CSV is lossless data interchange: spreadsheet applications may interpret authored cells as formulas, so review untrusted exports as text. Source and baseline identity remain author supplied; no automated creative judgments are made.

Paired report/merged outputs are reserved together before writing. A handled write failure removes only newly created outputs; interruption by the operating system can still leave partial output files. Structured Markdown values use single-line text; JSON, HTML and CSV preserve supplied newlines.
