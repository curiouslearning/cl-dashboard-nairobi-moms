"""
nairobimom_ui.py  —  Styling, HTML tile renderers, and charts for the Nairobimom dashboard.
"""

import streamlit as st
import plotly.graph_objects as go


# ============================================================
# Color palette
# ============================================================
TEAL_DARK = "#0D7377"
TEAL_DEEP = "#084C4F"
TEAL_TEXT = "#032628"
TEAL_MUTED = "#5A8A8D"

FUNNEL_COLORS = [
    "#C5E3E3",
    "#B8DCDC",
    "#ABD5D5",
    "#9ECECE",
    "#91C7C5",
]


# ============================================================
# CSS
# ============================================================
def inject_css():
    st.markdown("""
    <style>
    .nm-tile-label {
        margin: 0;
        font-size: 10px;
        font-weight: 600;
        letter-spacing: 0.4px;
        text-transform: uppercase;
        opacity: 0.72;
    }
    .block-container {
    padding-top: 3rem !important;
    }
    .nm-tile-abbrev {
        margin: 0;
        font-size: 9px;
        letter-spacing: 0.3px;
        opacity: 0.5;
    }
    .nm-tile-value {
        margin: 1px 0 0;
        font-size: 22px;
        font-weight: 700;
        line-height: 1.1;
    }
    .nm-tile-sub {
        margin: 0;
        font-size: 10px;
        opacity: 0.6;
    }
    .nm-section-header {
        font-size: 13px;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        color: #5A8A8D;
        margin: 0 0 10px;
        padding-bottom: 6px;
        border-bottom: 1.5px solid #C0E0E0;
    }
    .nm-cohort-badge {
        display: inline-block;
        background: #0D7377;
        color: #fff;
        border-radius: 8px;
        padding: 4px 14px;
        font-size: 13px;
        font-weight: 600;
        letter-spacing: 0.3px;
        margin-left: 10px;
        vertical-align: middle;
    }
    .nm-cohort-raw {
        font-size: 11px;
        color: #5A8A8D;
        margin-top: 2px;
    }
    .nm-switcher {
        display: flex;
        gap: 8px;
        margin-bottom: 20px;
        flex-wrap: wrap;
    }
    .nm-switcher a {
        background: #D5EBEB;
        color: #032628;
        border-radius: 6px;
        padding: 5px 14px;
        font-size: 12px;
        font-weight: 500;
        text-decoration: none;
        border: 1.5px solid transparent;
    }
    .nm-switcher a.active {
        background: #0D7377;
        color: #fff;
        border-color: #0D7377;
    }
    </style>
    """, unsafe_allow_html=True)


# ============================================================
# HTML renderers
# ============================================================

def funnel_tile_html(abbrev: str, label: str, count: int, pct: float, bg: str) -> str:
    return f"""
    <div style="background-color:{bg}; border-radius:8px; padding:12px 8px 10px;
                text-align:center; height:110px; display:flex; flex-direction:column;
                justify-content:center; gap:2px; margin-bottom:8px;">
        <p class="nm-tile-label" style="color:{TEAL_TEXT};">{label}</p>
        <p class="nm-tile-abbrev" style="color:{TEAL_TEXT};">{abbrev}</p>
        <p class="nm-tile-value" style="color:{TEAL_DEEP};">{count:,}</p>
        <p class="nm-tile-sub" style="color:{TEAL_TEXT};">{pct:.1%} of total</p>
    </div>
    """


def user_count_html(total_users: int) -> str:
    return f"<p class='nm-cohort-raw'>{total_users:,} users</p>"


def switcher_html(url_key: str) -> str:
    html = "<div class='nm-switcher'>"
    for key, name in [("njeri", "Njeri"), ("laureen", "Laureen"), ("njambi", "Njambi")]:
        active_class = "active" if key == url_key.lower() else ""
        html += f"<a href='?cohort={key}' target='_self' class='{active_class}'>{name}</a>"
    html += "</div>"
    return html


# ============================================================
# Funnel drop-off chart
# ============================================================

def funnel_dropoff_chart(funnel_steps: list[dict]) -> go.Figure:
    """
    Area + line chart showing % of total users reaching each funnel step.
    Visually emphasises the drop-off shape across the funnel.
    """
    labels = [f"{s['abbrev']}<br><span style='font-size:10px'>{s['label']}</span>"
              for s in funnel_steps]
    pcts = [round(s["pct_of_total"] * 100, 1) for s in funnel_steps]
    counts = [s["count"] for s in funnel_steps]

    fig = go.Figure()

    # Filled area
    fig.add_trace(go.Scatter(
        x=labels,
        y=pcts,
        mode="lines+markers",
        fill="tozeroy",
        fillcolor="rgba(13, 115, 119, 0.12)",
        line=dict(color=TEAL_DARK, width=2.5),
        marker=dict(color=TEAL_DARK, size=8),
        customdata=counts,
        hovertemplate=(
            "<b>%{x}</b><br>"
            "%{y:.1f}% of total<br>"
            "%{customdata:,} users<extra></extra>"
        ),
    ))

    # Annotate each point with the percentage
    for i, (label, pct, count) in enumerate(zip(labels, pcts, counts)):
        fig.add_annotation(
            x=label,
            y=pct,
            text=f"<b>{pct:.1f}%</b><br>{count:,}",
            showarrow=False,
            yshift=22,
            font=dict(size=11, color=TEAL_DEEP),
            align="center",
        )

    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(
            tickformat=".0f",
            ticksuffix="%",
            range=[0, 115],
            showgrid=True,
            gridcolor="rgba(0,0,0,0.06)",
            zeroline=False,
            title=None,
        ),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            title=None,
        ),
        showlegend=False,
        height=320,
    )

    return fig
