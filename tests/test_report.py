import pytest

from brief_matrix import report


def test_composite_is_mean_of_three_axes():
    # Pins the /3.0 divisor: 1.0 + 0.5 + 0.0 over three axes == 0.5.
    # A /2.0 mutation would read 0.75 and fail this.
    row = {
        "voice_score": 1.0,
        "citation_score": 0.5,
        "section_score": 0.0,
    }
    assert report.composite(row) == pytest.approx(0.5)
