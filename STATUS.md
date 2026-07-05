# BriefMatrix Status

Snapshot of where the multi-tenant brief platform sits at v0.1. This
file is the contract between the runtime and whoever picks it up next.

## Current state

- v0.1 ships a runnable Python CLI: `python -m brief_matrix validate`,
  `python -m brief_matrix calibrate`, and `python -m brief_matrix ledger`.
- The runtime package lives at top-level `brief_matrix/` with modules
  `cli.py`, `loader.py`, `voice_gate.py`, `score.py`, `calibrate.py`
  (compat alias for `score`), `ledger.py`, `promote.py`, and
  `report.py`.
- Tenant schema, brief schema, review-record schema, and
  calibration-run schema all land under `schemas/` as draft 2020-12
  JSON Schema documents.
- Two example tenants ship: `procurement-analyst` and
  `municipal-budget-watch`. Their section structures and voice
  overrides diverge, and tests assert tenant overrides do not bleed
  across tenants.
- The voice gate (`brief_matrix/voice_gate.py`) wraps a shared
  banlist (`BANNED_FAIL`) plus per-tenant additive overrides.
  Removing a shared term from an override file is rejected.
- The calibration scorer (`brief_matrix/score.py`) scores any
  brief or draft on three axes — voice discipline, citation
  coverage, and section conformance — and the CLI writes a row to
  `data/ledger/`.
- The first calibration row,
  `data/ledger/2026-W25-procurement-analyst-calibration-run.jsonl`,
  is checked in. It scores the fixture draft at
  `review-queue/procurement-analyst/2026-W34.md` and provides a
  baseline future runs can diff against.
- `brief_matrix/report.py` renders ledger rows as a Markdown table
  for human review.
- Tests under `tests/` cover the loader, the voice gate, the
  calibration scorer, and the CLI entry points. `python -m pytest`
  exits zero on the fixture set.
- The methodology behind the three score axes is documented at
  `docs/METHODOLOGY.md`. The first architectural decisions are
  recorded under `decisions/`.
- Top-level `PRODUCT_BRIEF.md` and `SYSTEM_MAP.md` describe the
  product and module map.

## Known limits

- The fetcher layer is fixture-only. There is no live source ingest;
  candidate items are read from `tenants/<id>/sources.yaml` as the
  literal candidate set. Live ingest is out of v0.1 scope.
- The synthesizer is a stub. It assembles a placeholder draft from
  fixture candidates so the rest of the loop has something to
  score, but it does not call an LLM. Real synthesis lands in
  spec 0003.
- The review queue is a directory of Markdown files. Promotion is a
  CLI action that moves one approved draft into `briefs/`, writes a
  calibration row, and records the review transition. There is no
  approval UI.
- Two tenants ship. Multi-tenant load and per-tenant secret scoping
  are still out of v0.1 scope, but loader isolation and additive voice
  overrides are covered by tests.
- Citation-faithfulness is checked structurally — every cited claim
  has a `source_url` and an `inline_claim` — but the URL is not
  fetched. The semantic check (does the source actually support
  the claim?) is named in DEC-BM-002 and deferred.
- The calibration ledger is a directory of JSONL files at
  `data/ledger/`. There is no cross-run aggregation view beyond
  `report.markdown_table`; the ledger is meant to be diffed in git.

## Next feature queue

- Add a third tenant with a different cadence and a non-weekly
  section structure to test paths beyond Friday weekly briefs.
- Implement `scripts/citation_faithfulness.py` to fetch each cited
  URL and check the inline claim against the page text. Pair it
  with a new calibration axis and bump the calibration-run schema
  to v2.
- Replace the synthesizer stub with a real LLM-backed drafter that
  fills the tenant's declared section structure from candidate
  items and emits inline citations.
- Add a rejection workflow that records a review row without moving
  the draft, so rejected briefs have the same audit shape as
  promoted briefs.
- Wire `brief_matrix.report` into a `ledger summary` subcommand so
  the cross-tenant Markdown table is reachable from the CLI.

- Resolve factory defect: missing PRODUCT_BRIEF.md,SYSTEM_MAP.md
- Resolve factory defect: missing data/ledger/*.jsonl
- Resolve factory defect: METHODOLOGY.md missing revisit section
- Resolve factory defect: PRODUCT_BRIEF.md is required for active repos
- Resolve factory defect: SYSTEM_MAP.md is required for active repos
- Resolve factory defect: expected file 'PRODUCT_BRIEF.md' is missing
- Resolve factory defect: expected file 'SYSTEM_MAP.md' is missing
- Resolve factory defect: expected file 'brief_matrix/cli.py' is missing
- Resolve factory defect: expected file 'brief_matrix/score.py' is missing
- Resolve factory defect: expected file 'brief_matrix/ledger.py' is missing
- Resolve factory defect: expected glob 'data/ledger/*.jsonl' matched no files
- Resolve factory defect: module 'cli' declares source 'brief_matrix/cli.py', but it is missing
- Resolve factory defect: module 'score' declares source 'brief_matrix/score.py', but it is missing
- Resolve factory defect: module 'ledger' declares source 'brief_matrix/ledger.py', but it is missing
- Resolve factory defect: module 'report' declares source 'brief_matrix/report.py', but it is missing
- Resolve factory defect: claude_code review requested patch; inspect defect log
