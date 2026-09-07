"""Command-line interface."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from .core import LedgerError, load, markdown, summarize
from .review import csv_export, html_review, merge_csv


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="adaptation-ledger")
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--adaptation", action="append", default=[])
    parser.add_argument("--format", choices=("markdown", "json", "html", "csv"), default="markdown")
    parser.add_argument("--import-csv", type=Path, help="Preview stable-ID CSV changes")
    parser.add_argument(
        "--merged-output", type=Path, help="Write the reviewed merge to a new ledger"
    )
    parser.add_argument("--output", type=Path)
    try:
        args = parser.parse_args(argv)
        ledger = load(args.ledger)
        if args.merged_output and not args.import_csv:
            raise LedgerError("--merged-output requires --import-csv.")
        targets = [path for path in (args.output, args.merged_output) if path]
        if len({path.resolve() for path in targets}) != len(targets):
            raise LedgerError("Report and merged output must be different files.")
        for path in targets:
            if path.exists():
                raise LedgerError(f"Output already exists: {path}")
        preview = None
        if args.import_csv:
            ledger, preview = merge_csv(ledger, args.import_csv.read_text(encoding="utf-8"))
        result = summarize(ledger, adaptations=set(args.adaptation) or None)
        if preview is not None:
            result["import_preview"] = preview
        if args.format == "json":
            rendered = json.dumps(result, indent=2) + "\n"
        elif args.format == "html":
            rendered = html_review(result)
        elif args.format == "csv":
            rendered = csv_export(result)
        else:
            rendered = markdown(result)
        if preview is not None and args.format != "json":
            print(json.dumps(preview, indent=2), file=sys.stderr)
        if args.merged_output:
            args.merged_output.parent.mkdir(parents=True, exist_ok=True)
            args.merged_output.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
        if args.output:
            if args.output.exists():
                raise LedgerError(f"Output already exists: {args.output}")
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
            print(args.output.resolve())
        else:
            print(rendered, end="")
        return 0
    except (LedgerError, OSError, UnicodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
