import copy
import json
from pathlib import Path

import pytest
from test_core import sample

from adaptation_ledger.cli import main
from adaptation_ledger.core import LedgerError, summarize
from adaptation_ledger.review import csv_export, html_review, merge_csv


def test_csv_roundtrip_and_non_destructive_merge() -> None:
    original = sample()
    before = copy.deepcopy(original)
    merged, preview = merge_csv(original, csv_export(original))
    assert preview["changes"][0]["action"] == "updated"  # optional blank anchor columns
    assert merged["differences"][0]["source_version"] == "The hero leaves."
    assert original == before
    update = copy.deepcopy(original)
    update["differences"][0]["source_version"] = 'A comma, a "quote" and\na newline.'
    merged, preview = merge_csv(original, csv_export(update))
    assert merged["differences"][0]["source_version"] == update["differences"][0]["source_version"]
    assert preview["changes"][0]["before"]["source_version"] == "The hero leaves."
    update["differences"][0]["id"] = "new"
    merged, preview = merge_csv(original, csv_export(update))
    assert [d["id"] for d in merged["differences"]] == ["ending-1", "new"]
    assert preview["removed"] == []


def test_duplicate_cross_adaptation_and_malformed_csv() -> None:
    original = sample()
    changed = copy.deepcopy(original)
    changed["differences"][0]["adaptation"] = "series"
    with pytest.raises(LedgerError, match="another adaptation"):
        merge_csv(original, csv_export(changed))
    changed["differences"] *= 2
    with pytest.raises(LedgerError):
        merge_csv(original, csv_export(changed))
    for text in ("id,id\na,b", csv_export(original) + "bad,row\n"):
        with pytest.raises(LedgerError):
            merge_csv(original, text)


def test_cli_preview_apply_and_html_safety(tmp_path: Path) -> None:
    original = sample()
    original["differences"][0]["source_anchor"] = "Chapter 4"
    source = tmp_path / "source.json"
    source.write_text(json.dumps(original), encoding="utf-8")
    csv = tmp_path / "changes.csv"
    original["differences"][0]["source_version"] = "</script><img src=x onerror=alert(1)>"
    csv.write_text(csv_export(original), encoding="utf-8")
    report, merged = tmp_path / "review.json", tmp_path / "merged.json"
    assert (
        main([str(source), "--import-csv", str(csv), "--format", "json", "--output", str(report)])
        == 0
    )
    assert not merged.exists()
    assert (
        json.loads(report.read_text(encoding="utf-8"))["import_preview"]["changes"][0]["action"]
        == "updated"
    )
    assert main([str(source), "--import-csv", str(csv), "--merged-output", str(merged)]) == 0
    assert (
        json.loads(source.read_text(encoding="utf-8"))["differences"][0]["source_version"]
        == "The hero leaves."
    )
    assert main([str(source), "--import-csv", str(csv), "--merged-output", str(merged)]) == 2
    html = html_review(summarize(original))
    assert "</script><img" not in html
    assert "Chapter 4" in html and 'type="search"' in html
