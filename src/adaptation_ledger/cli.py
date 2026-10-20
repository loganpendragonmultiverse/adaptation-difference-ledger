"""Command-line interface."""

from __future__ import annotations

import argparse
import json
import os
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
    parser.add_argument(
        "--baseline", type=Path, help="Explicit baseline ledger for three-way CSV review"
    )
    parser.add_argument("--output", type=Path)
    try:
        args = parser.parse_args(argv)
        ledger = load(args.ledger)
        if args.baseline and not args.import_csv:
            raise LedgerError("--baseline requires --import-csv.")
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
            ledger, preview = merge_csv(
                ledger,
                args.import_csv.read_text(encoding="utf-8"),
                baseline=load(args.baseline) if args.baseline else None,
            )
            if args.merged_output and preview.get("conflicts"):
                raise LedgerError(
                    "Unresolved three-way conflicts; preview without --merged-output."
                )
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
        outputs = {}
        if args.merged_output:
            outputs[args.merged_output] = json.dumps(ledger, indent=2) + "\n"
        if args.output:
            outputs[args.output] = rendered
        _write_outputs(outputs)
        if args.output:
            print(args.output.resolve())
        else:
            print(rendered, end="")
        return 0
    except (LedgerError, OSError, UnicodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


def _write_outputs(outputs: dict[Path, str]) -> None:
    """Reserve every new path before writing; roll back only files we created."""
    reserved = []
    try:
        for path in outputs:
            path.parent.mkdir(parents=True, exist_ok=True)
            handle = path.open("x", encoding="utf-8")
            reserved.append((path, handle, os.fstat(handle.fileno())))
        for path, handle, _ in reserved:
            handle.write(outputs[path])
            handle.flush()
    except (OSError, UnicodeError):
        for path, handle, identity in reserved:
            handle.close()
            try:
                current = path.lstat()
                if (current.st_dev, current.st_ino) == (identity.st_dev, identity.st_ino):
                    path.unlink()
            except OSError:
                pass  # Report the original I/O error; never remove another file.
        raise
    finally:
        for _, handle, _ in reserved:
            handle.close()


if __name__ == "__main__":
    raise SystemExit(main())
