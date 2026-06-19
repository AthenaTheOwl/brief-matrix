# First PR

The literal first PR after this scaffold. The goal is the tenant
schema, the example tenant directory, and the decision record naming
the v0 persona — no runtime yet.

## Files this PR adds

- `schemas/tenant.schema.json`
  - JSON Schema draft 2020-12
  - Required: `id`, `name`, `persona`, `source_registry`,
    `spec_ledger_ref`, `review_target`
  - Optional: `voice_overrides`
- `schemas/brief.schema.json`
  - Required: `tenant_id`, `iso_week`, `sections[]`, `citations[]`,
    `voice_lint_pass`, `review_status`
  - `review_status` enum: `pending-review`, `approved`, `rejected`
- `schemas/review-record.schema.json`
  - Required: `tenant_id`, `iso_week`, `from_status`, `to_status`,
    `reviewer`, `decided_at`
- `tenants/procurement-analyst/config.yaml`
  - `id: procurement-analyst`
  - `name: Procurement / Supply-Chain Weekly`
  - `persona`: short description of the reader
  - `source_registry: sources.yaml`
  - `spec_ledger_ref: specs/`
  - `review_target: file://briefs/procurement-analyst/`
- `tenants/procurement-analyst/sources.yaml`
  - Fixture sources only; no live URLs. Three example entries
    representing trade press, an academic feed, and a primary-source
    docket.
- `tenants/procurement-analyst/specs/section-structure.yaml`
  - Section list: `intro`, `items`, `what-this-means`, `footer`
- `decisions/DEC-BM-001-v0-persona-choice.md`
  - Names the procurement / supply-chain analyst as the v0 persona
  - Justifies it as the persona closest to the user's day-job
    fluency, so the calibration loop tightens fastest

## Verification

```
python -m pytest        # no tests yet; the runner exits clean
python scripts/validate_schemas.py
```

Both exit zero. The schemas parse with `jsonschema`. The tenant
config validates against the tenant schema.

## What this PR does not do

- No voice-lint script. That is PR 2.
- No synthesizer. That is PR 3.
- No fetcher implementations. PR 3 adds the fixture fetcher.
- No review-queue Markdown fixture. That is PR 2.
- No CLI entry point.
