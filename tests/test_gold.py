import json
from pathlib import Path

import pytest
from test_core import sample

from adaptation_ledger.cli import main
from adaptation_ledger.core import LedgerError, markdown, summarize, validate
from adaptation_ledger.review import merge_csv


@pytest.mark.parametrize("field", ["adaptation", "category", "significance"])
@pytest.mark.parametrize("value", [[], {}, True, None, 1])
def test_typed_membership_fields_are_actionable(field, value, tmp_path: Path, capsys):
    data = sample()
    data["differences"][0][field] = value
    with pytest.raises(LedgerError):
        validate(data)
    source = tmp_path / "ledger.json"
    source.write_text(json.dumps(data), encoding="utf-8")
    assert main([str(source)]) == 2
    assert "Traceback" not in capsys.readouterr().err


@pytest.mark.parametrize("version", [True, 1.0, "1", None])
def test_schema_version_is_an_integer(version):
    data = sample()
    data["version"] = version
    with pytest.raises(LedgerError, match="version 1"):
        validate(data)


@pytest.mark.parametrize("baseline", [False, True])
def test_malformed_quoted_csv_is_rejected(baseline):
    with pytest.raises(LedgerError, match="Malformed CSV"):
        merge_csv(
            sample(),
            'id,source_version\nending-1,"unfinished',
            baseline=sample() if baseline else None,
        )


def test_blank_labels_and_descriptions_are_rejected():
    data = sample()
    data["source"]["title"] = "  "
    with pytest.raises(LedgerError, match="title"):
        validate(data)
    data = sample()
    data["differences"][0]["source_version"] = "\n\t"
    with pytest.raises(LedgerError, match="source_version"):
        validate(data)


def test_markdown_treats_authored_markup_literally():
    data = sample()
    data["source"]["title"] = "<img src=x> [title](https://example.com)"
    data["differences"][0]["source_version"] = "<script>danger</script>\n# heading"
    rendered = markdown(summarize(validate(data)))
    assert "<img" not in rendered and "<script>" not in rendered
    assert "&lt;script&gt;" in rendered and "\\# heading" in rendered
    assert "\\[title\\]" in rendered


def test_dangling_output_link_is_not_followed(tmp_path: Path):
    source = tmp_path / "source.json"
    source.write_text(json.dumps(sample()), encoding="utf-8")
    target, output = tmp_path / "missing", tmp_path / "report.md"
    try:
        output.symlink_to(target)
    except OSError:
        pytest.skip("symlinks unavailable")
    assert main([str(source), "--output", str(output)]) == 2
    assert output.is_symlink() and not target.exists()


def test_second_output_failure_rolls_back_only_new_merged_ledger(tmp_path: Path):
    from adaptation_ledger.review import csv_export

    source = tmp_path / "source.json"
    source.write_text(json.dumps(sample()), encoding="utf-8")
    incoming = tmp_path / "incoming.csv"
    incoming.write_text(csv_export(sample()), encoding="utf-8")
    merged, report, missing = tmp_path / "merged.json", tmp_path / "report.md", tmp_path / "missing"
    try:
        report.symlink_to(missing)
    except OSError:
        pytest.skip("symlinks unavailable")
    assert (
        main(
            [
                str(source),
                "--import-csv",
                str(incoming),
                "--merged-output",
                str(merged),
                "--output",
                str(report),
            ]
        )
        == 2
    )
    assert not merged.exists()
    assert report.is_symlink() and not missing.exists()
    assert json.loads(source.read_text(encoding="utf-8")) == sample()
