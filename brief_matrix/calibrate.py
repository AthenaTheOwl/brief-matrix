"""Back-compat alias for brief_matrix.score.

Kept so existing imports (`from brief_matrix import calibrate`) and
tests keep working after score.py became the canonical module.
"""

from brief_matrix.score import (  # noqa: F401
    CalibrationResult,
    FRONT_MATTER_RE,
    H2_RE,
    INLINE_LINK_RE,
    make_row,
    score,
)
