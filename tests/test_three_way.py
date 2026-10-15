import copy
import json

import pytest
from test_core import sample

from adaptation_ledger.cli import main
from adaptation_ledger.core import LedgerError
from adaptation_ledger.review import csv_export, merge_csv


def test_concurrent_fields_conflict_and_nonconflicting_preservation():
    baseline = sample()
    current, incoming = copy.deepcopy(baseline), copy.deepcopy(baseline)
    current["differences"][0].update(source_version="Current", evidence="Current evidence")
    incoming["differences"][0].update(source_version="Incoming", adaptation_version="Incoming film")
    before = copy.deepcopy(current)
    merged, preview = merge_csv(current, csv_export(incoming), baseline=baseline)
    assert preview["conflicts"] == [
        {
            "id": "ending-1",
            "field": "source_version",
            "baseline": "The hero leaves.",
            "current": "Current",
            "incoming": "Incoming",
        }
    ]
    assert merged["differences"][0]["evidence"] == "Current evidence"
    assert merged["differences"][0]["adaptation_version"] == "Incoming film"
    assert current == before


def test_omitted_columns_new_ids_same_changes_and_no_deletion():
    baseline = sample()
    current = copy.deepcopy(baseline)
    current["differences"][0]["evidence"] = "Later evidence"
    merged, preview = merge_csv(
        current, "id,source_version\nending-1,New text\n", baseline=baseline
    )
    assert not preview["conflicts"]
    assert merged["differences"][0]["evidence"] == "Later evidence"
    incoming = copy.deepcopy(baseline)
    incoming["differences"][0]["id"] = "new"
    merged, preview = merge_csv(current, csv_export(incoming), baseline=baseline)
    assert [r["id"] for r in merged["differences"]] == ["ending-1", "new"]
    assert preview["removed"] == []
    assert not merge_csv(baseline, csv_export(baseline), baseline=baseline)[1]["conflicts"]


def test_new_id_collision_removed_record_and_reused_adaptation():
    baseline = sample()
    incoming = copy.deepcopy(baseline)
    incoming["differences"][0]["source_version"] = "changed"
    assert merge_csv(baseline, csv_export(incoming), baseline={**baseline, "differences": []})[1][
        "conflicts"
    ]
    assert merge_csv({**baseline, "differences": []}, csv_export(incoming), baseline=baseline)[1][
        "conflicts"
    ]
    incoming["differences"][0]["adaptation"] = "series"
    with pytest.raises(LedgerError, match="another adaptation"):
        merge_csv(baseline, csv_export(incoming), baseline=baseline)


@pytest.mark.parametrize(
    "text",
    ["id,id\\na,b", "other\\nx", "id\\nending-1,extra", "id\\nending-1\\nending-1", "id\\nmissing"],
)
def test_invalid_baseline_csv(text):
    with pytest.raises(LedgerError):
        merge_csv(sample(), text.replace("\\n", "\n"), baseline=sample())


def test_cli_conflict_refuses_all_output_and_preserves_sources(tmp_path, capsys):
    base = sample()
    current = copy.deepcopy(base)
    incoming = copy.deepcopy(base)
    current["differences"][0]["source_version"] = "local"
    incoming["differences"][0]["source_version"] = "remote"
    paths = {
        name: tmp_path / name
        for name in ("base.json", "current.json", "incoming.csv", "merged.json", "report.json")
    }
    paths["base.json"].write_text(json.dumps(base))
    paths["current.json"].write_text(json.dumps(current))
    paths["incoming.csv"].write_text(csv_export(incoming))
    args = [
        str(paths["current.json"]),
        "--baseline",
        str(paths["base.json"]),
        "--import-csv",
        str(paths["incoming.csv"]),
    ]
    assert main([*args, "--format", "json"]) == 0
    assert json.loads(capsys.readouterr().out)["import_preview"]["conflicts"]
    assert (
        main(
            [
                *args,
                "--merged-output",
                str(paths["merged.json"]),
                "--output",
                str(paths["report.json"]),
            ]
        )
        == 2
    )
    assert not paths["merged.json"].exists() and not paths["report.json"].exists()
    assert json.loads(paths["current.json"].read_text()) == current
    assert main([str(paths["current.json"]), "--baseline", str(paths["base.json"])]) == 2


def test_matching_concurrent_change_and_cli_success(tmp_path, capsys):
    base = sample()
    edited = copy.deepcopy(base)
    edited["differences"][0]["source_version"] = "Shared change"
    merged, preview = merge_csv(edited, csv_export(edited), baseline=base)
    assert not preview["conflicts"]
    assert merged["differences"][0]["source_version"] == "Shared change"
    baseline = tmp_path / "baseline.json"
    current = tmp_path / "current.json"
    incoming = tmp_path / "incoming.csv"
    output = tmp_path / "merged.json"
    baseline.write_text(json.dumps(base))
    current.write_text(json.dumps(base))
    incoming.write_text(chr(10).join(["id,source_version", "ending-1,Shared change", ""]))
    assert (
        main(
            [
                str(current),
                "--baseline",
                str(baseline),
                "--import-csv",
                str(incoming),
                "--merged-output",
                str(output),
            ]
        )
        == 0
    )
    assert json.loads(output.read_text())["differences"][0]["source_version"] == "Shared change"
    assert json.loads(current.read_text()) == base


def test_current_reuses_difference_id_for_other_adaptation():
    baseline = sample()
    current = copy.deepcopy(baseline)
    current["differences"][0]["adaptation"] = "series"
    with pytest.raises(LedgerError, match="another adaptation"):
        merge_csv(current, csv_export(baseline), baseline=baseline)
