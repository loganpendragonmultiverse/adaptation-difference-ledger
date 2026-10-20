# Changelog

## 1.2.2 - 2026-10-20

- Validate typed enum fields, exact integer schema versions and blank required text without tracebacks.
- Reject malformed quoted CSV and render authored Markdown/HTML literally.
- Refuse output races and dangling symbolic links through exclusive creation.
- Include operating documents and the synthetic example in the wheel.

## 1.2.1

- Correct released documentation labels; package behavior is unchanged.
- Preserve the original v1.2.0 tags and artifacts. This patch supplies corrected documentation in new artifacts.

## 1.2.0 - 2026-10-15

- Add `--baseline baseline.json` to `--import-csv edited.csv --format json` for three-way review against the current ledger.

## 1.1.0 - 2026-09-07

- Add side-by-side HTML review with scene/chapter anchors and filters, plus previewed stable-ID CSV merging.
- Added regression coverage for the audited behavior and invalid inputs.

## [1.0.0] - 2026-07-26

- Initial source/adaptation schema validation, category and significance summaries, filtered Markdown/JSON reports, examples, and automated tests.

[1.0.0]: https://github.com/loganpendragonmultiverse/adaptation-difference-ledger/releases/tag/v1.0.0
