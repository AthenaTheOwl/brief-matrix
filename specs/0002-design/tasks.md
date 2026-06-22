# Tasks — 0002 Design

Ordered task list for the v0.1 runtime and calibration ledger.

## PR A — Package skeleton + loader

- [x] `pyproject.toml` with `[dependency-groups]` and
      `[tool.uv] package = true`
- [x] `src/brief_matrix/__init__.py`, `__main__.py`
- [x] `src/brief_matrix/loader.py` with tenant + schema validation
- [x] `schemas/tenant.schema.json`
- [x] `schemas/brief.schema.json`
- [x] `schemas/review-record.schema.json`
- [x] `tests/test_loader.py`

## PR B — Voice gate + calibration scorer

- [x] `src/brief_matrix/voice_gate.py`
- [x] `scripts/voice_lint.py` carrying the shared banlist
- [x] `src/brief_matrix/calibrate.py` with three-axis scorer
- [x] `schemas/calibration-run.schema.json`
- [x] `src/brief_matrix/ledger.py`
- [x] `tests/test_voice_gate.py`
- [x] `tests/test_calibrate.py`

## PR C — CLI + fixture tenant + first ledger row

- [x] `src/brief_matrix/cli.py` exposing `validate`, `calibrate`,
      `ledger`
- [x] `tenants/procurement-analyst/config.yaml`
- [x] `tenants/procurement-analyst/sources.yaml`
- [x] `tenants/procurement-analyst/voice_overrides.yaml`
- [x] `tenants/procurement-analyst/specs/section-structure.yaml`
- [x] `review-queue/procurement-analyst/2026-W34.md` fixture draft
- [x] `ledger/2026-W25-calibration-run.json` first checked-in row
- [x] `tests/test_cli.py`
- [x] `docs/methodology.md`
- [x] `decisions/DEC-BM-001-v0-persona-choice.md`
- [x] `decisions/DEC-BM-002-three-axis-calibration.md`

## PR D (next) — second tenant + semantic faithfulness

- [ ] Add `tenants/independent-municipal-budget-watch/`
- [ ] `scripts/citation_faithfulness.py` — fetch each cited URL
- [ ] `ledger summary` subcommand for cross-tenant aggregation
- [ ] Replace synthesizer stub with LLM-backed drafter
