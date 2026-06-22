#!/usr/bin/env python3
"""Standalone voice-lint script. Mirrors src/brief_matrix/voice_gate.BANNED_FAIL
for code paths that want to run lint without importing the package."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from brief_matrix.voice_gate import BANNED_FAIL, check  # noqa: E402


SCAN_GLOBS: tuple[str, ...] = (
    "briefs/**/*.md",
    "review-queue/**/*.md",
)


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    paths: list[Path] = []
    if argv:
        paths = [Path(a) for a in argv]
    else:
        for pattern in SCAN_GLOBS:
            paths.extend(REPO_ROOT.glob(pattern))

    failed = 0
    for path in paths:
        if not path.exists() or path.is_dir():
            continue
        text = path.read_text(encoding="utf-8")
        result = check(text)
        if not result.passed:
            failed += 1
            print(f"FAIL  {path}")
            for hit in result.hits:
                print(f"      hit: {hit}")
        else:
            print(f"OK    {path}")
    print(f"voice_lint: {len(paths)} scanned, {failed} failed, "
          f"banlist={len(BANNED_FAIL)} terms")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
