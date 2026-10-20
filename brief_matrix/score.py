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
# A link reference definition: label, destination, optional title, nothing else.
LINK_DEF_RE = re.compile(
    r"^ {0,3}\[[^\]\n]+\]:[ \t]*(?:<[^>\n]*>|\S+)"
    r"(?:[ \t]+(?:\"[^\"\n]*\"|'[^'\n]*'|\([^)\n]*\)))?[ \t]*(?:\r?\n|$)",
    re.MULTILINE,
)
FENCE_OPEN_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
BLOCK_COMMENT_RE = re.compile(r"^ {0,3}<!--")
# An inline comment stays inside its paragraph: it cannot cross a blank line
# or a heading. A "<!--" with no "-->" in the same paragraph is literal text.
INLINE_COMMENT_RE = re.compile(
    r"<!--(?:(?!\n[ \t\r]*\n|\n {0,3}#).)*?-->", re.DOTALL
)


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
    sections = _split_by_heading(body)
    filled: list[str] = []
    for name in declared:
        content = sections.get(name.lower(), "")
        # Link definitions alone do not render any section content.
        content = LINK_DEF_RE.sub("", content)
        if content.strip():
            filled.append(name)
    return filled


def _strip_comments(body: str) -> str:
    """Remove HTML comments the way a CommonMark renderer hides them.

    A line opening with "<!--" (up to 3 spaces of indent) starts a comment
    block that ends on the first line containing "-->", or runs to the end of
    the file when unclosed. "<!-->" and "<!--->" close themselves. Elsewhere a
    comment is inline and must close within its paragraph. Fenced code is
    left alone, so a "<!--" shown in a code sample hides nothing.
    """
    out: list[str] = []
    prose: list[str] = []

    def flush() -> None:
        out.append(INLINE_COMMENT_RE.sub("", "".join(prose)))
        prose.clear()

    fence = ""
    in_comment = False
    for line in body.splitlines(keepends=True):
        if fence:
            out.append(line)
            stripped = line.strip()
            if stripped.startswith(fence) and not stripped.strip(fence[0]):
                fence = ""
            continue
        if in_comment:
            end = line.find("-->")
            if end != -1:
                in_comment = False
                prose.append(line[end + 3:])
            continue
        fence_match = FENCE_OPEN_RE.match(line)
        if fence_match:
            flush()
            fence = fence_match.group(1)
            out.append(line)
            continue
        block_match = BLOCK_COMMENT_RE.match(line)
        if block_match:
            flush()
            # Search from the "--" of "<!--" so "<!-->" counts as closed.
            end = line.find("-->", block_match.end() - 2)
            if end == -1:
                in_comment = True
            else:
                prose.append(line[:block_match.end() - 4] + line[end + 3:])
            continue
        prose.append(line)
    flush()
    return "".join(out)


def _split_by_heading(body: str) -> dict[str, str]:
    """Map lowercased H2 heading -> the text under it (until the next H2).

    A heading that appears twice keeps the text under both copies.
    """
    # Strip before splitting: a heading inside a multiline comment is hidden too.
    body = _strip_comments(body)
    parts = re.split(r"^##\s+", body, flags=re.MULTILINE)
    by_heading: dict[str, str] = {}
    for chunk in parts[1:]:
        head, _, rest = chunk.partition("\n")
        key = head.strip().lower()
        by_heading[key] = by_heading.get(key, "") + rest
    return by_heading


def _citations_per_section(
    body: str, cite_required: list[str]
) -> tuple[int, int]:
    """Citation coverage over the sections that *require* a citation.

    Returns (sections_with_at_least_one_citation, sections_that_require_one).
    Narrative sections (intro, what-this-means) are not in ``cite_required``
    and so do not drag the score down for carrying no link.
    """
    by_heading = _split_by_heading(body)
    cited = 0
    for name in cite_required:
        section_body = by_heading.get(name.lower(), "")
        if INLINE_LINK_RE.search(section_body):
            cited += 1
    return cited, len(cite_required)


def score(brief_path: str | Path, tenant: Tenant) -> CalibrationResult:
    text = Path(brief_path).read_text(encoding="utf-8")
    body, _front_matter = _strip_front_matter(text)

    voice = voice_gate.check_tenant(body, tenant)
    voice_score = 1.0 if voice.passed else 0.0

    declared = tenant.section_names
    filled = _sections_filled(body, declared)
    section_score = (len(filled) / len(declared)) if declared else 0.0

    # Only sections that the spec marks `requires_citation: true` count
    # toward citation coverage. If the spec is silent (older fixtures
    # with no flags) every section is required, preserving prior behaviour.
    cite_required = [
        s["name"]
        for s in tenant.section_structure
        if s.get("requires_citation", True)
    ]
    cited_count, required_count = _citations_per_section(body, cite_required)
    if required_count == 0 or not INLINE_LINK_RE.search(body):
        citation_score = 0.0
    else:
        citation_score = cited_count / required_count

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
