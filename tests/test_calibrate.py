from brief_matrix import calibrate
from brief_matrix.loader import load_tenant


def test_score_fixture_brief(procurement_tenant_dir, fixture_brief):
    tenant = load_tenant(procurement_tenant_dir)
    result = calibrate.score(fixture_brief, tenant)

    # Voice should pass cleanly on the fixture.
    assert result.voice_score == 1.0
    assert result.voice_hits == []

    # All four declared sections should be filled.
    assert set(result.sections_filled) == {
        "intro",
        "items",
        "what-this-means",
        "footer",
    }
    assert result.section_score == 1.0

    # Every section carries at least one inline citation.
    assert result.citation_score == 1.0


def test_score_missing_section_lowers_section_score(tmp_path, procurement_tenant_dir):
    tenant = load_tenant(procurement_tenant_dir)
    brief = tmp_path / "partial.md"
    brief.write_text(
        "## intro\n\nOne paragraph.\n\n"
        "## items\n\nAn item with [a link](https://example.invalid/x).\n",
        encoding="utf-8",
    )
    result = calibrate.score(brief, tenant)
    assert result.section_score == 0.5  # 2 of 4 sections filled
    assert result.voice_score == 1.0


def test_score_no_citations_collapses_citation_score(tmp_path, procurement_tenant_dir):
    tenant = load_tenant(procurement_tenant_dir)
    brief = tmp_path / "nocite.md"
    brief.write_text(
        "## intro\n\nNothing cited.\n\n"
        "## items\n\nStill nothing.\n\n"
        "## what-this-means\n\nStill nothing.\n\n"
        "## footer\n\nNothing.\n",
        encoding="utf-8",
    )
    result = calibrate.score(brief, tenant)
    assert result.citation_score == 0.0


def test_partial_citation_coverage_is_half(tmp_path, procurement_tenant_dir):
    # The tenant marks exactly `items` and `footer` as requires_citation.
    # Cite one of the two -> cited_count/required_count == 1/2. Pins the
    # ratio so it can't be flattened to a hardcoded 1.0.
    tenant = load_tenant(procurement_tenant_dir)
    brief = tmp_path / "partial-cite.md"
    brief.write_text(
        "## intro\n\nTheme paragraph.\n\n"
        "## items\n\nAn item with [a link](https://example.invalid/x).\n\n"
        "## what-this-means\n\nImplication.\n\n"
        "## footer\n\nRoll-up with no link.\n",
        encoding="utf-8",
    )
    result = calibrate.score(brief, tenant)
    assert result.citation_score == 0.5


def test_voice_violation_zeroes_voice_score(tmp_path, procurement_tenant_dir):
    # A banned term drives voice.passed False, which pins the else-0.0 branch
    # of voice_score (the 1.0 branch is covered by the clean fixture).
    tenant = load_tenant(procurement_tenant_dir)
    brief = tmp_path / "voice-fail.md"
    brief.write_text(
        "## intro\n\nWe must leverage the new tariff window this week.\n\n"
        "## items\n\nAn item with [a link](https://example.invalid/x).\n\n"
        "## what-this-means\n\nImplication.\n\n"
        "## footer\n\nRoll-up ([src](https://example.invalid/y)).\n",
        encoding="utf-8",
    )
    result = calibrate.score(brief, tenant)
    assert result.voice_score == 0.0
    assert result.voice_hits  # non-empty; names the banned term


def test_make_row_includes_required_fields(procurement_tenant_dir, fixture_brief):
    tenant = load_tenant(procurement_tenant_dir)
    result = calibrate.score(fixture_brief, tenant)
    row = calibrate.make_row(
        result,
        tenant_id=tenant.id,
        iso_week="2026-W34",
        brief_path="review-queue/procurement-analyst/2026-W34.md",
    )
    assert row["schema_version"] == 1
    assert row["tenant_id"] == "procurement-analyst"
    assert row["iso_week"] == "2026-W34"
    assert 0.0 <= row["voice_score"] <= 1.0
