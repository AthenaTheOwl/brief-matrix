# Requirements — 0002 Design

Numbered requirements for the v0.1 runtime + calibration ledger. The
0001 spec named what the foundation must contain; 0002 names what the
runtime must do with it. R-BM-* numbering continues from 0001.

## Runtime CLI

- **R-BM-011** The package ships as `brief_matrix` under `src/`. It is
  installable in editable mode via `uv sync`. `python -m brief_matrix`
  is the canonical entry point.
- **R-BM-012** The CLI exposes three subcommands in v0.1:
  `validate`, `calibrate`, and `ledger`. Each takes a `--tenant`
  argument naming a directory under `tenants/`.
- **R-BM-013** `validate` loads the named tenant, parses its config
  against the tenant schema, parses its sources against the source
  schema, and exits zero if and only if every gate passes.
- **R-BM-014** `calibrate` runs the calibration scorer against a
  named brief or draft file and writes a single calibration row to
  `ledger/`. It does not mutate the brief.
- **R-BM-015** `ledger` reads all rows under `ledger/` and prints
  a one-line-per-row summary to stdout. It is read-only.

## Calibration scoring

- **R-BM-016** The calibration scorer emits a row with three axes:
  `voice_score`, `citation_score`, and `section_score`. Each is a
  float in [0.0, 1.0]. Definitions live in `docs/methodology.md`.
- **R-BM-017** `voice_score` is `1.0` if the brief passes voice-lint
  with the merged shared+tenant banlist, `0.0` otherwise. There are
  no partial credits for voice; the discipline is a hard gate.
- **R-BM-018** `citation_score` is the fraction of declared sections
  that contain at least one inline citation. A brief with zero
  citations scores 0.0 regardless of section count.
- **R-BM-019** `section_score` is the fraction of the tenant's
  declared section structure that the brief actually fills. Extra
  sections do not raise the score; missing sections lower it.
- **R-BM-020** A calibration row carries `schema_version`,
  `tenant_id`, `iso_week`, `brief_path`, `created_at`,
  `voice_score`, `citation_score`, `section_score`, and `notes`.
  The row schema lives at `schemas/calibration-run.schema.json`.

## Ledger discipline

- **R-BM-021** Calibration rows are checked into git as one JSON
  file per run under `ledger/`. They are append-only; no row is
  edited after the fact. A correction is a new row with an explicit
  `supersedes` note.
- **R-BM-022** At least one calibration row ships in the repo at
  v0.1 so that downstream consumers have an example shape and so
  that the loader has something to read on `ledger` calls.

## Methodology surface

- **R-BM-023** Each scoring axis is defined in
  `docs/methodology.md`, with a worked example pulled from the
  checked-in fixture brief. Changing the definition requires a new
  DEC-BM entry.
- **R-BM-024** The first decision in the calibration era,
  `DEC-BM-002`, names the three-axis split and explains why
  semantic citation-faithfulness is deferred.
