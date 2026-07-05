from __future__ import annotations

import json
import shutil
from pathlib import Path

import yaml

from brief_matrix import cli
from brief_matrix.promote import promote_brief


def _copy_tree(src: Path, dst: Path) -> None:
    shutil.copytree(src, dst)


def test_promote_moves_review_draft_and_writes_ledgers(tmp_path: Path, repo_root: Path) -> None:
    tenant_src = repo_root / "tenants" / "procurement-analyst"
    brief_src = repo_root / "review-queue" / "procurement-analyst" / "2026-W34.md"
    tenant_dst = tmp_path / "tenants" / "procurement-analyst"
    review_dst = tmp_path / "review-queue" / "procurement-analyst"
    _copy_tree(tenant_src, tenant_dst)
    review_dst.mkdir(parents=True)
    shutil.copy2(brief_src, review_dst / "2026-W34.md")

    result = promote_brief(
        tenant_dir=tenant_dst,
        brief_path=review_dst / "2026-W34.md",
        reviewer="tester",
        repo_root=tmp_path,
        notes="test promotion",
        now="2026-07-05T16:00:00+00:00",
    )

    assert not (review_dst / "2026-W34.md").exists()
    assert result.destination == tmp_path / "briefs" / "procurement-analyst" / "2026-W34.md"
    front = yaml.safe_load(result.destination.read_text(encoding="utf-8").split("---", 2)[1])
    assert front["status"] == "approved"
    assert front["reviewer"] == "tester"

    calibration_rows = list((tmp_path / "data" / "ledger").glob("*.jsonl"))
    assert len(calibration_rows) == 1
    calibration = json.loads(calibration_rows[0].read_text(encoding="utf-8").splitlines()[0])
    assert calibration["brief_path"] == "briefs/procurement-analyst/2026-W34.md"
    assert calibration["voice_score"] == 1.0

    review_line = (tmp_path / "data" / "reviews" / "review-records.jsonl").read_text(encoding="utf-8").splitlines()[0]
    review = json.loads(review_line)
    assert review["from_status"] == "pending-review"
    assert review["to_status"] == "approved"


def test_promote_cli_reports_missing_brief_cleanly(capsys, procurement_tenant_dir: Path, tmp_path: Path) -> None:
    rc = cli.main([
        "promote",
        "--tenant",
        str(procurement_tenant_dir),
        "--brief",
        str(tmp_path / "missing.md"),
        "--reviewer",
        "tester",
    ])
    assert rc == 1
    err = capsys.readouterr().err
    assert "promote: FAIL" in err
    assert "brief not found" in err
