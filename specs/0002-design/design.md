# Design — 0002 Design

How the v0.1 runtime is laid out, and why the calibration ledger is
the spine of the control plane.

## Layering

```
brief_matrix/
  __init__.py
  __main__.py        # delegates to cli.main
  cli.py             # argparse, three subcommands
  loader.py          # tenant config + schema validation
  voice_gate.py      # banlist merge + match
  score.py           # three-axis scorer (canonical)
  calibrate.py       # back-compat alias for score.py
  ledger.py          # JSONL row read/write at data/ledger/
  report.py          # markdown rollup over ledger rows
  fetchers/
    __init__.py
    fixture.py       # returns sources.yaml as the candidate set
```

Every module is import-safe: no side effects at import, no network at
import. The CLI is the only place a process exits with a non-zero
status.

## Tenant config flow

1. `loader.load_tenant(path)` resolves `tenants/<id>/config.yaml`.
2. The loader validates the config against
   `schemas/tenant.schema.json`.
3. The loader returns a typed dict carrying the merged tenant view:
   config, sources, section structure, voice overrides.
4. `validate` is the CLI surface for this. It is a no-op if the
   tenant is well-formed and an exit-1 with a structured error
   message if not.

The loader never reads files outside `tenants/<id>/`. The directory
boundary IS the tenant isolation guarantee in v0.1.

## Voice gate

`voice_gate.check(text, tenant)` merges the shared `BANNED_FAIL`
banlist with the tenant's `voice_overrides.yaml` `extra_banned`
entries. The merge is union-only; the override loader rejects an
attempt to remove a shared term (R-BM-008).

The gate returns `(passed: bool, hits: list[str])`. The CLI prints
hits when the gate fails. Voice failure is binary on purpose:
discipline is the moat, and a "mostly-passed" voice gate is the
same shape as no gate at all.

## Calibration scorer

`score.score(brief_path, tenant)` returns a `CalibrationRow`
dict shaped by `schemas/calibration-run.schema.json`. The three
axes are computed independently so each can be diffed across runs:

- **voice_score**: 1.0 if `voice_gate.check` passes, else 0.0.
- **citation_score**: count of sections containing at least one
  `[…](http…)` link, divided by section count. Zero citations
  collapses to 0.0 regardless.
- **section_score**: count of declared sections that the brief
  actually fills (matched by H2 headings), divided by declared
  section count. Extra H2s are noted in `notes` but do not raise
  the score.

The scorer reads the brief, the tenant's section structure, and the
merged voice config. It writes nothing on its own. The CLI's
`calibrate` subcommand calls the scorer and hands the row to
`ledger.append`.

## Ledger module

`ledger.append(row)` appends one JSON object per line to
`data/ledger/<iso-week>-<tenant>-calibration-run.jsonl`. Each line
is a complete row; the file is append-safe in the sense that a
partial line at the tail is rejected by `ledger.read_all` (the
schema validator refuses any row that does not parse cleanly).

`ledger.read_all()` walks `data/ledger/`, parses each JSONL line
against the schema, and yields the rows sorted by `created_at`.
The `ledger` subcommand prints one row per line.

## Why three axes

Voice is binary because the brand promise is a discipline
guarantee. Citations and sections are continuous because the brief
shape is partially-fillable — a draft with three of five sections
filled is a real intermediate state worth tracking in the ledger.

A single composite score would hide which axis regressed between
runs, which is the question the ledger exists to answer.

## What 0002 does not do

- No live source ingest. The fixture fetcher returns the contents
  of `sources.yaml` as the candidate set.
- No LLM-backed synthesis. The synthesizer is a stub; the
  fixture draft is hand-written and lives in the review queue.
- No semantic citation-faithfulness. Structural coverage only.
  See DEC-BM-002 for the rationale.
- No cross-run aggregation in the `ledger` subcommand. Per-row
  print is the v0.1 surface; aggregation lands in 0003.
