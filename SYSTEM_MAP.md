# BriefMatrix — System Map

How the pieces connect. Read this alongside `PRODUCT_BRIEF.md` (the
"what") and `docs/METHODOLOGY.md` (the "how scores are computed").

## Top-level layout

```
brief-matrix/
  PRODUCT_BRIEF.md          # the product, who uses it, why
  SYSTEM_MAP.md             # this file
  STATUS.md                 # current/limits/next-queue snapshot
  README.md                 # operator-facing entry point
  AGENTS.md                 # agent operating contract
  LICENSE
  pyproject.toml            # uv + hatch packaging
  brief_matrix/             # runtime package (top-level, not src/)
    __init__.py
    __main__.py             # python -m brief_matrix → cli.main
    cli.py                  # argparse: validate / calibrate / ledger
    loader.py               # tenant config + schema validation
    voice_gate.py           # shared banlist + per-tenant union
    score.py                # three-axis scorer (canonical)
    calibrate.py            # back-compat alias for score.py
    ledger.py               # JSONL row read/write at data/ledger/
    report.py               # markdown rollup over ledger rows
    fetchers/
      __init__.py
      fixture.py            # sources.yaml → candidate items
  schemas/                  # draft 2020-12 JSON Schema docs
    tenant.schema.json
    brief.schema.json
    review-record.schema.json
    calibration-run.schema.json
  tenants/
    procurement-analyst/    # the example fixture tenant
      config.yaml
      sources.yaml
      voice_overrides.yaml
      specs/section-structure.yaml
  briefs/                   # approved briefs, per tenant
  review-queue/             # pending drafts, per tenant
    procurement-analyst/2026-W34.md
  data/
    ledger/                 # calibration ledger, append-only JSONL
      2026-W25-procurement-analyst-calibration-run.jsonl
  specs/
    0001-foundation/        # initial requirements (R-BM-001 … 010)
    0002-design/             # v0.1 design / acceptance ledger
  decisions/
    DEC-BM-001-v0-persona-choice.md
    DEC-BM-002-three-axis-calibration.md
  docs/
    METHODOLOGY.md          # axis definitions + worked example
    first-pr.md
  scripts/
    voice_lint.py           # shared banlist (BANNED_FAIL)
    validate_tenants.py
    validate_schemas.py
  tests/                    # pytest suite
```

## Data flow — one calibration run

```
tenants/<id>/config.yaml
       │
       ▼
brief_matrix.loader.load_tenant()
       │  validates against schemas/tenant.schema.json
       ▼
       Tenant(config, sources, section_structure, voice_overrides)
                │
                ▼
        brief_matrix.score.score(brief_path, tenant)
                │
                ├── voice_gate.check_tenant() → voice_score ∈ {0, 1}
                ├── H2-vs-declared-sections  → section_score ∈ [0, 1]
                └── inline-link-per-section  → citation_score ∈ [0, 1]
                │
                ▼
        brief_matrix.score.make_row()
                │  validates against schemas/calibration-run.schema.json
                ▼
        brief_matrix.ledger.append(row)
                │  one JSON object per line
                ▼
        data/ledger/<iso-week>-<tenant>-calibration-run.jsonl
```

## Module responsibilities

| Module | Owns |
|---|---|
| `brief_matrix.cli` | Argparse surface. Exit codes. Stdout/stderr framing. |
| `brief_matrix.loader` | Reading a tenant directory and validating it. Tenant isolation is the directory boundary. |
| `brief_matrix.voice_gate` | The shared `BANNED_FAIL` constant. Banlist merge (union-only). Word-boundary matching. |
| `brief_matrix.score` | The three axes. Pure functions over `(brief, tenant)`. No I/O beyond reading the brief. |
| `brief_matrix.calibrate` | Compat alias re-exporting `score.*`. Kept so existing imports keep working. |
| `brief_matrix.ledger` | JSONL append at `data/ledger/`. Schema-validates on read and write. |
| `brief_matrix.report` | Renders ledger rows as a Markdown table for human review. |
| `brief_matrix.fetchers.fixture` | Returns `sources.yaml` entries as the candidate set. v0.1 stub for live ingest. |

## CLI surface

```
python -m brief_matrix validate  --tenant tenants/<id>
python -m brief_matrix calibrate --tenant tenants/<id> --brief <path> [--iso-week W] [--dry-run] [--notes …]
python -m brief_matrix ledger    [--path data/ledger]
```

Every subcommand exits zero on success, non-zero on a structured
error. `--dry-run` on `calibrate` prints the row without writing to
the ledger — this is what the acceptance test uses to keep the
checked-in row stable.

## Tenant isolation

`loader.load_tenant()` never reads outside `tenants/<id>/`. The
directory boundary IS the isolation guarantee in v0.1. Multi-tenant
under load (concurrent loader processes, per-tenant secret scoping)
is named in spec 0001 but not exercised.

## What revisits this map

- Adding a new module to `brief_matrix/`. New file → new row in the
  Module responsibilities table.
- Adding a new schema. The data-flow diagram references the schema
  by name.
- Moving the ledger out of `data/ledger/` or changing the row
  format. Both the diagram and the CLI surface section change.
- Adding a new CLI verb. The CLI surface block must reflect every
  shipped verb.
