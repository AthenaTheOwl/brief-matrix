#!/usr/bin/env python3
"""Walk tenants/ and validate each tenant against the tenant schema +
loader rules. Exit zero if every tenant validates."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from brief_matrix.loader import TenantError, load_tenant  # noqa: E402


def main() -> int:
    tenants_dir = REPO_ROOT / "tenants"
    if not tenants_dir.exists():
        print("no tenants/ directory; nothing to validate")
        return 0

    failed = 0
    count = 0
    for path in sorted(tenants_dir.iterdir()):
        if not path.is_dir() or path.name.startswith("."):
            continue
        count += 1
        try:
            tenant = load_tenant(path)
            print(
                f"OK    {tenant.id:<32} sections={len(tenant.section_structure)} "
                f"sources={len(tenant.sources.get('sources', []))}"
            )
        except TenantError as exc:
            failed += 1
            print(f"FAIL  {path.name}\n  {exc}")
    print(f"validate_tenants: {count} scanned, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
