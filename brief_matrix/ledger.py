"""Calibration ledger I/O. JSONL at data/ledger/, append-only."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from brief_matrix.loader import REPO_ROOT, SCHEMA_DIR


LEDGER_DIR = REPO_ROOT / "data" / "ledger"


def _schema() -> dict[str, Any]:
    with (SCHEMA_DIR / "calibration-run.schema.json").open("r", encoding="utf-8") as fh:
        return json.load(fh)


def validate_row(row: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(_schema())
    return [e.message for e in validator.iter_errors(row)]


def row_filename(row: dict[str, Any]) -> str:
    return f"{row['iso_week']}-{row['tenant_id']}-calibration-run.jsonl"


def _dump_row(row: dict[str, Any]) -> str:
    return json.dumps(row, sort_keys=True, separators=(",", ":"))


def append(row: dict[str, Any], *, ledger_dir: Path | None = None) -> Path:
    errors = validate_row(row)
    if errors:
        raise ValueError("invalid calibration row:\n  - " + "\n  - ".join(errors))
    target_dir = ledger_dir or LEDGER_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    out = target_dir / row_filename(row)
    line = _dump_row(row) + "\n"
    with out.open("a", encoding="utf-8") as fh:
        fh.write(line)
    return out


def read_all(*, ledger_dir: Path | None = None) -> list[dict[str, Any]]:
    target_dir = ledger_dir or LEDGER_DIR
    if not target_dir.exists():
        return []
    rows: list[dict[str, Any]] = []
    for path in sorted(target_dir.glob("*.jsonl")):
        with path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                errors = validate_row(row)
                if errors:
                    raise ValueError(
                        f"{path}: invalid calibration row:\n  - "
                        + "\n  - ".join(errors)
                    )
                rows.append(row)
    rows.sort(key=lambda r: r.get("created_at", ""))
    return rows


def format_row_line(row: dict[str, Any]) -> str:
    return (
        f"{row['iso_week']}  {row['tenant_id']:<28}  "
        f"voice={row['voice_score']:.2f}  "
        f"cit={row['citation_score']:.2f}  "
        f"sec={row['section_score']:.2f}  "
        f"{row['brief_path']}"
    )
