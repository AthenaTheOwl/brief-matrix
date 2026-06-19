# Design — 0001 Foundation

## Shape

brief-matrix is a Python package that runs the ai-field-brief pattern
for N tenants in one repo. Each tenant has an isolated configuration
directory; the runtime is shared.

The architecture has four layers:

1. **Tenant config.** `tenants/<id>/config.yaml` plus
   `tenants/<id>/sources.yaml` plus `tenants/<id>/specs/`.
2. **Runtime.** `src/brief_matrix/` orchestrates one weekly run per
   tenant: fetch, synthesize, voice-gate, queue.
3. **Review queue.** `review-queue/<tenant-id>/` holds pending
   drafts as Markdown files. A human approves or rejects out of
   band; an approval transitions the file into `briefs/`.
4. **Publication.** `briefs/<tenant-id>/<iso-week>.md` is the
   approved artifact. The per-tenant `review_target` field names
   where the publisher renders it next.

## Data flow

```
tenants/<id>/config.yaml + sources.yaml
   |
   v
[fetcher.run]  -> candidate_items.yaml
   |
   v
[synthesizer.draft]  -> draft.md
   |
   v
[voice_gate.check]  -> pass | fail
   |  pass
   v
review-queue/<id>/<week>.md  (status: pending-review)
   |  human approves
   v
briefs/<id>/<week>.md  (status: approved)
   |
   v
[publisher.render]  ->  per-tenant target
```

## Tenant isolation

A tenant cannot read another tenant's spec ledger, source registry,
or review queue. The runtime takes a tenant id as a required input
and refuses to operate across tenant boundaries. v0 enforces this
through directory-scoped file access in the loader; later specs
may add stronger isolation if multi-machine deployment matters.

## Voice override semantics

The shared banlist is in `scripts/voice_lint.py::BANNED_FAIL`. A
tenant may add terms in `tenants/<id>/voice_overrides.yaml`. A
tenant may not remove a shared-banlist term; the validator rejects
the override config if it tries.

A tenant may also add allowed-after-marker entries (the
`<!-- voice_lint:allow ... -->` pattern from ai-field-brief), but
only for terms the shared lint has flagged at WARN, not at FAIL.

## Review queue mechanics

The review queue is a directory of Markdown files. Each file is the
draft plus a YAML front-matter block with `status`, `created_at`,
`tenant_id`, `iso_week`, `voice_lint_pass`. Approval is a manual
edit: change `status: pending-review` to `status: approved` and
move the file from `review-queue/` into `briefs/`. The validator
re-checks voice-lint on the moved file.

v0 does not ship a review UI. The Markdown file plus the directory
move is the workflow.

## Out of v0 scope

- A web UI for the review queue
- Multi-machine deployment
- Per-tenant LLM key isolation
- Cross-tenant calibration metrics
