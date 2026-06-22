# DEC-BM-001 — v0 persona choice

- **Status:** accepted
- **Decided:** 2026-06-22
- **Applies to:** specs/0001-foundation, specs/0002-design

## Context

The v0 BriefMatrix scaffold needs exactly one example tenant. The
tenant choice does double duty: it is the literal fixture against
which schemas and the runtime are exercised, AND it sets the tone
for what kind of brief the platform produces.

## Decision

The v0 persona is a **procurement / supply-chain analyst** working
inside a mid-cap manufacturer. The fixture sources are USTR Federal
Register notices, a fictional PortWatch trade-press feed, and a
Production & Operations Management academic feed.

## Why this persona

Three reasons, in order of weight:

1. The persona's day-job fluency is closest to the maintainer's
   background, so the calibration loop tightens fastest. A bad
   citation or a hand-wavy "what-this-means" paragraph is
   immediately recognizable.
2. The brief shape — tariff dockets, port operations, supplier
   structure — is recognizably a control-plane artifact. It is
   not lifestyle content and not generic AI news; it forces the
   format to carry analytical weight.
3. Procurement is one of the categories where the existing
   newsletter market is weakest. There is room for a discipline-
   gated brief.

## What this rules out for v0

- A second tenant. Multi-tenant divergence is named in 0001 but
  is not exercised until DEC-BM-NNN selects the second persona.
- Live source ingest. The persona's sources include a primary-
  source docket whose URL structure changes; we do not want the
  fixture to break on a source-side change in v0.
- LLM-backed synthesis. The fixture brief is hand-written so the
  scoring methodology can be developed against a known-good
  reference.

## Reversibility

Low cost. Swapping the v0 persona would require rewriting the
fixture tenant directory, the fixture brief, and the first ledger
row, but no schema or runtime code. The decision is recorded so
the next persona has a path to follow.
