"""Rollup renderer over calibration ledger rows.

Reads rows via `ledger.read_all` and emits a Markdown table the
reviewer can paste into a status doc. v0.1 ships only the
``markdown_table`` shape; richer dashboards land in spec 0003.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from brief_matrix import ledger


def markdown_table(rows: Iterable[dict[str, Any]]) -> str:
    """Render rows as a 5-column Markdown table.

    Columns: iso_week, tenant_id, voice, citation, section. Rows sort
    by (tenant_id, iso_week) so per-tenant trajectories read top-down.
    """
    rows_list = sorted(
        rows,
        key=lambda r: (r.get("tenant_id", ""), r.get("iso_week", "")),
    )
    header = "| iso_week | tenant_id | voice | citation | section |"
    sep = "|---|---|---|---|---|"
    body_lines = []
    for r in rows_list:
        body_lines.append(
            f"| {r['iso_week']} | {r['tenant_id']} | "
            f"{r['voice_score']:.2f} | {r['citation_score']:.2f} | "
            f"{r['section_score']:.2f} |"
        )
    if not body_lines:
        body_lines.append("| _no rows_ |  |  |  |  |")
    return "\n".join([header, sep, *body_lines])


def summary(ledger_dir: Path | None = None) -> str:
    """Read the on-disk ledger and emit a Markdown table."""
    rows = ledger.read_all(ledger_dir=ledger_dir)
    return markdown_table(rows)


def composite(row: dict[str, Any]) -> float:
    """Mean of the three axis scores. The single number a row ranks on."""
    return (
        float(row["voice_score"])
        + float(row["citation_score"])
        + float(row["section_score"])
    ) / 3.0


def ranked(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Rows sorted by composite score, best first.

    Ties break on iso_week (newer first) so a fresh clean brief outranks
    an older one with the same scores.
    """
    return sorted(
        rows,
        key=lambda r: (composite(r), r.get("iso_week", "")),
        reverse=True,
    )
