# Development

Use the Python package in src and the pytest regression suite. CI must pass before release.

## 1.1.0 improvement session

Add side-by-side HTML review with scene/chapter anchors and filters, plus previewed stable-ID CSV merging.

HTML provides search, category/significance filters and local permalink anchors for both source and adaptation descriptions. Optional `source_anchor` and `adaptation_anchor` fields hold author-supplied chapter/scene labels. Export CSV with `--format csv`; preview changes with `--import-csv edited.csv --format json`. Add `--merged-output new-ledger.json` only when ready to write a new ledger. IDs update existing records in place; new IDs append; omitted IDs remain unchanged. Duplicate IDs, malformed rows and attempts to reuse an ID for a different adaptation are rejected. CSV columns are id, adaptation, category, significance, source_version, adaptation_version, source_anchor, adaptation_anchor and evidence. Optional columns not present in the import retain their prior values. No source file is replaced.

Local formatting, lint, strict types and regression tests pass. Public release completion requires the protected CI/CodeQL matrix, tagged artifacts and matching Forge catalog/detail deployment.

## 1.2.0 candidate

Add `--baseline baseline.json` to `--import-csv edited.csv --format json` for three-way review against the current ledger. In this mode only `id` is required as a CSV header; existing records inherit omitted incoming fields from the supplied baseline, while omitted fields and IDs preserve current values. New IDs require complete valid records. Incoming-only field changes apply; matching concurrent changes agree; divergent changes report baseline/current/incoming conflicts. Concurrent new IDs and current deletions require review. IDs cannot move between adaptations. Preview JSON includes conflicts and an inspectable candidate; `--merged-output` refuses any unresolved conflict before writing either output. Omit `--baseline` for the legacy full-row merge. Baseline identity and provenance are author supplied.
