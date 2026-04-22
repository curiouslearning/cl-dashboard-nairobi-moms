"""
nairobimom.py  —  Nairobimom Cohort Dashboard

Single-page, filter-free dashboard for the three Nairobimom cohorts.
Cohort is selected via URL query parameter:
    ?cohort=mom1   →  Mom 1  (nairobimomone_swahili_english-standalone)
    ?cohort=mom2   →  Mom 2  (nairobimomtwo_swahili_english-standalone)
    ?cohort=mom3   →  Mom 3  (nairobimomthree_swahili_english-standalone)
"""

import streamlit as st

from settings import initialize
import nairobimom_helpers as nh
import nairobimom_ui as ui


initialize()
ui.inject_css()

# ============================================================
# URL param → cohort
# ============================================================
url_key = st.query_params.get("cohort", nh.DEFAULT_URL_KEY)
cohort_name, alias = nh.resolve_cohort(url_key)

# ============================================================
# Load + filter data
# ============================================================
with st.spinner("Loading data…"):
    df_all = nh.load_nairobimom_data()

df = nh.filter_cohort(df_all, cohort_name)
total_users = len(df)

# ============================================================
# Page header
# ============================================================
st.markdown(
    f"## Nairobi Moms Cohort Dashboard "
    f"<span class='nm-cohort-badge'>{alias}</span>",
    unsafe_allow_html=True,
)
st.markdown(ui.user_count_html(total_users), unsafe_allow_html=True)
st.markdown(ui.switcher_html(url_key), unsafe_allow_html=True)


# ============================================================
# Funnel tiles — single row of 5
# ============================================================
funnel_steps = nh.compute_funnel(df)

st.markdown("<p class='nm-section-header'>Funnel</p>", unsafe_allow_html=True)

cols = st.columns(5)
for i, step in enumerate(funnel_steps):
    with cols[i]:
        st.markdown(
            ui.funnel_tile_html(
                abbrev=step["abbrev"],
                label=step["label"],
                count=step["count"],
                pct=step["pct_of_total"],
                bg=ui.FUNNEL_COLORS[i],
            ),
            unsafe_allow_html=True,
        )

# ============================================================
# Funnel drop-off chart
# ============================================================
st.plotly_chart(
    ui.funnel_dropoff_chart(funnel_steps),
    width='content'
)
