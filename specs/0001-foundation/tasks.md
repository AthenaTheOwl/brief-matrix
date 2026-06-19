# Tasks — 0001 Foundation

Checkbox tasks ordered for the first two to three PRs after the
scaffold.

## PR 1 — Tenant schema and example tenant

- [ ] Write `schemas/tenant.schema.json` per R-BM-001
- [ ] Write `schemas/brief.schema.json` per R-BM-004
- [ ] Write `schemas/review-record.schema.json`
- [ ] Create `tenants/procurement-analyst/config.yaml`
- [ ] Create `tenants/procurement-analyst/sources.yaml` (fixture
      sources; no live URLs)
- [ ] Create `tenants/procurement-analyst/specs/section-structure.yaml`
- [ ] Add `scripts/validate_tenants.py` skeleton
- [ ] Add `scripts/validate_schemas.py` skeleton
- [ ] Add `decisions/DEC-BM-001-v0-persona-choice.md`

## PR 2 — Voice gate plus review-queue layout

- [ ] Add `scripts/voice_lint.py` with the shared BANNED_FAIL banlist
- [ ] Create `tenants/procurement-analyst/voice_overrides.yaml`
      (empty, demonstrates schema)
- [ ] Create `review-queue/.gitkeep` and `briefs/.gitkeep`
- [ ] Write a fixture draft at
      `review-queue/procurement-analyst/2026-W34.md` showing the
      front-matter shape
- [ ] Implement `src/brief_matrix/loader.py` (tenant config loader)
- [ ] Implement `src/brief_matrix/voice_gate.py` wrapper around
      voice_lint
- [ ] Wire CLI entry: `python -m brief_matrix validate`

## PR 3 — Synthesizer skeleton and DEC ledger

- [ ] Implement `src/brief_matrix/synthesizer.py` stub that emits a
      placeholder draft from fixture candidate items
- [ ] Implement `src/brief_matrix/fetchers/fixture.py` returning
      checked-in candidate items
- [ ] Add `scripts/validate_decisions.py` skeleton
- [ ] Document the section structure choice in DEC-BM-002
- [ ] Update README install + run section once the CLI exists
