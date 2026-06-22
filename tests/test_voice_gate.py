from brief_matrix import voice_gate


def test_clean_text_passes():
    result = voice_gate.check("This is a plain factual sentence about a port.")
    assert result.passed is True
    assert result.hits == []


def test_banned_term_fails():
    result = voice_gate.check("We must leverage the new tariff window.")
    assert result.passed is False
    assert "leverage" in result.hits


def test_tenant_overrides_extend_banlist():
    extras = ["paradigm-shift"]
    result = voice_gate.check(
        "The week is a paradigm-shift in port operations.", extras
    )
    assert result.passed is False
    assert "paradigm-shift" in result.hits


def test_word_boundary_does_not_match_substring():
    # "delve" is banned; "delivery" should not match.
    result = voice_gate.check("Delivery times rose at Long Beach.")
    assert result.passed is True
    assert result.hits == []


def test_merged_banlist_is_union():
    extras = ["extra-term"]
    merged = voice_gate.merged_banlist(extras)
    assert "extra-term" in merged
    for shared in voice_gate.BANNED_FAIL:
        assert shared in merged
