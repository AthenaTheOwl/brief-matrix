"""Three-axis calibration scorer.

Reads a brief Markdown file plus a loaded Tenant; returns a row shaped
by schemas/calibration-run.schema.json.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from brief_matrix.loader import Tenant
from brief_matrix import voice_gate


FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
H2_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
INLINE_LINK_RE = re.compile(r"\[[^\]]+\]\((https?://[^)\s]+)\)")


@dataclass
class CalibrationResult:
    voice_score: float
    citation_score: float
    section_score: float
    voice_hits: list[str]
    sections_declared: list[str]
    sections_filled: list[str]


def _strip_front_matter(text: str) -> tuple[str, dict[str, Any]]:
    import yaml

    match = FRONT_MATTER_RE.match(text)
    if not match:
        return text, {}
    fm_raw = match.group(1)
    body = text[match.end():]
    try:
        fm = yaml.safe_load(fm_raw) or {}
    except yaml.YAMLError:
        fm = {}
    return body, (fm if isinstance(fm, dict) else {})


def _sections_filled(body: str, declared: list[str]) -> list[str]:
    headings = [h.strip().lower() for h in H2_RE.findall(body)]
    filled: list[str] = []
    for name in declared:
        if name.lower() in headings:
            filled.append(name)
    return filled


def _citations_per_section(body: str, declared: list[str]) -> tuple[int, int]:
    """Return (sections_with_at_least_one_citation, total_declared)."""
    parts = re.split(r"^##\s+", body, flags=re.MULTILINE)
    by_heading: dict[str, str] = {}
    for chunk in parts[1:]:
        head, _, rest = chunk.partition("\n")
        by_heading[head.strip().lower()] = rest

    declared_lower = [d.lower() for d in declared]
    cited = 0
    for d in declared_lower:
        section_body = by_heading.get(d, "")
        if INLINE_LINK_RE.search(section_body):
            cited += 1
    return cited, len(declared)


def score(brief_path: str | Path, tenant: Tenant) -> CalibrationResult:
    text = Path(brief_path).read_text(encoding="utf-8")
    body, _front_matter = _strip_front_matter(text)

    voice = voice_gate.check_tenant(body, tenant)
    voice_score = 1.0 if voice.passed else 0.0

    declared = tenant.section_names
    filled = _sections_filled(body, declared)
    section_score = (len(filled) / len(declared)) if declared else 0.0

    cited_count, declared_count = _citations_per_section(body, declared)
    if declared_count == 0 or not INLINE_LINK_RE.search(body):
        citation_score = 0.0
    else:
        citation_score = cited_count / declared_count

    return CalibrationResult(
        voice_score=voice_score,
        citation_score=round(citation_score, 4),
        section_score=round(section_score, 4),
        voice_hits=voice.hits,
        sections_declared=declared,
        sections_filled=filled,
    )


def make_row(
    result: CalibrationResult,
    *,
    tenant_id: str,
    iso_week: str,
    brief_path: str,
    notes: str | None = None,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "schema_version": 1,
        "tenant_id": tenant_id,
        "iso_week": iso_week,
        "brief_path": brief_path,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "voice_score": result.voice_score,
        "citation_score": result.citation_score,
        "section_score": result.section_score,
        "voice_hits": result.voice_hits,
        "sections_declared": result.sections_declared,
        "sections_filled": result.sections_filled,
    }
    if notes:
        row["notes"] = notes
    return row
