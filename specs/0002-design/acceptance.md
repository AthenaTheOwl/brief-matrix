# Acceptance — 0002 Design

"v0.1 done" means the following hold simultaneously.

## Artifacts present

- `pyproject.toml` declares `[dependency-groups]` and `[tool.uv]
  package = true`.
- `brief_matrix/{cli,loader,voice_gate,score,calibrate,ledger,report}.py`
  all import cleanly with no side effects at import.
- `schemas/calibration-run.schema.json` validates as draft 2020-12.
- `tenants/procurement-analyst/` carries `config.yaml`,
  `sources.yaml`, `voice_overrides.yaml`, and
  `specs/section-structure.yaml`.
- `review-queue/procurement-analyst/2026-W34.md` exists with the
  documented front-matter.
- `data/ledger/2026-W25-procurement-analyst-calibration-run.jsonl`
  is the first checked-in row and validates against the
  calibration-run schema.
- `docs/METHODOLOGY.md` defines the three axes with a worked
  example from the fixture draft and a `## What revisits this`
  section listing the edits that require a paired decision entry.
- `decisions/DEC-BM-001-v0-persona-choice.md` and
  `decisions/DEC-BM-002-three-axis-calibration.md` exist.

## CLI gates pass

Run from the repo root:

```
python -m pytest
python -m brief_matrix validate --tenant tenants/procurement-analyst
python -m brief_matrix calibrate --tenant tenants/procurement-analyst \
    --brief review-queue/procurement-analyst/2026-W34.md --dry-run
python -m brief_matrix ledger
```

All four exit zero. The `--dry-run` flag prevents the calibrate
acceptance test from re-writing the checked-in ledger row.

## Manual review

- A reader can trace one fixture candidate item from
  `tenants/procurement-analyst/sources.yaml` to the inline
  citation in `review-queue/procurement-analyst/2026-W34.md` and
  then to the `citation_score` in the checked-in ledger row.
- The three calibration axes are defined unambiguously in
  `docs/methodology.md`; an outside reader can compute the row by
  hand from the fixture brief and arrive at the same numbers.
- `STATUS.md` carries the three required H2 sections (Current
  state / Known limits / Next feature queue) and reflects what
  is actually shipped, not what is planned.

## Out of v0.1 acceptance

- Real LLM-backed synthesis. Stub only in v0.1.
- Live source ingest. Fixture only.
- Semantic citation-faithfulness. Structural coverage only.
- Multi-tenant scale. One tenant ships.
