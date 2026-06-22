#!/usr/bin/env python3
"""Parse every JSON schema under schemas/ and confirm it self-validates
as a draft 2020-12 metaschema."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = REPO_ROOT / "schemas"


def main() -> int:
    if not SCHEMA_DIR.exists():
        print("no schemas/ directory; nothing to validate")
        return 0
    failed = 0
    count = 0
    for path in sorted(SCHEMA_DIR.glob("*.schema.json")):
        count += 1
        try:
            with path.open("r", encoding="utf-8") as fh:
                schema = json.load(fh)
            Draft202012Validator.check_schema(schema)
            print(f"OK    {path.name}")
        except Exception as exc:
            failed += 1
            print(f"FAIL  {path.name}\n  {exc}")
    print(f"validate_schemas: {count} scanned, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
