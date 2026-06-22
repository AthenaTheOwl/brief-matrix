import json

import pytest

from brief_matrix import cli


def test_validate_ok(capsys, procurement_tenant_dir):
    rc = cli.main(["validate", "--tenant", str(procurement_tenant_dir)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "validate: OK" in out


def test_validate_missing_tenant(capsys, tmp_path):
    rc = cli.main(["validate", "--tenant", str(tmp_path / "no-such")])
    assert rc == 1
    err = capsys.readouterr().err
    assert "validate: FAIL" in err


def test_calibrate_dry_run(capsys, procurement_tenant_dir, fixture_brief):
    rc = cli.main(
        [
            "calibrate",
            "--tenant",
            str(procurement_tenant_dir),
            "--brief",
            str(fixture_brief),
            "--dry-run",
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out
    row = json.loads(out)
    assert row["tenant_id"] == "procurement-analyst"
    assert row["iso_week"] == "2026-W34"
    assert row["voice_score"] == 1.0


def test_ledger_prints_checked_in_rows(capsys, repo_root):
    rc = cli.main(["ledger", "--path", str(repo_root / "data" / "ledger")])
    assert rc == 0
    out = capsys.readouterr().out
    assert "procurement-analyst" in out


def test_calibrate_writes_to_temp_ledger(
    tmp_path, procurement_tenant_dir, fixture_brief, monkeypatch
):
    """Smoke test that --tenant + --brief produce a valid ledger row."""
    from brief_matrix import ledger

    monkeypatch.setattr(ledger, "LEDGER_DIR", tmp_path / "ledger")
    rc = cli.main(
        [
            "calibrate",
            "--tenant",
            str(procurement_tenant_dir),
            "--brief",
            str(fixture_brief),
            "--notes",
            "test-run",
        ]
    )
    assert rc == 0
    rows = list((tmp_path / "ledger").glob("*.jsonl"))
    assert len(rows) == 1
    with rows[0].open("r", encoding="utf-8") as fh:
        row = json.load(fh)
    assert row["tenant_id"] == "procurement-analyst"
    assert row["notes"] == "test-run"
