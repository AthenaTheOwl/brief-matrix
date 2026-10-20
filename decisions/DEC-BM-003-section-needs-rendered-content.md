# DEC-BM-003 — A section needs rendered content to count

- **Status:** accepted
- **Decided:** 2026-10-18
- **Applies to:** brief_matrix/score.py, docs/METHODOLOGY.md

## Context

DEC-BM-002 defined `section_score` as declared sections present over
declared sections, and the scorer counted a section as present when a
matching H2 heading appeared anywhere in the brief. A draft of four
empty headings, or of headings followed only by editorial
`<!-- ... -->` notes, scored 1.0 on shape while a reader saw nothing
under them.

## Decision

This entry records a change already merged in PR #2 (commit 5dda90a).
A declared section is present only when its H2 heading has rendered
content below it:

- HTML comments are removed before headings are matched, so a heading
  inside a comment does not count, and a heading followed only by
  comments is empty.
- Bare link reference definitions (`[label]: https://...`) do not
  count as content.
- A link inside an HTML comment does not count toward
  `citation_score`.

Comments are removed the way a CommonMark renderer hides them: a line
opening with `<!--` starts a comment block that runs to the first
`-->` (or the end of the file); any other comment must close within
its paragraph; fenced code is left alone.

## Reversibility

Cheap. The rule lives in `_sections_filled` and `_split_by_heading`;
no schema field changes. Ledger rows scored before this change used the
heading-only rule; the fixture brief scores the same under both.
