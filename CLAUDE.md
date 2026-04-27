# CL Dashboard - Nairobi Moms

## Project Overview
A standalone Streamlit dashboard for the three Nairobimom cohorts — Njeri, Laureen, and Njambi.
Single-page, filter-free. Cohort is selected via URL query parameter.

Deployed at: `https://dashboard-nairobi-moms.curiouslearning.org`

## Stack
- **Python 3.12**
- **Streamlit 1.56+**
- **Plotly** for charts
- **Pandas** for data
- **Google Cloud BigQuery** — direct query (no GCS parquet cache)
- **Google Cloud Secret Manager** — for GCP credentials
- **Cloud Run** — deployment target
- **GitHub** — source, connected to Cloud Build trigger

## Project Structure
```
main.py                  # Streamlit entry point, footer
.streamlit/
    config.toml          # Slate Teal theme
    pages.toml           # Navigation
app_pages/
    nairobimom.py        # Main dashboard page
nairobimom_helpers.py    # Data loading, cohort config, funnel computation
nairobimom_ui.py         # CSS injection, HTML tile renderers, Plotly charts
requirements.txt
Dockerfile
```

## Color Scheme: Slate Teal
```python
TEAL_DARK  = "#0D7377"   # primary / accent
TEAL_DEEP  = "#084C4F"   # text on colored elements
TEAL_TEXT  = "#032628"   # body text
TEAL_MUTED = "#5A8A8D"   # subtitle / muted text
# Theme
backgroundColor         = "#EDF4F4"
secondaryBackgroundColor = "#D5EBEB"
primaryColor            = "#0D7377"
textColor               = "#032628"
```

## Cohort Configuration
Defined in `nairobimom_helpers.py`. URL keys map to BigQuery cohort names:

| URL param     | Display name | BQ cohort_name                                      |
|---------------|--------------|-----------------------------------------------------|
| `?cohort=njeri`   | Njeri    | `app:nairobimomone_swahili_english-standalone`      |
| `?cohort=laureen` | Laureen  | `app:nairobimomtwo_swahili_english-standalone`      |
| `?cohort=njambi`  | Njambi   | `app:nairobimomthree_swahili_english-standalone`    |

Default: `njeri`. Unknown keys fall back to `njeri`.

## Data Loading
`load_nairobimom_data()` in `nairobimom_helpers.py`:
- Queries `cr_user_progress` JOIN `cr_cohorts` directly in BigQuery
- Filtered to the three nairobimom cohorts only
- Cached with `@st.cache_data(ttl=3600)`
- Returns a narrow DataFrame: funnel flags + engagement metrics only

GCP credentials via `get_gcp_credentials()` using Secret Manager secret:
`projects/405806232197/secrets/service_account_json/versions/latest`

BQ project: `dataexploration-193817`

## Funnel Steps
Defined in `FUNNEL_STEPS` in `nairobimom_helpers.py`:
```
LR  Learner Reached   lr_flag
PC  Puzzle Complete   pc_flag
LA  Level Acquired    la_flag
RA  Reader Acquired   ra_flag
GC  Game Complete     gc_flag
```
All flags are native columns in `cr_user_progress`.
`pc_flag`, `dc_flag`, `ts_flag`, `sl_flag` were added to the table as:
`CASE WHEN <event>_count > 0 THEN 1 ELSE 0 END`

## Key Patterns
- All styling and HTML renderers live in `nairobimom_ui.py`, not in the page file
- `inject_css()` must be called at the top of the page after `initialize()`
- Tile backgrounds use inline `background-color` (not CSS class) to avoid Streamlit stripping styles on the first column
- `filter_cohort()` and `compute_funnel()` are both `@st.cache_data` decorated for tab-switch performance

## Deployment
- Cloud Run, region `us-central1`
- Cloud Build trigger connected to GitHub repo `curiouslearning/cl-dashboard-nairobi-moms`
- Repo is **private** — Dockerfile must use `COPY . .` not `git clone`
- Custom domain managed via AWS Route 53, CNAME → `ghs.googlehosted.com`