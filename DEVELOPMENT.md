# Development

Use the Python package in src and the pytest regression suite. CI must pass before release.

## 1.1.0 improvement session

Add side-by-side HTML review with scene/chapter anchors and filters, plus previewed stable-ID CSV merging.

HTML provides search, category/significance filters and local permalink anchors for both source and adaptation descriptions. Optional `source_anchor` and `adaptation_anchor` fields hold author-supplied chapter/scene labels. Export CSV with `--format csv`; preview changes with `--import-csv edited.csv --format json`. Add `--merged-output new-ledger.json` only when ready to write a new ledger. IDs update existing records in place; new IDs append; omitted IDs remain unchanged. Duplicate IDs, malformed rows and attempts to reuse an ID for a different adaptation are rejected. CSV columns are id, adaptation, category, significance, source_version, adaptation_version, source_anchor, adaptation_anchor and evidence. Optional columns not present in the import retain their prior values. No source file is replaced.

Local formatting, lint, strict types and regression tests pass. Public release completion requires the protected CI/CodeQL matrix, tagged artifacts and matching Forge catalog/detail deployment.

## 1.2.0

Add `--baseline baseline.json` to `--import-csv edited.csv --format json` for three-way review against the current ledger. In this mode only `id` is required as a CSV header; existing records inherit omitted incoming fields from the supplied baseline, while omitted fields and IDs preserve current values. New IDs require complete valid records. Incoming-only field changes apply; matching concurrent changes agree; divergent changes report baseline/current/incoming conflicts. Identical concurrent additions agree without conflict; divergent supplied values for concurrent new IDs require review. Current deletions require review. IDs cannot move between adaptations. Preview JSON includes conflicts and an inspectable candidate; `--merged-output` refuses any unresolved conflict before writing either output. Omit `--baseline` for the legacy full-row merge. Baseline identity and provenance are author supplied.

## Version 1.2.2: reliable validation and packaged examples

Schema versions must be integer `1`; IDs, titles and required descriptions must contain non-whitespace text. Typed adaptation/category/significance values and malformed quoted CSV produce actionable errors. Markdown renders authored HTML and formatting literally. Output creation exclusively reserves a new path, refusing existing files and dangling symbolic links. The wheel now includes the README, changelog, development/testing instructions and synthetic ledger example under `share/doc/adaptation-difference-ledger`.

Run the full suite including `tests/test_gold.py`; test Markdown, JSON, HTML and CSV and a CSV merge with the installed wheel and source distribution. CSV is lossless data interchange: spreadsheet applications may interpret authored cells as formulas, so review untrusted exports as text. Source and baseline identity remain author supplied; no automated creative judgments are made.

Paired report/merged outputs are reserved together before writing. A handled write failure attempts to remove only newly created outputs; an operating-system interruption or cleanup I/O failure can still leave partial output files. Structured Markdown values use single-line text; JSON, HTML and CSV preserve supplied newlines.
