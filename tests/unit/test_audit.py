import json

import pytest

from tools.audit_player1_dataset import AuditError, audit_dataset, write_reports


def test_audit_fails_closed_when_required_manifest_is_missing(tmp_path):
    (tmp_path / "trajectories.jsonl").write_text("{}", encoding="utf-8")
    with pytest.raises(AuditError, match="recordings"):
        audit_dataset(tmp_path, expected_count=1)


def test_audit_writes_machine_and_human_reports(tmp_path):
    (tmp_path / "trajectories.jsonl").write_text(
        "\n".join(json.dumps({"id": str(index), "game": "unknown", "turn_count": 2}) for index in range(2)),
        encoding="utf-8",
    )
    (tmp_path / "recordings.jsonl").write_text(json.dumps({"id": "r1"}) + "\n", encoding="utf-8")
    report = audit_dataset(tmp_path, expected_count=2)
    output = tmp_path / "reports"
    write_reports(report, output)
    assert json.loads((output / "dataset-audit.json").read_text())["turns"] == 4
    assert (output / "dataset-audit.md").is_file()
