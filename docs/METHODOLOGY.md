# BriefMatrix Calibration Methodology

How the runtime scores a brief, and how the three axes are intended
to be read together. This document is the source of truth for the
calibration ledger; changes to a score definition require a new
`decisions/DEC-BM-NNN-*.md` entry.

## Why three axes

A single composite score hides which dimension regressed between
weeks. The three axes are intentionally independent so each row in
the ledger can be diffed on its own.

1. **Voice score** — discipline. Did the draft stay inside the
   shared voice constraint?
2. **Citation score** — sourcing. Does each declared section carry
   a verifiable inline link?
3. **Section score** — shape. Did the draft fill the section
   structure declared by the tenant's spec ledger?

Voice is binary. Citations and sections are continuous.

## Voice score

```
voice_score = 1.0 if voice_gate.check(body, merged_banlist) passes
              else 0.0
```

The merged banlist is `BANNED_FAIL` from
`brief_matrix/voice_gate.py` union the tenant's
`voice_overrides.yaml::extra_banned` list. Overrides may extend the
banlist; they may not shrink it (the loader rejects an override
that tries to remove a shared term).

Voice is binary because the brand promise is a discipline guarantee.
A "mostly-passed" voice draft has the same downstream shape as a
draft with no gate at all: a human reader still encounters a banned
phrase, the trust contract still breaks. Partial credit would dilute
the signal the ledger exists to carry.

## Citation score

```
citation_score = sections_with_at_least_one_link / declared_sections
```

A section "has a citation" when its body (the text under the H2
heading whose name matches a declared section) contains at least
one inline Markdown link to an `http://` or `https://` URL.

If the brief carries zero inline links at all, `citation_score`
collapses to `0.0` regardless of section count. This catches the
degenerate case where the synthesizer omitted citations entirely
but the section headings still match.

The score is structural, not semantic. v0.1 does NOT fetch the
cited URL and check that the page actually supports the inline
claim. Semantic faithfulness is named in DEC-BM-002 and deferred
to a later spec.

## Section score

```
section_score = declared_sections_present / declared_sections
```

A section is "present" when an H2 heading in the brief matches a
declared section name (case-insensitive). Extra H2 headings that
do not match a declared section do not raise the score; they
appear in the row's `notes` field for the reviewer to inspect.

Missing sections lower the score. The synthesizer is required to
fill the declared shape; inventing new sections is a separate
concern recorded in DEC-BM-002.

## Worked example — 2026-W34 procurement brief

The fixture brief at
`review-queue/procurement-analyst/2026-W34.md` carries:

- Four H2 headings: `intro`, `items`, `what-this-means`, `footer`.
- The tenant declares the same four section names in
  `specs/section-structure.yaml`.
- Every section body contains at least one inline link to an
  `https://example.invalid/...` URL.
- The body uses none of the BANNED_FAIL terms.

By the definitions above:

- `voice_score = 1.0`
- `citation_score = 4 / 4 = 1.0`
- `section_score = 4 / 4 = 1.0`

The checked-in row at
`data/ledger/2026-W25-procurement-analyst-calibration-run.jsonl`
records exactly these numbers. A reader can recompute by hand from
the fixture and arrive at the same result; this is the test of
whether the methodology is operational.

## What a row is FOR

A row is the seed of a diff. The interesting question is never
"what is the score this week?" — it is "which axis moved relative
to last week, and why?" The ledger is append-only so that the
answer is auditable.

## What revisits this

This document is not a one-shot artifact. The following events
require an edit here, paired with a new `decisions/DEC-BM-NNN-*.md`
entry:

- **Adding a fourth axis.** Semantic citation-faithfulness is the
  named candidate (DEC-BM-002). When that lands, the "Why three
  axes" section becomes "Why N axes" and the new axis gets its own
  formula block with worked numbers.
- **Changing voice from binary to continuous.** Today voice is
  intentionally binary. If a future decision flips that, the
  rationale paragraph above is the load-bearing claim that has to
  be revisited and either rewritten or retired.
- **Changing the citation-score collapse rule.** The "zero links
  collapses to 0.0" clause was a deliberate choice. Removing or
  altering it changes the meaning of every historical row and
  requires a methodology version bump.
- **Bumping the calibration-run schema.** A `schema_version`
  change in `schemas/calibration-run.schema.json` means the row
  shape changed; the worked example above no longer matches
  reality, and the bump must be reflected here so future readers
  can reconcile old rows against new ones.
- **Replacing the fixture worked example.** If the
  `procurement-analyst` 2026-W34 brief is retired or rewritten,
  the worked-example section must be regenerated against whatever
  replaces it, or the document silently becomes wrong.

Revisits are a feature of the ledger, not a sign the methodology
is unstable. Each revision is paired with the decision that drove
it, so a reader walking from a current row backward through the
ledger can always reconstruct the scoring rule in force at the
time the row was written.
