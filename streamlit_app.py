"""brief-matrix calibration browser.

Reads the committed calibration ledger (data/ledger/*.jsonl) directly and
renders it as a ranked page. No network, no secrets, no writes. Paths are
resolved relative to this file so it runs the same locally and on
Streamlit Cloud.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import streamlit as st

from brief_matrix import score as score_engine
from brief_matrix.loader import TenantError, load_tenant

HERE = Path(__file__).resolve().parent
LEDGER_DIR = HERE / "data" / "ledger"
TENANTS_DIR = HERE / "tenants"
SAMPLE_BRIEF = HERE / "review-queue" / "procurement-analyst" / "2026-W34.md"

AXES = ("voice_score", "citation_score", "section_score")


def load_rows() -> list[dict]:
    rows: list[dict] = []
    if not LEDGER_DIR.is_dir():
        return rows
    for path in sorted(LEDGER_DIR.glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def composite(row: dict) -> float:
    return sum(float(row[a]) for a in AXES) / len(AXES)


st.set_page_config(page_title="brief-matrix calibration", layout="centered")
st.title("brief-matrix calibration browser")
st.caption(
    "weekly briefs scored on three axes -- voice discipline, citation "
    "coverage, section conformance -- read from the committed ledger."
)

rows = load_rows()
if not rows:
    st.warning(
        "no calibration rows found under data/ledger/. run "
        "`python -m brief_matrix calibrate` to score a brief first."
    )
    st.stop()

ranked = sorted(rows, key=lambda r: (composite(r), r.get("iso_week", "")), reverse=True)

tenants = sorted({r["tenant_id"] for r in rows})
mean_all = sum(composite(r) for r in rows) / len(rows)

c1, c2, c3 = st.columns(3)
c1.metric("scored briefs", len(rows))
c2.metric("tenants", len(tenants))
c3.metric("mean score", f"{mean_all:.2f}")

# Interactive control: filter the table to one tenant or show all.
choice = st.selectbox("tenant", ["all tenants", *tenants])
view = ranked if choice == "all tenants" else [r for r in ranked if r["tenant_id"] == choice]

table = [
    {
        "rank": i,
        "iso_week": r["iso_week"],
        "tenant": r["tenant_id"],
        "voice": round(float(r["voice_score"]), 2),
        "citation": round(float(r["citation_score"]), 2),
        "section": round(float(r["section_score"]), 2),
        "mean": round(composite(r), 2),
    }
    for i, r in enumerate(view, start=1)
]
st.dataframe(table, use_container_width=True, hide_index=True)

# Headline callout on the top brief in the current view.
top = view[0]
top_mean = composite(top)
weak_axis, weak_val = min(
    ((a.replace("_score", ""), float(top[a])) for a in AXES),
    key=lambda kv: kv[1],
)
if top_mean >= 0.999:
    st.info(
        f"top brief: {top['tenant_id']} {top['iso_week']} is clean on all "
        f"three axes -- ready to promote."
    )
else:
    st.info(
        f"top brief: {top['tenant_id']} {top['iso_week']} at {top_mean:.2f}; "
        f"weakest axis is {weak_axis} ({weak_val:.2f})."
    )

with st.expander("what the axes mean"):
    st.markdown(
        "- **voice**: 1.0 when the brief carries no banned phrasing.\n"
        "- **citation**: share of citation-required sections that carry an "
        "inline link.\n"
        "- **section**: share of the tenant's declared sections that are filled."
    )


# ---------------------------------------------------------------------------
# Score a brief yourself -- drives the real calibration engine live.
#
# This is not a lookup. The text below is written to a temp file and run
# through brief_matrix.score.score(brief_path, tenant), the exact function
# the `calibrate` CLI verb uses. Edit the brief, watch the three axes move.
# ---------------------------------------------------------------------------
st.divider()
st.header("score a brief yourself")
st.caption(
    "paste or edit a brief below and run it through the real calibration "
    "scorer (brief_matrix.score.score) against a live-loaded tenant spec. "
    "this is the same engine the calibrate CLI verb uses -- not a lookup."
)


def available_tenants() -> list[str]:
    if not TENANTS_DIR.is_dir():
        return []
    return sorted(p.name for p in TENANTS_DIR.iterdir() if (p / "config.yaml").is_file())


def default_brief_text() -> str:
    if SAMPLE_BRIEF.is_file():
        return SAMPLE_BRIEF.read_text(encoding="utf-8")
    return (
        "## intro\n\nYour theme for the week.\n\n"
        "## items\n\n1. An item with [a citation](https://example.invalid/x).\n\n"
        "## what-this-means\n\nThe implication for the reader.\n\n"
        "## footer\n\nSource roll-up ([roll-up](https://example.invalid/x)).\n"
    )


tenant_names = available_tenants()
if not tenant_names:
    st.warning("no tenant specs found under tenants/. cannot score live.")
else:
    sel_tenant = st.selectbox("tenant spec to score against", tenant_names)

    try:
        tenant = load_tenant(TENANTS_DIR / sel_tenant)
    except TenantError as exc:  # malformed tenant dir
        st.error(f"could not load tenant '{sel_tenant}': {exc}")
        tenant = None

    if tenant is not None:
        st.caption(
            f"declared sections: {', '.join(tenant.section_names)} -- "
            "drop a heading, remove a citation, or paste a banned word "
            "(e.g. 'leverage', 'synergy') to watch an axis collapse."
        )
        brief_text = st.text_area(
            "brief markdown",
            value=default_brief_text(),
            height=360,
            key="brief_text",
        )

        # Write the user's text to a temp file and call the REAL scorer.
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as fh:
            fh.write(brief_text)
            tmp_path = Path(fh.name)
        try:
            result = score_engine.score(tmp_path, tenant)
        finally:
            tmp_path.unlink(missing_ok=True)

        composite_live = (
            result.voice_score + result.citation_score + result.section_score
        ) / 3.0

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("voice", f"{result.voice_score:.2f}")
        m2.metric("citation", f"{result.citation_score:.2f}")
        m3.metric("section", f"{result.section_score:.2f}")
        m4.metric("mean", f"{composite_live:.2f}")

        if result.voice_hits:
            st.error(
                "voice gate failed -- banned phrasing present: "
                + ", ".join(f"`{h}`" for h in result.voice_hits)
            )
        else:
            st.success("voice gate clean -- no banned phrasing.")

        declared = set(result.sections_declared)
        filled = set(result.sections_filled)
        missing = [s for s in result.sections_declared if s not in filled]
        if missing:
            st.warning(
                f"sections filled {len(filled)}/{len(declared)} -- missing: "
                + ", ".join(f"`{s}`" for s in missing)
            )
        else:
            st.info("all declared sections present.")

        if result.citation_score < 1.0:
            cite_required = [
                s["name"]
                for s in tenant.section_structure
                if s.get("requires_citation", True)
            ]
            st.warning(
                f"citation coverage {result.citation_score:.2f} -- "
                f"sections that require an inline link: "
                + ", ".join(f"`{s}`" for s in cite_required)
            )

        with st.expander("raw scorer output"):
            st.json(
                {
                    "voice_score": result.voice_score,
                    "citation_score": result.citation_score,
                    "section_score": result.section_score,
                    "voice_hits": result.voice_hits,
                    "sections_declared": result.sections_declared,
                    "sections_filled": result.sections_filled,
                }
            )
