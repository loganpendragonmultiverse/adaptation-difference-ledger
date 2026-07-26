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
