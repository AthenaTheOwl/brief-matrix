# BriefMatrix

Multi-tenant, persona-conditioned weekly brief platform. Any niche topic, any audience, with the same spec-driven structure, voice discipline, citation-faithfulness, and review-queue promotion shipped in ai-field-brief.

## What this is

ai-field-brief is the live single-tenant reference. BriefMatrix is the
shape that pattern takes when more than one persona uses it. The four
shipped control planes (spec ledger, voice-lint banlist, citation-
faithfulness check, review-queue promotion) become per-tenant
configuration; the brief-generation runtime is shared.

A "brief" here is a typed artifact, not a Substack post:

- spec ledger names the structure of the brief
- a fetcher per source pulls candidate items
- a synthesizer drafts the brief with explicit citations
- voice-lint refuses the draft if it carries banned phrasing
- the review queue holds the draft until a human approves

BriefMatrix is the platform layer that runs this loop for N tenants in
one repo, with one shared infrastructure and N tenant-isolated
configurations.

## Who uses it

Newsletter publishers who want spec-driven brief discipline instead of
ad-hoc summarization. In-house analyst teams at financial firms that
need a citable weekly artifact. Niche-community moderators who want a
brief that does not drift into hype. Industry trade associations.
University research-group communications leads.

## Why now

The newsletter market is saturating on undifferentiated AI summarization.
The spec-driven, voice-gated brief is a recognizable shape. The
ai-field-brief stack ships the discipline; BriefMatrix turns it into a
multi-tenant primitive so the discipline does not get reinvented per
publisher.

## Status


v0.1 shipped -- runnable, minimal. The scorer, loader, voice gate,
calibration ledger, and CLI (`validate` / `calibrate` / `ledger` /
`show`) are real and tested; one procurement-analyst tenant and one
scored row ship as fixtures. The three-axis scorer (voice, citation,
section) is the core deliverable. Next passes deepen it: a second
tenant fixture for multi-tenant isolation, real-data backfill. See
`STATUS.md` for the next-feature queue.

## How to run

The CLI scores briefs and keeps a calibration ledger. Nothing here
reaches the network; the bundled procurement-analyst tenant and one
scored row ship as checked-in fixtures.

```
python -m brief_matrix validate                         # check the tenant config
python -m brief_matrix calibrate \                       # score a brief, append a ledger row
  --tenant tenants/procurement-analyst \
  --brief review-queue/procurement-analyst/2026-W34.md
python -m brief_matrix ledger                            # print every ledger row
python -m brief_matrix show                              # ranked, readable rollup
```

`show` reads the committed ledger and prints the rows ranked by their
mean score, plus a one-line headline on the top brief:

```
brief-matrix -- calibration rollup
1 scored brief(s) across 1 tenant(s)

 #  iso_week   tenant                   voice    cit    sec   mean
------------------------------------------------------------------
 1  2026-W25   procurement-analyst       1.00   1.00   1.00   1.00

headline: procurement-analyst 2026-W25 is clean on all three axes
(voice/citation/section) -- ready to promote.
```

## live demo

A read-only Streamlit page renders the same calibration rollup as an
interactive browser: pick a tenant, see the ranked table, the three
axis scores, and a headline on the top brief.

Run it locally:

```
python -m uv run --with streamlit streamlit run streamlit_app.py
# or, with a plain venv:
pip install -r requirements.txt && streamlit run streamlit_app.py
```

Deploy on Streamlit Cloud: repo `AthenaTheOwl/brief-matrix`, branch
`main`, main file `streamlit_app.py`.

<!-- live-url: (paste the Streamlit Cloud URL here once deployed) -->

## Layout

```
brief-matrix/
  brief_matrix/            multi-tenant runtime (loader, scorer, voice gate, ledger, cli)
    fetchers/              one module per source class (fixture fetcher today)
  tenants/<tenant-id>/     per-tenant config, source registry, spec ledger, voice overrides
  review-queue/<tenant-id>/  drafts awaiting a score
  data/ledger/             append-only calibration rows (one .jsonl per iso-week + tenant)
  schemas/                 tenant, brief, review-record, calibration-run schemas
  streamlit_app.py         read-only calibration browser
  tests/                   pytest suite
```

## License

MIT. See [LICENSE](LICENSE).
