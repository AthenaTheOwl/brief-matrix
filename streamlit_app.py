"""brief-matrix calibration browser.

Reads the committed calibration ledger (data/ledger/*.jsonl) directly and
renders it as a ranked page. No network, no secrets, no writes. Paths are
resolved relative to this file so it runs the same locally and on
Streamlit Cloud.
"""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

HERE = Path(__file__).resolve().parent
LEDGER_DIR = HERE / "data" / "ledger"

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
