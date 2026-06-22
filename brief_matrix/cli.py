"""BriefMatrix CLI: validate, calibrate, ledger."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Sequence

from brief_matrix import ledger, score as score_mod
from brief_matrix.loader import TenantError, load_tenant


ISO_WEEK_RE = re.compile(r"(\d{4}-W\d{2})")

REPO_ROOT = Path(__file__).resolve().parents[1]
TENANTS_DIR = REPO_ROOT / "tenants"


def _default_tenant() -> str | None:
    """Return the sole tenant dir under tenants/, or None if ambiguous/absent.

    When exactly one tenant directory exists it is the canonical default, so
    `python -m brief_matrix validate` works with no args against the bundled
    fixture tenant.
    """
    if not TENANTS_DIR.is_dir():
        return None
    candidates = [
        d for d in sorted(TENANTS_DIR.iterdir()) if (d / "config.yaml").exists()
    ]
    if len(candidates) == 1:
        return str(candidates[0])
    return None


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="brief-matrix",
        description="Multi-tenant brief platform — validate, calibrate, ledger.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_validate = sub.add_parser("validate", help="Validate a tenant directory.")
    p_validate.add_argument(
        "--tenant",
        default=None,
        help="Path to tenant dir. Defaults to the sole tenant under tenants/.",
    )

    p_calibrate = sub.add_parser("calibrate", help="Score a brief and append to ledger.")
    p_calibrate.add_argument("--tenant", required=True, help="Path to tenant dir.")
    p_calibrate.add_argument("--brief", required=True, help="Path to brief markdown.")
    p_calibrate.add_argument(
        "--iso-week",
        help="ISO week tag for the row. Inferred from the brief filename if omitted.",
    )
    p_calibrate.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the row without writing to data/ledger/.",
    )
    p_calibrate.add_argument("--notes", help="Optional note recorded on the row.")

    p_ledger = sub.add_parser("ledger", help="Print all ledger rows.")
    p_ledger.add_argument(
        "--path",
        help="Override the default data/ledger/ directory (used by tests).",
    )

    return parser


def _infer_iso_week(brief_path: str) -> str | None:
    name = Path(brief_path).stem
    match = ISO_WEEK_RE.search(name)
    return match.group(1) if match else None


def cmd_validate(args: argparse.Namespace) -> int:
    tenant_dir = args.tenant or _default_tenant()
    if tenant_dir is None:
        print(
            "validate: FAIL  no --tenant given and could not pick a default "
            "(zero or multiple tenants under tenants/).",
            file=sys.stderr,
        )
        return 1
    try:
        tenant = load_tenant(tenant_dir)
    except TenantError as exc:
        print(f"validate: FAIL\n{exc}", file=sys.stderr)
        return 1
    print(
        f"validate: OK  tenant={tenant.id}  "
        f"sections={len(tenant.section_structure)}  "
        f"sources={len(tenant.sources.get('sources', []))}"
    )
    return 0


def cmd_calibrate(args: argparse.Namespace) -> int:
    try:
        tenant = load_tenant(args.tenant)
    except TenantError as exc:
        print(f"calibrate: FAIL (tenant)\n{exc}", file=sys.stderr)
        return 1

    brief_path = Path(args.brief)
    if not brief_path.exists():
        print(f"calibrate: FAIL  brief not found: {brief_path}", file=sys.stderr)
        return 1

    iso_week = args.iso_week or _infer_iso_week(args.brief)
    if not iso_week:
        print(
            "calibrate: FAIL  could not infer --iso-week; pass it explicitly.",
            file=sys.stderr,
        )
        return 1

    result = score_mod.score(brief_path, tenant)
    row = score_mod.make_row(
        result,
        tenant_id=tenant.id,
        iso_week=iso_week,
        brief_path=str(brief_path).replace("\\", "/"),
        notes=args.notes,
    )

    if args.dry_run:
        import json as _json

        print(_json.dumps(row, indent=2, sort_keys=True))
        return 0

    out = ledger.append(row)
    print(
        f"calibrate: OK  voice={result.voice_score:.2f}  "
        f"cit={result.citation_score:.2f}  sec={result.section_score:.2f}  "
        f"wrote={out}"
    )
    return 0


def cmd_ledger(args: argparse.Namespace) -> int:
    ledger_dir = Path(args.path) if args.path else None
    rows = ledger.read_all(ledger_dir=ledger_dir)
    if not rows:
        print("ledger: (empty)")
        return 0
    for row in rows:
        print(ledger.format_row_line(row))
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    handlers = {
        "validate": cmd_validate,
        "calibrate": cmd_calibrate,
        "ledger": cmd_ledger,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
