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


def test_show_reads_committed_ledger(capsys, repo_root):
    rc = cli.main(["show", "--path", str(repo_root / "data" / "ledger")])
    assert rc == 0
    out = capsys.readouterr().out
    assert "calibration rollup" in out
    assert "procurement-analyst" in out
    assert "headline:" in out
    # The committed row is clean on all axes.
    assert "ready to promote" in out


def test_show_ranks_best_first(capsys, tmp_path):
    from brief_matrix import ledger

    led = tmp_path / "ledger"
    led.mkdir()
    rows = [
        {
            "schema_version": 1,
            "tenant_id": "weak-tenant",
            "iso_week": "2026-W10",
            "brief_path": "x/weak.md",
            "created_at": "2026-03-01T00:00:00+00:00",
            "voice_score": 0.0,
            "citation_score": 0.5,
            "section_score": 0.5,
        },
        {
            "schema_version": 1,
            "tenant_id": "strong-tenant",
            "iso_week": "2026-W11",
            "brief_path": "x/strong.md",
            "created_at": "2026-03-08T00:00:00+00:00",
            "voice_score": 1.0,
            "citation_score": 1.0,
            "section_score": 1.0,
        },
    ]
    for r in rows:
        ledger.append(r, ledger_dir=led)

    rc = cli.main(["show", "--path", str(led)])
    assert rc == 0
    out = capsys.readouterr().out
    # strong-tenant must rank #1 (appear before weak-tenant in the table).
    assert out.index("strong-tenant") < out.index("weak-tenant")
    assert "strong-tenant 2026-W11" in out  # headline names the top brief


def test_calibrate_brief_is_directory(capsys, procurement_tenant_dir):
    # A directory passed as --brief must fail cleanly, not raise
    # IsADirectoryError/PermissionError out of score().
    rc = cli.main(
        [
            "calibrate",
            "--tenant",
            str(procurement_tenant_dir),
            "--brief",
            str(procurement_tenant_dir),
            "--iso-week",
            "2026-W25",
            "--dry-run",
        ]
    )
    assert rc == 1
    err = capsys.readouterr().err
    assert "calibrate: FAIL" in err
    assert "brief not found" in err


def test_validate_malformed_yaml(capsys, tmp_path):
    # A malformed config.yaml must surface as a clean FAIL, not a raw
    # yaml.scanner.ScannerError trace.
    tenant_dir = tmp_path / "broken"
    tenant_dir.mkdir()
    (tenant_dir / "config.yaml").write_text(
        "id: broken\nname: [unclosed\n  bracket: yes\n", encoding="utf-8"
    )
    rc = cli.main(["validate", "--tenant", str(tenant_dir)])
    assert rc == 1
    err = capsys.readouterr().err
    assert "validate: FAIL" in err
    assert "invalid YAML" in err


def test_ledger_corrupt_line(capsys, tmp_path):
    # A corrupt append-only ledger line must fail cleanly, not raise
    # json.decoder.JSONDecodeError.
    led = tmp_path / "ledger"
    led.mkdir()
    (led / "2026-W01-x-calibration-run.jsonl").write_text(
        "{ not valid json }\n", encoding="utf-8"
    )
    rc = cli.main(["ledger", "--path", str(led)])
    assert rc == 1
    err = capsys.readouterr().err
    assert "ledger: FAIL" in err
    assert "not valid JSON" in err


def test_show_corrupt_line(capsys, tmp_path):
    led = tmp_path / "ledger"
    led.mkdir()
    (led / "2026-W01-x-calibration-run.jsonl").write_text(
        "{ not valid json }\n", encoding="utf-8"
    )
    rc = cli.main(["show", "--path", str(led)])
    assert rc == 1
    err = capsys.readouterr().err
    assert "show: FAIL" in err
    assert "not valid JSON" in err


def test_show_empty_ledger(capsys, tmp_path):
    rc = cli.main(["show", "--path", str(tmp_path / "empty")])
    assert rc == 0
    out = capsys.readouterr().out
    assert "empty" in out


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
