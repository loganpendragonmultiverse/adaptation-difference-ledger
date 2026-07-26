"""Structured adaptation comparison."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

CATEGORIES = {"character", "event", "setting", "timeline", "theme", "dialogue", "ending", "other"}
SIGNIFICANCE = {"minor", "moderate", "major"}


class LedgerError(ValueError):
    """Raised for invalid source data."""


def load(path: Path) -> dict[str, Any]:
    try:
        return validate(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise LedgerError(f"Could not read ledger: {exc}") from exc


def validate(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict) or payload.get("version") != 1:
        raise LedgerError("Ledger must be a version 1 JSON object.")
    source = payload.get("source")
    adaptations = payload.get("adaptations")
    differences = payload.get("differences")
    if not isinstance(source, dict) or not isinstance(source.get("title"), str):
        raise LedgerError("source needs a title.")
    if not isinstance(adaptations, list) or not adaptations:
        raise LedgerError("adaptations must be a non-empty list.")
    adaptation_ids: set[str] = set()
    for item in adaptations:
        if (
            not isinstance(item, dict)
            or not isinstance(item.get("id"), str)
            or not item["id"]
            or item["id"] in adaptation_ids
        ):
            raise LedgerError("Adaptation IDs must be non-empty and unique.")
        if not isinstance(item.get("title"), str) or not item["title"]:
            raise LedgerError(f"Adaptation {item['id']} needs a title.")
        adaptation_ids.add(item["id"])
    if not isinstance(differences, list):
        raise LedgerError("differences must be a list.")
    difference_ids: set[str] = set()
    for item in differences:
        if (
            not isinstance(item, dict)
            or not isinstance(item.get("id"), str)
            or not item["id"]
            or item["id"] in difference_ids
        ):
            raise LedgerError("Difference IDs must be non-empty and unique.")
        difference_ids.add(item["id"])
        if item.get("adaptation") not in adaptation_ids:
            raise LedgerError(f"Difference {item['id']} references an unknown adaptation.")
        if item.get("category") not in CATEGORIES or item.get("significance") not in SIGNIFICANCE:
            raise LedgerError(f"Difference {item['id']} has an invalid category or significance.")
        for field in ("source_version", "adaptation_version"):
            if not isinstance(item.get(field), str) or not item[field]:
                raise LedgerError(f"Difference {item['id']} needs {field}.")
    return payload


def summarize(ledger: dict[str, Any], *, adaptations: set[str] | None = None) -> dict[str, Any]:
    known = {item["id"] for item in ledger["adaptations"]}
    chosen = adaptations or known
    unknown = chosen - known
    if unknown:
        raise LedgerError(f"Unknown adaptations: {', '.join(sorted(unknown))}")
    items = [item for item in ledger["differences"] if item["adaptation"] in chosen]
    return {
        "source": ledger["source"],
        "adaptations": [item for item in ledger["adaptations"] if item["id"] in chosen],
        "counts": {
            "total": len(items),
            "by_category": dict(sorted(Counter(item["category"] for item in items).items())),
            "by_significance": dict(
                sorted(Counter(item["significance"] for item in items).items())
            ),
            "by_adaptation": dict(sorted(Counter(item["adaptation"] for item in items).items())),
        },
        "differences": sorted(
            items, key=lambda item: (item["adaptation"], item["category"], item["id"])
        ),
    }


def markdown(payload: dict[str, Any]) -> str:
    lines = [
        f"# {payload['source']['title']}: adaptation differences",
        "",
        f"Recorded differences: **{payload['counts']['total']}**",
        "",
    ]
    titles = {item["id"]: item["title"] for item in payload["adaptations"]}
    for identifier, title in titles.items():
        lines.extend([f"## {title}", ""])
        items = [item for item in payload["differences"] if item["adaptation"] == identifier]
        if not items:
            lines.extend(["_No differences recorded._", ""])
        for item in items:
            lines.extend(
                [
                    f"### {item['category'].title()}: {item['id']}",
                    f"Significance: **{item['significance']}**",
                    "",
                    f"- Source: {item['source_version']}",
                    f"- Adaptation: {item['adaptation_version']}",
                ]
            )
            if item.get("evidence"):
                lines.append(f"- Evidence: {item['evidence']}")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"
