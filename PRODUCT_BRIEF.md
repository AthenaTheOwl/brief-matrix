# BriefMatrix — Product Brief

A multi-tenant control plane that scores, calibrates, and audits the
weekly briefs produced by other repos. BriefMatrix is not a brief
generator; it is the discipline layer that keeps brief-generation
honest week over week.

## The product

BriefMatrix runs on a monthly-or-quarterly cadence against any repo
that ships persona-conditioned briefs (the live reference is
`ai-field-brief`). Each run:

1. Loads a tenant's spec ledger, source registry, and voice overrides.
2. Scores a candidate draft on three independent axes — voice
   discipline, citation coverage, section conformance.
3. Appends one row to the calibration ledger so the next run has
   something to diff against.

The ledger is the artifact. A single row is a snapshot; a sequence of
rows tells the discipline story.

## Who this is for

- **Newsletter publishers** running spec-driven brief workflows who
  want a third-party scorecard instead of "the draft looked fine."
- **In-house analyst teams** at financial / research firms that need
  a citable, auditable weekly artifact and a paper trail for review.
- **Trade associations and research groups** that publish briefs
  under a brand-voice constraint and need to prove the constraint
  held.

The user is the operator running calibration runs — typically the
editor or platform lead, not the brief author. The author writes the
draft; BriefMatrix asks "does this draft pass the contract?"

## The contract this enforces

Three axes, each independently diffable across runs:

| Axis | Question | Range |
|---|---|---|
| Voice score | Did the draft stay inside the merged banlist? | binary {0, 1} |
| Citation score | Does each declared section carry an inline link? | [0, 1] |
| Section score | Did the draft fill the declared section structure? | [0, 1] |

Voice is binary on purpose — partial credit defeats the discipline
contract. The other two are fractional because briefs can land in
intermediate shapes worth tracking.

## Why this is a control plane, not a generator

The brief-generation runtime lives in the tenant repos. BriefMatrix
does not draft. It only scores. The separation matters:

- **Tenants own the synthesis.** They can swap LLMs, change
  prompts, restructure their fetcher graph. BriefMatrix does not
  care; it scores the output.
- **BriefMatrix owns the discipline.** The voice banlist, the
  schema for a row, the calibration methodology — these are
  versioned here and inherited by every tenant.
- **The ledger is the contract surface.** A regression in any axis
  shows up as a row that does not match its predecessor. That row
  is the only artifact a stakeholder needs to read.

## v0.1 scope

- One example tenant (`procurement-analyst`) ships as a fixture so
  the runtime is exercised end-to-end.
- One calibration row is checked in at
  `data/ledger/2026-W25-procurement-analyst-calibration-run.jsonl`
  as the seed of the ledger.
- The CLI ships three verbs: `validate`, `calibrate`, `ledger`.
- Tests cover the loader, voice gate, scorer, ledger I/O, and CLI.
- Methodology is documented at `docs/METHODOLOGY.md` with a worked
  example a reader can reproduce by hand.

## Out of v0.1

- Live source ingest. The fixture fetcher returns `sources.yaml` as
  the candidate set.
- LLM-backed synthesis. The synthesizer is a stub.
- Semantic citation-faithfulness. Structural coverage only; URL
  fetching lands in a later spec.
- Multi-tenant scale. One tenant ships in v0.1; the loader respects
  tenant directory boundaries but multi-tenant isolation under load
  is named in 0001 and not exercised.

## What success looks like

A new tenant onboards by writing a `config.yaml`, a `sources.yaml`,
a section structure, and (optionally) voice overrides. The first
`calibrate` run produces a row. Every subsequent week's row is a
diff against the prior — and the diff is the only thing an editor
has to read to know whether discipline held.
