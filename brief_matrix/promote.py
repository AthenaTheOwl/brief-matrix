"""Promotion workflow: move an approved draft into briefs/ and record the decision."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

from brief_matrix import ledger, score as score_mod
from brief_matrix.loader import REPO_ROOT, SCHEMA_DIR, Tenant, load_tenant

FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


class PromoteError(Exception):
    """Raised when a draft cannot be promoted cleanly."""


@dataclass(frozen=True)
class PromotionResult:
    tenant_id: str
    iso_week: str
    destination: Path
    calibration_path: Path
    review_record_path: Path


def _now_iso(now: str | None = None) -> str:
    return now or datetime.now(timezone.utc).isoformat(timespec="seconds")


def _read_markdown(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    match = FRONT_MATTER_RE.match(text)
    if not match:
        return {}, text
    raw = match.group(1)
    try:
        fm = yaml.safe_load(raw) or {}
    except yaml.YAMLError as exc:
        raise PromoteError(f"{path}: invalid front matter: {exc}") from exc
    if not isinstance(fm, dict):
        raise PromoteError(f"{path}: front matter must be a mapping")
    return fm, text[match.end():]


def _dump_markdown(front_matter: dict[str, Any], body: str) -> str:
    raw = yaml.safe_dump(front_matter, sort_keys=False, allow_unicode=False).strip()
    return f"---\n{raw}\n---\n\n{body.lstrip()}"


def _infer_iso_week(path: Path, front_matter: dict[str, Any]) -> str:
    value = front_matter.get("iso_week")
    if isinstance(value, str) and re.fullmatch(r"\d{4}-W\d{2}", value):
        return value
    match = re.search(r"(\d{4}-W\d{2})", path.stem)
    if match:
        return match.group(1)
    raise PromoteError("could not infer iso_week from front matter or filename")


def _tenant_review_dir(repo_root: Path, tenant: Tenant) -> Path:
    return repo_root / "review-queue" / tenant.id


def _tenant_brief_dir(repo_root: Path, tenant: Tenant) -> Path:
    return repo_root / "briefs" / tenant.id


def _review_record_schema() -> dict[str, Any]:
    with (SCHEMA_DIR / "review-record.schema.json").open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _append_review_record(path: Path, row: dict[str, Any]) -> Path:
    errors = sorted(
        Draft202012Validator(_review_record_schema()).iter_errors(row),
        key=lambda error: list(error.path),
    )
    if errors:
        bullets = "\n  - ".join(error.message for error in errors)
        raise PromoteError(f"invalid review record:\n  - {bullets}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
    return path


def _relative_for_row(path: Path, repo_root: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return path.as_posix()


def promote_brief(
    *,
    tenant_dir: str | Path,
    brief_path: str | Path,
    reviewer: str,
    repo_root: Path | None = None,
    notes: str | None = None,
    now: str | None = None,
) -> PromotionResult:
    """Promote one pending-review draft into briefs/<tenant>/."""
    root = (repo_root or REPO_ROOT).resolve()
    tenant = load_tenant(tenant_dir)
    source = Path(brief_path).resolve()
    if not source.is_file():
        raise PromoteError(f"brief not found: {source}")
    try:
        source.relative_to(_tenant_review_dir(root, tenant).resolve())
    except ValueError as exc:
        raise PromoteError(f"brief must live under review-queue/{tenant.id}/") from exc

    front_matter, body = _read_markdown(source)
    from_status = str(front_matter.get("status", "pending-review"))
    if from_status != "pending-review":
        raise PromoteError(f"brief status must be pending-review, got {from_status!r}")
    iso_week = _infer_iso_week(source, front_matter)

    result = score_mod.score(source, tenant)
    if result.voice_score < 1.0:
        raise PromoteError("voice gate failed: " + ", ".join(result.voice_hits))
    if result.citation_score < 1.0 or result.section_score < 1.0:
        raise PromoteError(
            f"calibration failed: citation={result.citation_score:.2f} section={result.section_score:.2f}"
        )

    destination = _tenant_brief_dir(root, tenant) / source.name
    if destination.exists():
        raise PromoteError(f"destination already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    front_matter["status"] = "approved"
    front_matter["reviewer"] = reviewer
    front_matter["promoted_at"] = _now_iso(now)
    destination.write_text(_dump_markdown(front_matter, body), encoding="utf-8", newline="\n")
    source.unlink()

    promoted_result = score_mod.score(destination, tenant)
    calibration_row = score_mod.make_row(
        promoted_result,
        tenant_id=tenant.id,
        iso_week=iso_week,
        brief_path=_relative_for_row(destination, root),
        notes=notes or f"Promoted by {reviewer}.",
    )
    calibration_path = ledger.append(calibration_row, ledger_dir=root / "data" / "ledger")

    review_row: dict[str, Any] = {
        "tenant_id": tenant.id,
        "iso_week": iso_week,
        "from_status": from_status,
        "to_status": "approved",
        "reviewer": reviewer,
        "decided_at": _now_iso(now),
    }
    if notes:
        review_row["notes"] = notes
    review_path = _append_review_record(root / "data" / "reviews" / "review-records.jsonl", review_row)
    return PromotionResult(
        tenant_id=tenant.id,
        iso_week=iso_week,
        destination=destination,
        calibration_path=calibration_path,
        review_record_path=review_path,
    )
