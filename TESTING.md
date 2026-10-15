# Testing

Run `ruff format --check .`, `ruff check .`, `mypy src`, `pytest`, and `python -m build`. CI also audits dependencies and runs the supported OS/Python matrix.

## 1.1.0 regression acceptance

Run the complete existing suite plus the new regression fixtures. Confirm the documented command produces the selected output, malformed input remains actionable, and source files remain unchanged. Add side-by-side HTML review with scene/chapter anchors and filters, plus previewed stable-ID CSV merging.

## 1.2.0 acceptance

Exercise the optional input with the full regression suite, including validation, inclusive boundaries, deterministic ordering and legacy default behavior. Add `--baseline baseline.json` to `--import-csv edited.csv --format json` for three-way review against the current ledger. In this mode only `id` is required as a CSV header; existing records inherit omitted incoming fields from the supplied baseline, while omitted fields and IDs preserve current values. New IDs require complete valid records. Incoming-only field changes apply; matching concurrent changes agree; divergent changes report baseline/current/incoming conflicts. Identical concurrent additions agree without conflict; divergent supplied values for concurrent new IDs require review. Current deletions require review. IDs cannot move between adaptations. Preview JSON includes conflicts and an inspectable candidate; `--merged-output` refuses any unresolved conflict before writing either output. Omit `--baseline` for the legacy full-row merge. Baseline identity and provenance are author supplied.
