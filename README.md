# BriefMatrix

Multi-tenant, persona-conditioned weekly brief platform. Any niche topic, any audience, with the same spec-driven structure, voice discipline, citation-faithfulness, and review-queue promotion shipped in ai-field-brief.

## What this is

ai-field-brief is the live single-tenant reference. BriefMatrix is the
shape that pattern takes when more than one persona uses it. The four
shipped control planes (spec ledger, voice-lint banlist, citation-
faithfulness check, review-queue promotion) become per-tenant
configuration; the brief-generation runtime is shared.

A "brief" here is a typed artifact, not a Substack post:

- spec ledger names the structure of the brief
- a fetcher per source pulls candidate items
- a synthesizer drafts the brief with explicit citations
- voice-lint refuses the draft if it carries banned phrasing
- the review queue holds the draft until a human approves

BriefMatrix is the platform layer that runs this loop for N tenants in
one repo, with one shared infrastructure and N tenant-isolated
configurations.

## Who uses it

Newsletter publishers who want spec-driven brief discipline instead of
ad-hoc summarization. In-house analyst teams at financial firms that
need a citable weekly artifact. Niche-community moderators who want a
brief that does not drift into hype. Industry trade associations.
University research-group communications leads.

## Why now

The newsletter market is saturating on undifferentiated AI summarization.
The spec-driven, voice-gated brief is a recognizable shape. The
ai-field-brief stack ships the discipline; BriefMatrix turns it into a
multi-tenant primitive so the discipline does not get reinvented per
publisher.

## Status

v0 scaffold; no implementation yet. The specs ledger names the first
set of requirements (R-BM-001 through R-BM-010). The first PR after
this scaffold lands the tenant schema and the per-tenant directory
layout.

## How to run

Placeholder; will land in spec 0002. v0 ships the tenant schema, the
per-tenant directory layout, and one example tenant (a procurement /
supply-chain analyst) as a checked-in fixture. No runtime is required
to read the artifact.

The eventual CLI shape (target for spec 0003):

```
python -m brief_matrix generate --tenant tenants/procurement-analyst --week 2026-W34
python -m brief_matrix review --tenant tenants/procurement-analyst --week 2026-W34
```

## Layout

```
brief-matrix/
  README.md
  LICENSE
  AGENTS.md
  .gitignore
  specs/
    0001-foundation/
      requirements.md
      design.md
      tasks.md
      acceptance.md
  docs/
    first-pr.md
```

Future directories (named in specs, not created yet):

- `src/brief_matrix/` — multi-tenant runtime
- `src/brief_matrix/fetchers/` — one module per source class
- `tenants/<tenant-id>/` — per-tenant config, spec ledger, voice
  overrides
- `briefs/<tenant-id>/<year>-W<nn>.md` — published briefs
- `review-queue/<tenant-id>/` — pending drafts awaiting approval
- `schemas/` — tenant, brief, review-record schemas

## License

MIT. See [LICENSE](LICENSE).
