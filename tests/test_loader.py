import pytest

from brief_matrix.loader import TenantError, load_tenant


def test_loads_procurement_tenant(procurement_tenant_dir):
    tenant = load_tenant(procurement_tenant_dir)
    assert tenant.id == "procurement-analyst"
    assert "intro" in tenant.section_names
    assert "items" in tenant.section_names
    assert "what-this-means" in tenant.section_names
    assert "footer" in tenant.section_names
    assert tenant.sources["sources"], "expected at least one source"


def test_loader_rejects_missing_dir(tmp_path):
    missing = tmp_path / "no-such-tenant"
    with pytest.raises(TenantError):
        load_tenant(missing)


def test_loader_rejects_id_mismatch(tmp_path):
    tenant_dir = tmp_path / "mismatch-id"
    tenant_dir.mkdir()
    (tenant_dir / "config.yaml").write_text(
        "id: different-id\n"
        "name: Mismatch\n"
        "persona: A tester.\n"
        "source_registry: sources.yaml\n"
        "spec_ledger_ref: specs/\n"
        "review_target: file://nowhere/\n",
        encoding="utf-8",
    )
    (tenant_dir / "sources.yaml").write_text("sources: []\n", encoding="utf-8")
    specs = tenant_dir / "specs"
    specs.mkdir()
    (specs / "section-structure.yaml").write_text(
        "sections:\n  - name: intro\n    description: foo\n",
        encoding="utf-8",
    )
    with pytest.raises(TenantError, match="does not match directory name"):
        load_tenant(tenant_dir)


def test_loader_rejects_override_that_removes_shared_term(tmp_path):
    tenant_dir = tmp_path / "with-bad-overrides"
    tenant_dir.mkdir()
    (tenant_dir / "config.yaml").write_text(
        "id: with-bad-overrides\n"
        "name: bad overrides\n"
        "persona: A tester.\n"
        "source_registry: sources.yaml\n"
        "spec_ledger_ref: specs/\n"
        "voice_overrides: voice_overrides.yaml\n"
        "review_target: file://nowhere/\n",
        encoding="utf-8",
    )
    (tenant_dir / "sources.yaml").write_text("sources: []\n", encoding="utf-8")
    specs = tenant_dir / "specs"
    specs.mkdir()
    (specs / "section-structure.yaml").write_text(
        "sections:\n  - name: intro\n    description: foo\n",
        encoding="utf-8",
    )
    (tenant_dir / "voice_overrides.yaml").write_text(
        "extra_banned:\n  - '-leverage'\n",
        encoding="utf-8",
    )
    with pytest.raises(TenantError, match="remove shared banlist term"):
        load_tenant(tenant_dir)
