# Acceptance — 0001 Foundation

"v0 done" means the following hold simultaneously.

## Artifacts present

- `schemas/tenant.schema.json` validates
- `schemas/brief.schema.json` validates
- `schemas/review-record.schema.json` validates
- `tenants/procurement-analyst/config.yaml` parses against the tenant
  schema
- `tenants/procurement-analyst/sources.yaml` is well-typed
- `tenants/procurement-analyst/specs/section-structure.yaml` is well-
  typed
- `tenants/procurement-analyst/voice_overrides.yaml` exists (may be
  empty) and validates against the override schema
- `review-queue/procurement-analyst/2026-W34.md` exists as a fixture
  draft with valid front-matter
- `decisions/DEC-BM-001-v0-persona-choice.md` exists

## Gates pass

Run from the repo root:

```
python -m pytest
python scripts/voice_lint.py
python scripts/validate_schemas.py
python scripts/validate_tenants.py
python scripts/validate_decisions.py
```

All five exit zero.

## Manual review

- The example tenant's section structure is recognizable as a brief
  shape (intro, items, what-this-means, footer).
- The voice-lint banlist is seeded from the shared portfolio voice
  spec; the override schema rejects an attempt to remove a shared
  term.
- A reader can trace one fixture candidate item through the directory
  layout from `sources.yaml` to the draft in `review-queue/`.

## Out of v0 acceptance

- The synthesizer is a stub. Real candidate-to-draft synthesis is
  spec 0003.
- The fetcher is a fixture. Live source ingest is spec 0003.
- A second tenant is not required. Multi-tenant scale is spec 0002.
