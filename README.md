# brief-matrix

Two tenant rulebooks now share one scorer without sharing one another's escape
hatches. Procurement analysis and municipal budget monitoring carry different sections
and vocabulary, while the shared banlist remains a floor neither tenant can weaken.
The calibration ledger still has one scored brief, so the next useful evidence is a
municipal row rather than another configuration file.

## What it does

A weekly brief is easy to write and easy to let rot. The first one cites its
sources; the tenth quietly stops. brief-matrix is the runtime that refuses to let
that happen across more than one publisher at a time. A brief here is a typed
artifact with a spec ledger naming its sections, a fetcher per source pulling
candidates, a synthesizer drafting with explicit citations, a voice gate that
rejects banned phrasing, and a review queue that holds the draft until a human signs
off.

[ai-field-brief](https://github.com/AthenaTheOwl/ai-field-brief) is the live
single-tenant version of that loop. brief-matrix is the shape it takes when the loop
has to run for N tenants out of one repo. The four control planes — spec ledger,
voice banlist, citation check, review-queue promotion — become per-tenant
configuration; the generation runtime is shared. Removing a shared banned term from
a tenant's override file is rejected, so a publisher can add discipline but not opt
out of it.

The three-axis scorer is the core of it: every draft gets scored on voice, citation
coverage, and section conformance, and the result lands as an append-only row in the
ledger. Section conformance requires reader-facing content below each declared
heading; an empty heading or an editorial comment does not complete the section.
v0.1 ships procurement-analyst and municipal-budget-watch tenant contracts,
plus one scored procurement row. An isolation test proves one tenant's overrides cannot
weaken the other's banlist. The data adapter remains a fixture fetcher.

## Try it

The CLI validates both tenant contracts, scores drafts, records human promotion, and
keeps a calibration ledger. Nothing reaches the network; the tenant rules and the first
procurement calibration row are checked-in fixtures.

```
python -m brief_matrix validate --tenant tenants/procurement-analyst
python -m brief_matrix validate --tenant tenants/municipal-budget-watch
python -m brief_matrix calibrate \                       # score a brief, append a ledger row
  --tenant tenants/procurement-analyst \
  --brief review-queue/procurement-analyst/2026-W34.md
python -m brief_matrix promote \                         # record the human decision
  --tenant tenants/procurement-analyst \
  --brief review-queue/procurement-analyst/2026-W34.md \
  --reviewer reviewer-id
python -m brief_matrix ledger                            # print every ledger row
python -m brief_matrix show                              # ranked, readable rollup
```

`show` reads the committed ledger and prints the rows ranked by their mean score,
plus a one-line headline on the top brief:

```
brief-matrix -- calibration rollup
1 scored brief(s) across 1 tenant(s)

 #  iso_week   tenant                   voice    cit    sec   mean
------------------------------------------------------------------
 1  2026-W25   procurement-analyst       1.00   1.00   1.00   1.00

headline: procurement-analyst 2026-W25 is clean on all three axes
(voice/citation/section) -- ready to promote.
```

A brief at 1.00/1.00/1.00 is eligible for promotion; the promote command records
who accepted it and appends the review decision exactly once. A brief that slipped on
any axis stays in the review queue until someone fixes and recalibrates it.

## Live demo

A read-only Streamlit page renders the same calibration rollup as an interactive
browser: pick a tenant, see the ranked table, the three axis scores, and a headline
on the top brief.

Run it locally:

```
python -m uv run --with streamlit streamlit run streamlit_app.py
# or, with a plain venv:
pip install -r requirements.txt && streamlit run streamlit_app.py
```

Deploy on Streamlit Cloud: repo `AthenaTheOwl/brief-matrix`, branch `main`, main
file `streamlit_app.py`.

<!-- live-url: (paste the Streamlit Cloud URL here once deployed) -->

## How it connects

- [ai-field-brief](https://github.com/AthenaTheOwl/ai-field-brief) — the live
  single-tenant reference. It ships the discipline; brief-matrix turns it into a
  multi-tenant primitive so the discipline doesn't get reinvented per publisher.

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
