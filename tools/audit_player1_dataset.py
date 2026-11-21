"""Title-neutral Player-1 dataset metadata audit.

The utility intentionally audits metadata files only. It never selects a game
or infers unavailable recording contents.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

EXPECTED_TRAJECTORIES = 6044


class AuditError(RuntimeError):
    pass


def _read_json_lines(path: Path) -> list[dict[str, Any]]:
    records = []
    with path.open(encoding="utf-8") as file:
        for line_number, line in enumerate(file, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                raise AuditError(f"invalid JSON at {path}:{line_number}") from error
            if not isinstance(record, dict):
                raise AuditError(f"record at {path}:{line_number} is not an object")
            records.append(record)
    return records


def audit_dataset(root: Path, expected_count: int = EXPECTED_TRAJECTORIES) -> dict[str, Any]:
    if not root.is_dir():
        raise AuditError(f"dataset directory does not exist: {root}")
    jsonl_files = sorted(root.rglob("*.jsonl"))
    if not jsonl_files:
        raise AuditError("no metadata JSONL files found")
    trajectory_files = [
        path
        for path in jsonl_files
        if path.name != "recordings.jsonl" and "trajector" in path.name.lower()
    ]
    if not trajectory_files:
        raise AuditError("required trajectory metadata file is missing")
    recordings_path = root / "recordings.jsonl"
    if not recordings_path.is_file():
        raise AuditError("required recordings.jsonl manifest is missing")

    trajectories = [record for path in trajectory_files for record in _read_json_lines(path)]
    recordings = _read_json_lines(recordings_path)
    if len(trajectories) != expected_count:
        raise AuditError(f"trajectory count {len(trajectories)} does not match expected {expected_count}")

    labels = Counter(str(record.get("game", record.get("game_label", "<unknown>"))) for record in trajectories)
    modes = Counter(str(record.get("mode", "<unknown>")) for record in trajectories)
    sources = Counter(str(record.get("source", "<unknown>")) for record in trajectories)
    turns = sum(
        len(record.get("turns", [])) if isinstance(record.get("turns"), list) else int(record.get("turn_count", 0))
        for record in trajectories
    )
    trajectory_ids = [record.get("trajectory_id", record.get("id")) for record in trajectories]
    duplicate_ids = sorted({value for value in trajectory_ids if value is not None and trajectory_ids.count(value) > 1})
    return {
        "dataset_root": str(root),
        "audited_at": datetime.now(UTC).isoformat(),
        "trajectory_records": len(trajectories),
        "recording_manifest_records": len(recordings),
        "turns": turns,
        "estimated_control_seconds": turns * 0.2,
        "by_game_label": dict(labels),
        "by_mode": dict(modes),
        "by_source": dict(sources),
        "duplicate_trajectory_ids": duplicate_ids,
        "limitations": ["Metadata does not establish unavailable source-video contents."],
    }


def write_reports(report: dict[str, Any], output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "dataset-audit.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    lines = [
        "# Player-1 Dataset Audit",
        "",
        f"- Trajectory records: {report['trajectory_records']}",
        f"- Recording manifest records: {report['recording_manifest_records']}",
        f"- Turns: {report['turns']}",
        f"- Estimated control seconds (200 ms/turn): {report['estimated_control_seconds']}",
        "",
        "## Limitations",
        *[f"- {item}" for item in report["limitations"]],
    ]
    (output / "dataset-audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    report = audit_dataset(args.dataset)
    write_reports(report, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
