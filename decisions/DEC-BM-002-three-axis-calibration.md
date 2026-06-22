# DEC-BM-002 — Three-axis calibration, semantic faithfulness deferred

- **Status:** accepted
- **Decided:** 2026-06-22
- **Applies to:** specs/0002-design, docs/methodology.md

## Context

The runtime needs a scoring discipline so each weekly run produces
a row in the ledger that downstream readers can diff. The
candidates considered were:

1. A single composite score in [0, 1].
2. A vector of independent axis scores.
3. An LLM judge that returns a free-form quality rating.

## Decision

The runtime ships option (2) with **three axes**: voice,
citation, and section. Definitions live in `docs/methodology.md`.
A semantic citation-faithfulness check (does the cited URL
actually support the inline claim?) is **deferred** to spec 0003.

## Why three axes, not one composite

A composite hides which axis regressed week to week. The whole
point of the ledger is to support a diff; collapsing the diff
into one number defeats the construct.

The three axes were chosen to be independent on purpose:

- Voice is process discipline; it should not be affected by a
  weak news week.
- Citation is sourcing discipline; it should not be affected by
  a strong-voice but un-sourced draft.
- Section is shape discipline; it captures whether the
  synthesizer respected the tenant's declared structure.

## Why voice is binary

Voice is a brand-trust gate. A "mostly-passed" voice draft has
the same downstream shape as no gate at all: the reader still
encounters the banned phrase. Partial credit would dilute the
signal and create an incentive to ship close-to-banned drafts.

## Why semantic faithfulness is deferred

The structural check (does each section carry an inline link?)
catches the most common failure mode in v0.1: the synthesizer
omitted citations. The semantic check (does the URL's content
actually support the claim?) requires fetching the URL, parsing
it, and an LLM-side check. That stack is a meaningful new
dependency, and we want the structural baseline to be stable
before introducing it.

DEC-BM-NNN (TBD) will name the semantic check, the model that
runs it, and the policy when fetched content disagrees with the
inline claim.

## What this rules in for spec 0003

- A new score axis, `faithfulness_score`, with the same [0,1]
  shape.
- A schema bump on `calibration-run.schema.json` from
  `schema_version: 1` to `schema_version: 2`.
- A `scripts/citation_faithfulness.py` runner.

## Reversibility

Medium cost. The three-axis decision is baked into the schema;
moving to a single composite would require a schema migration
and a re-run of historic rows. The deferral of semantic
faithfulness is fully reversible — adding a fourth axis is
strictly additive.
