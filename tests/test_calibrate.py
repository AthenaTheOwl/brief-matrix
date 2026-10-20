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


def test_empty_section_headings_do_not_count_as_filled(tmp_path, procurement_tenant_dir):
    tenant = load_tenant(procurement_tenant_dir)
    brief = tmp_path / "empty-sections.md"
    brief.write_text(
        "## intro\n\n## items\n\n## what-this-means\n\n## footer\n",
        encoding="utf-8",
    )
    result = calibrate.score(brief, tenant)
    assert result.sections_filled == []
    assert result.section_score == 0.0


def test_editorial_comments_do_not_complete_a_section(tmp_path, procurement_tenant_dir):
    tenant = load_tenant(procurement_tenant_dir)
    brief = tmp_path / "comments.md"
    brief.write_text(
        "## intro\n\n<!-- Draft this later. -->\n\n"
        "## items\n\nA sourced item [reference](https://example.invalid/x).\n",
        encoding="utf-8",
    )
    result = calibrate.score(brief, tenant)
    assert result.sections_filled == ["items"]
    assert result.section_score == 0.25


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


def test_hidden_comment_heading_is_not_a_filled_section():
    from brief_matrix.score import _sections_filled

    draft = "<!--\n## intro\nDraft only, invisible when rendered.\n-->\n"
    assert _sections_filled(draft, ["intro"]) == []


def test_reference_definition_alone_is_not_a_filled_section():
    from brief_matrix.score import _sections_filled

    assert _sections_filled("## intro\n[ref]: https://example.invalid/x\n", ["intro"]) == []


def test_unclosed_comment_marker_mid_line_does_not_hide_later_sections():
    from brief_matrix.score import _sections_filled

    body = (
        "## intro\n\nUse `<!--` to open an HTML comment.\n\n"
        "## items\n\nAn item [a](https://example.invalid/a).\n"
    )
    assert _sections_filled(body, ["intro", "items"]) == ["intro", "items"]


def test_unclosed_comment_opening_a_line_hides_the_rest():
    from brief_matrix.score import _sections_filled

    body = "## intro\n\nVisible.\n\n<!--\n## items\n\nDraft only.\n"
    assert _sections_filled(body, ["intro", "items"]) == ["intro"]


def test_indented_unclosed_comment_hides_the_rest_but_code_block_does_not():
    from brief_matrix.score import _sections_filled

    three = "## intro\n\nVisible.\n\n   <!--\n## items\n\nDraft.\n"
    assert _sections_filled(three, ["intro", "items"]) == ["intro"]
    four = (
        "## intro\n\nVisible.\n\n    <!--\n\n"
        "## items\n\nReal [a](https://example.invalid/a).\n"
    )
    assert _sections_filled(four, ["intro", "items"]) == ["intro", "items"]


def test_mid_line_marker_does_not_pair_with_a_later_comment(tmp_path, procurement_tenant_dir):
    tenant = load_tenant(procurement_tenant_dir)
    brief = tmp_path / "marker.md"
    brief.write_text(
        "## intro\n\nUse `<!--` to open an HTML comment.\n\n"
        "## items\n\nAn item [a](https://example.invalid/a).\n\n"
        "## what-this-means\n\nMeaning [b](https://example.invalid/b).\n\n"
        "## footer\n\n<!-- editor: confirm sources before Friday -->\n"
        "Sources [c](https://example.invalid/c).\n",
        encoding="utf-8",
    )
    result = calibrate.score(brief, tenant)
    assert result.section_score == 1.0
    assert result.citation_score == 1.0


def test_mid_line_marker_does_not_pair_with_a_later_arrow():
    from brief_matrix.score import _sections_filled

    body = (
        "## intro\n\nUse `<!--` to open an HTML comment.\n\n"
        "## items\n\nAn item [a](https://example.invalid/a).\n\n"
        "## what-this-means\n\nPrices moved Q3 --> Q4.\n"
    )
    names = ["intro", "items", "what-this-means"]
    assert _sections_filled(body, names) == names


def test_comment_marker_in_fenced_code_hides_nothing():
    from brief_matrix.score import _sections_filled

    body = (
        "## intro\n\nExample markup:\n\n```html\n<!--\n```\n\n"
        "## items\n\nAn item [a](https://example.invalid/a).\n"
    )
    assert _sections_filled(body, ["intro", "items"]) == ["intro", "items"]


def test_short_empty_comments_close_themselves():
    from brief_matrix.score import _sections_filled

    for marker in ("<!-->", "<!--->"):
        body = f"## intro\n\n{marker}\n\n## items\n\nx\n"
        assert _sections_filled(body, ["intro", "items"]) == ["items"]


def test_bracketed_prose_is_not_a_link_definition():
    from brief_matrix.score import _sections_filled

    body = (
        "## intro\n\n[Update]: the agency re-bid the contract.\n\n"
        "## footer\n\n[Next]: see [packet](https://example.invalid/p).\n"
    )
    assert _sections_filled(body, ["intro", "footer"]) == ["intro", "footer"]
    titled = '## intro\n[ref]: <https://example.invalid/x> "Title"\n'
    assert _sections_filled(titled, ["intro"]) == []


def test_duplicate_heading_keeps_content_from_both_copies():
    from brief_matrix.score import _sections_filled

    assert _sections_filled("## intro\n\nReal text.\n\n## intro\n", ["intro"]) == ["intro"]
