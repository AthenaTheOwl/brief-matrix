# AGENTS.md — brief-matrix

Operating contract for AI agents working in this repo. Conventions
match the AthenaTheOwl portfolio so an agent already trained on
ai-field-brief recognizes the shape.

## What this repo is

A multi-tenant runtime that produces persona-conditioned weekly briefs
under the same spec-driven discipline as ai-field-brief. Each tenant
has its own spec ledger, source registry, voice overrides, and review
queue. The runtime is shared; the configuration is per-tenant.

The brief is a typed artifact, not a free-form post. Voice-lint and
citation-faithfulness are merge gates, not dashboards.

## Roles you may see in tasks

| Role | What they do |
|---|---|
| `tenant-loader` | Reads a tenant config, validates against the tenant schema |
| `source-fetcher` | Pulls candidate items from one source per call |
| `brief-synthesizer` | Drafts the weekly brief from candidate items |
| `voice-gate` | Runs voice-lint against the draft; refuses on failure |
| `review-curator` | Lands the draft in the per-tenant review queue |
| `publisher` | Renders an approved brief to the per-tenant target |

These roles exist in the spec ledger; not all are implemented in v0.

## Voice constraints

- No marketing words. The shared banlist is in
  `scripts/voice_lint.py::BANNED_FAIL`. Per-tenant overrides may add
  to the banlist; they may not remove from it.
- No antithetical reversals as a structural device.
- Every claim in a brief cites a source URL inline.
- A draft that fails voice-lint never lands in the review queue.

## Gates (will land in spec 0002)

Planned local gates before pushing:

- `pytest`
- `voice_lint.py` on `briefs/**/*.md` and `review-queue/**/*.md`
- `spec_check.py` against `specs/` and `tenants/*/specs/`
- `validate_tenants.py` — every tenant config is well-typed
- `citation_faithfulness.py` — every cited claim resolves

## Out of scope

- A hosted dashboard. v0 is CLI plus checked-in artifacts.
- LLM-judge scoring of brief quality. Discipline is the moat, not a
  judge model.
- Cross-tenant content reuse. Each tenant's spec ledger and source
  registry are isolated.
- Real-time delivery. Weekly cadence on cron, not push.
