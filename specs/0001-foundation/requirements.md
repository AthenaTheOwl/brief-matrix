# Requirements — 0001 Foundation

Numbered requirements for the v0 scaffold of brief-matrix. The R-BM-*
prefix is the brand tag and appears in every downstream spec, decision,
and gate.

## Tenant model

- **R-BM-001** The repo ships a tenant schema under
  `schemas/tenant.schema.json`. Fields: `id`, `name`, `persona`,
  `source_registry`, `spec_ledger_ref`, `voice_overrides`,
  `review_target`.
- **R-BM-002** Each tenant lives at `tenants/<tenant-id>/` with at
  least `config.yaml`, `sources.yaml`, and `specs/`. The directory
  layout is enforced by `scripts/validate_tenants.py`.
- **R-BM-003** v0 ships exactly one example tenant: a procurement /
  supply-chain analyst persona, fixture-only, no live sources.

## Brief model

- **R-BM-004** The repo ships a brief schema under
  `schemas/brief.schema.json`. Fields: `tenant_id`, `iso_week`,
  `sections[]`, `citations[]`, `voice_lint_pass`, `review_status`.
- **R-BM-005** A brief has a fixed section structure declared in
  the tenant's spec ledger. The synthesizer fills sections; it does
  not invent new ones.
- **R-BM-006** Every citation entry pairs a `source_url` with an
  `inline_claim`. Briefs with zero citations are invalid.

## Discipline

- **R-BM-007** Voice-lint is a hard gate. A draft that fails voice-
  lint never lands in the review queue; it is returned to the
  synthesizer with the failed terms named.
- **R-BM-008** Per-tenant voice overrides may extend the shared
  banlist; they may not shrink it. The override schema is enforced
  by `scripts/validate_tenants.py`.

## Review queue

- **R-BM-009** A drafted brief lands in
  `review-queue/<tenant-id>/<iso-week>.md` with status
  `pending-review`. Approval transitions it to
  `briefs/<tenant-id>/<iso-week>.md`. The transition is recorded in
  the review-record schema.

## Governance

- **R-BM-010** Architectural choices are recorded in
  `decisions/DEC-BM-NNN-<slug>.md`. The first decision (DEC-BM-001)
  picks the v0 persona and justifies the single-tenant fixture
  approach.
