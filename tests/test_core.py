import json
from pathlib import Path

import pytest

from adaptation_ledger.cli import main
from adaptation_ledger.core import LedgerError, markdown, summarize, validate


def sample() -> dict:
    return {
        "version": 1,
        "source": {"title": "The Book", "edition": "First"},
        "adaptations": [
            {"id": "film", "title": "The Film", "year": 2020},
            {"id": "series", "title": "The Series", "year": 2024},
        ],
        "differences": [
            {
                "id": "ending-1",
                "adaptation": "film",
                "category": "ending",
                "significance": "major",
                "source_version": "The hero leaves.",
                "adaptation_version": "The hero stays.",
                "evidence": "Final scene",
            }
        ],
    }


def test_summary_counts_and_filter() -> None:
    result = summarize(validate(sample()), adaptations={"film"})
    assert result["counts"]["by_category"] == {"ending": 1}
    assert len(result["adaptations"]) == 1


def test_markdown_contains_both_versions() -> None:
    text = markdown(summarize(validate(sample())))
    assert "The hero leaves" in text and "The hero stays" in text


@pytest.mark.parametrize(
    "change,message",
    [
        ({"version": 2}, "version 1"),
        ({"source": {}}, "source"),
        ({"adaptations": []}, "adaptations"),
        ({"differences": "bad"}, "differences"),
    ],
)
def test_invalid_roots(change: dict, message: str) -> None:
    payload = sample()
    payload.update(change)
    with pytest.raises(LedgerError, match=message):
        validate(payload)


def test_invalid_difference_and_unknown_filter() -> None:
    payload = sample()
    payload["differences"][0]["category"] = "costume"
    with pytest.raises(LedgerError, match="invalid"):
        validate(payload)
    with pytest.raises(LedgerError, match="Unknown"):
        summarize(validate(sample()), adaptations={"radio"})


def test_cli_json_and_output_guard(tmp_path: Path, capsys) -> None:  # type: ignore[no-untyped-def]
    source = tmp_path / "ledger.json"
    source.write_text(json.dumps(sample()), encoding="utf-8")
    target = tmp_path / "report.json"
    assert main([str(source), "--format", "json", "--output", str(target)]) == 0
    assert json.loads(target.read_text())["counts"]["total"] == 1
    assert main([str(source), "--output", str(target)]) == 2
    assert "already exists" in capsys.readouterr().err


def test_adaptation_and_difference_validation_edges() -> None:
    bad_adaptation = sample()
    bad_adaptation["adaptations"] = ["bad"]
    with pytest.raises(LedgerError, match="IDs"):
        validate(bad_adaptation)
    no_title = sample()
    no_title["adaptations"][0]["title"] = ""
    with pytest.raises(LedgerError, match="title"):
        validate(no_title)
    duplicate = sample()
    duplicate["adaptations"].append(dict(duplicate["adaptations"][0]))
    with pytest.raises(LedgerError, match="unique"):
        validate(duplicate)
    bad_reference = sample()
    bad_reference["differences"][0]["adaptation"] = "radio"
    with pytest.raises(LedgerError, match="unknown adaptation"):
        validate(bad_reference)
    missing_text = sample()
    missing_text["differences"][0]["source_version"] = ""
    with pytest.raises(LedgerError, match="source_version"):
        validate(missing_text)


def test_empty_adaptation_section_and_cli_stdout(tmp_path: Path, capsys) -> None:  # type: ignore[no-untyped-def]
    payload = sample()
    payload["differences"] = []
    assert "No differences" in markdown(summarize(validate(payload)))
    source = tmp_path / "ledger.json"
    source.write_text(json.dumps(sample()), encoding="utf-8")
    assert main([str(source), "--adaptation", "film"]) == 0
    assert "The Film" in capsys.readouterr().out
    assert main([str(tmp_path / "missing.json")]) == 2
