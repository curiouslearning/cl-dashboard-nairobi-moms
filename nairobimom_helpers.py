"""
nairobimom_helpers.py

Data loading and computation helpers for the Nairobimom standalone dashboard.
Reads from a dedicated GCS parquet export (nairobimom_users) that covers only
the three nairobimom cohorts with a narrow column set.
"""

import pandas as pd
import streamlit as st


# ================================================@st.cache_data(show_spinner=False)============
# Cohort configuration
# ============================================================

# Maps URL query param ?cohort=momX → internal cohort_name in the parquet
COHORT_URL_MAP: dict[str, str] = {
    "njeri":   "app:nairobimomone_swahili_english-standalone",
    "laureen": "app:nairobimomtwo_swahili_english-standalone",
    "njambi":  "app:nairobimomthree_swahili_english-standalone",
}

COHORT_ALIAS: dict[str, str] = {
    "app:nairobimomone_swahili_english-standalone":   "Njeri",
    "app:nairobimomtwo_swahili_english-standalone":   "Laureen",
    "app:nairobimomthree_swahili_english-standalone": "Njambi",
}

DEFAULT_URL_KEY = "njeri"


# ============================================================
# Funnel step definitions
# ============================================================
# Each tuple: (abbreviation, display label, DataFrame column name)
FUNNEL_STEPS: list[tuple[str, str, str]] = [
    ("LR", "Learner Reached",  "lr_flag"),
    ("PC", "Puzzle Complete",  "pc_flag"),
    ("LA", "Learner Acquired",   "la_flag"),
    ("RA", "Reader Acquired",  "ra_flag"),
    ("GC", "Game Complete",    "gc_flag"),
]


# ============================================================
# Data loading
# ============================================================

@st.cache_data(ttl=3600, show_spinner=False)
def load_nairobimom_data() -> pd.DataFrame:
    """
    Query nairobimom users directly from BigQuery.
    Cached for 1 hour — adjust ttl as needed.
    """
    from settings import get_gcp_credentials

    sql = """
        SELECT
            u.cr_user_id,
            c.cohort_name,
            u.lr_flag,
            u.pc_flag,
            u.la_flag,
            u.ra_flag,
            u.gc_flag,
            u.max_user_level,
            u.total_time_minutes,
            u.engagement_event_count,
            u.avg_session_length_minutes,
            u.active_span,
            u.days_to_ra
        FROM `dataexploration-193817.user_data.cr_user_progress` u
        JOIN `dataexploration-193817.user_data.cr_cohorts` c
          ON u.cr_user_id = c.cr_user_id
        WHERE c.cohort_name IN (
            'app:nairobimomone_swahili_english-standalone',
            'app:nairobimomtwo_swahili_english-standalone',
            'app:nairobimomthree_swahili_english-standalone'
        )
    """
    _,client = get_gcp_credentials()
    return client.query(sql).to_dataframe()


def resolve_cohort(url_key: str) -> tuple[str, str]:
    """
    Given a URL key (e.g. 'mom2'), return (cohort_name, display_alias).
    Falls back to mom1 if the key is unrecognized.
    """
    key = (url_key or DEFAULT_URL_KEY).lower().strip()
    cohort_name = COHORT_URL_MAP.get(key, COHORT_URL_MAP[DEFAULT_URL_KEY])
    alias = COHORT_ALIAS[cohort_name]
    return cohort_name, alias


@st.cache_data(show_spinner=False)
def filter_cohort(df: pd.DataFrame, cohort_name: str) -> pd.DataFrame:
    return df.loc[df["cohort_name"] == cohort_name].copy()


# ============================================================
# Funnel computation
# ============================================================
@st.cache_data(show_spinner=False)
def compute_funnel(df: pd.DataFrame) -> list[dict]:
    """
    For each funnel step, compute user count and % of total users.

    Returns list of dicts:
        abbrev, label, count, pct_of_total, total
    """
    total = len(df)
    steps = []
    for abbrev, label, col in FUNNEL_STEPS:
        if col in df.columns:
            count = int(df[col].fillna(0).astype(int).sum())
        else:
            count = 0
        steps.append({
            "abbrev":       abbrev,
            "label":        label,
            "col":          col,
            "count":        count,
            "pct_of_total": count / total if total > 0 else 0.0,
            "total":        total,
        })
    return steps


# ============================================================
# Engagement metric computation
# ============================================================

def compute_engagement(df: pd.DataFrame) -> dict[str, float]:
    """
    Return per-user average engagement metrics.
    Keys match the tile labels used in the dashboard.
    """


    def _mean(col: str) -> float:
        if col not in df.columns or len(df) == 0:
            return 0.0
        return float(df[col].astype(float).dropna().mean() or 0.0)

    return {
        "Avg Level Reached":          _mean("max_user_level"),
        "Avg # Sessions / User":      _mean("engagement_event_count"),
        "Avg Total Play Time / User": _mean("total_time_minutes"),
        "Avg Session Length / User":  _mean("avg_session_length_minutes"),
        "Active Span / User":         _mean("active_span"),
        "Avg Days to RA":             _mean("days_to_ra"),
    }
