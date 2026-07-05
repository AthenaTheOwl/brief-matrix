from __future__ import annotations

from brief_matrix.loader import load_tenant
from brief_matrix.voice_gate import check_tenant


def test_second_tenant_loads_with_divergent_sections(repo_root):
    tenant = load_tenant(repo_root / "tenants" / "municipal-budget-watch")
    assert tenant.id == "municipal-budget-watch"
    assert tenant.section_names == ["agenda-risk", "cash-impact", "next-check"]


def test_tenant_voice_overrides_are_isolated(repo_root):
    procurement = load_tenant(repo_root / "tenants" / "procurement-analyst")
    municipal = load_tenant(repo_root / "tenants" / "municipal-budget-watch")
    text = "The phrase kitchen-table appears in this sentence."

    assert check_tenant(text, municipal).passed is False
    assert check_tenant(text, procurement).passed is True
    assert check_tenant("We must leverage this docket.", municipal).passed is False
    assert check_tenant("We must leverage this docket.", procurement).passed is False
