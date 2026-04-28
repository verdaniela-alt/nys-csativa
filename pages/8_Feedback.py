"""
8_Feedback.py — User Survey / Feedback page.
NYS Cannabis & Hemp Grower Tools.
Responses are stored in a Google Sheet via gspread (if configured);
falls back to a local CSV if the Sheets connection is unavailable.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import datetime
from utils.sidebar import render_sidebar

st.set_page_config(
    page_title="Feedback | NYS Cannabis Tool",
    page_icon="💬",
    layout="wide",
)
render_sidebar()

# ── NYS Counties ──────────────────────────────────────────────────────────────
NYS_COUNTIES = [
    "Albany", "Allegany", "Bronx", "Broome", "Cattaraugus", "Cayuga",
    "Chautauqua", "Chemung", "Chenango", "Clinton", "Columbia", "Cortland",
    "Delaware", "Dutchess", "Erie", "Essex", "Franklin", "Fulton", "Genesee",
    "Greene", "Hamilton", "Herkimer", "Jefferson", "Kings (Brooklyn)",
    "Lewis", "Livingston", "Madison", "Monroe", "Montgomery", "Nassau",
    "New York (Manhattan)", "Niagara", "Oneida", "Onondaga", "Ontario",
    "Orange", "Orleans", "Oswego", "Otsego", "Putnam", "Queens",
    "Rensselaer", "Richmond (Staten Island)", "Rockland", "St. Lawrence",
    "Saratoga", "Schenectady", "Schoharie", "Schuyler", "Seneca",
    "Steuben", "Suffolk", "Sullivan", "Tioga", "Tompkins", "Ulster",
    "Warren", "Washington", "Wayne", "Westchester", "Wyoming", "Yates",
]

# ── Google Sheets backend (optional) ─────────────────────────────────────────
_SHEET_CONFIGURED = False
_GSPREAD_AVAILABLE = False

try:
    import gspread
    _GSPREAD_AVAILABLE = True
except ImportError:
    pass

def _get_sheet():
    """Return gspread Worksheet or None if not configured."""
    if not _GSPREAD_AVAILABLE:
        return None
    try:
        creds_dict = st.secrets.get("gcp_service_account", None)
        sheet_url  = st.secrets.get("feedback_sheet_url", None)
        if creds_dict is None or sheet_url is None:
            return None
        gc = gspread.service_account_from_dict(dict(creds_dict))
        sh = gc.open_by_url(sheet_url)
        return sh.sheet1
    except Exception:
        return None


_FALLBACK_CSV = os.path.join(os.path.dirname(__file__), "..", "resources", "feedback_responses.csv")

_COLUMNS = [
    "timestamp", "user_type", "age_range", "sex", "orientation",
    "nys_resident", "county", "role", "suggestions",
]

def _append_response(row: dict):
    """Write one response row. Tries Google Sheets first, then local CSV."""
    ws = _get_sheet()
    if ws is not None:
        try:
            # Ensure header row exists
            existing = ws.get_all_values()
            if not existing:
                ws.append_row(_COLUMNS)
            ws.append_row([row.get(c, "") for c in _COLUMNS])
            return "sheets"
        except Exception:
            pass
    # Fallback: local CSV
    os.makedirs(os.path.dirname(_FALLBACK_CSV), exist_ok=True)
    df_new = pd.DataFrame([row])[_COLUMNS]
    if os.path.exists(_FALLBACK_CSV):
        df_new.to_csv(_FALLBACK_CSV, mode="a", header=False, index=False)
    else:
        df_new.to_csv(_FALLBACK_CSV, mode="w", header=True, index=False)
    return "csv"


# ── Page ──────────────────────────────────────────────────────────────────────
st.title("💬 Site Feedback & User Survey")
st.caption(
    "Help us improve these tools! Your responses are anonymous and take about 2 minutes. "
    "No personally identifiable information is collected."
)

st.info(
    "**Privacy note:** Responses include only aggregate demographic categories and text you "
    "voluntarily provide. No names, email addresses, or precise location data are collected. "
    "Data is used solely to understand who is using these tools and how to improve them.",
    icon="🔒",
)

st.divider()

with st.form("feedback_form", clear_on_submit=True):

    # ── Returning vs New ──────────────────────────────────────────────────────
    st.subheader("1. Visit type")
    user_type = st.radio(
        "Is this your first time using these tools?",
        ["First visit", "Returning user"],
        horizontal=True,
    )

    st.divider()

    # ── Demographics ──────────────────────────────────────────────────────────
    st.subheader("2. About you  *(optional — all fields)*")
    st.caption("All demographic questions are optional. Select 'Prefer not to say' to skip.")

    dcol1, dcol2, dcol3 = st.columns(3)

    with dcol1:
        age_range = st.selectbox(
            "Age range",
            ["Prefer not to say", "18–24", "25–34", "35–44", "45–54", "55–64", "65+"],
        )

    with dcol2:
        sex = st.selectbox(
            "Sex",
            ["Prefer not to say", "Female", "Male", "Intersex", "Other"],
        )

    with dcol3:
        orientation = st.selectbox(
            "Sexual orientation",
            [
                "Prefer not to say",
                "Straight / Heterosexual",
                "Gay or Lesbian",
                "Bisexual",
                "Queer",
                "Asexual",
                "Other",
            ],
        )

    st.divider()

    # ── Location ──────────────────────────────────────────────────────────────
    st.subheader("3. Location")
    nys_resident = st.radio(
        "Are you located in New York State?",
        ["Yes", "No / Outside NYS", "Prefer not to say"],
        horizontal=True,
    )

    county = ""
    if nys_resident == "Yes":
        county = st.selectbox(
            "Which NYS county are you in? *(optional)*",
            ["— select county —"] + NYS_COUNTIES,
        )
        if county == "— select county —":
            county = ""

    st.divider()

    # ── Role ──────────────────────────────────────────────────────────────────
    st.subheader("4. Your role  *(optional)*")
    role = st.selectbox(
        "Which best describes your primary role?",
        [
            "Prefer not to say",
            "Licensed cannabis cultivator (OCM)",
            "Licensed hemp grower",
            "Applicant / prospective licensee",
            "Processor / extractor",
            "Retailer / dispensary operator",
            "Agronomist / crop advisor (CCA)",
            "Researcher / academic",
            "Extension educator / advisor",
            "Student",
            "Other",
        ],
    )

    st.divider()

    # ── Suggestions ───────────────────────────────────────────────────────────
    st.subheader("5. Suggestions")
    suggestions = st.text_area(
        "What would you like to see improved or added to these tools?",
        placeholder="e.g., 'Add a pesticide lookup tool', 'The soil tool doesn't load my county correctly', …",
        height=130,
    )

    st.write("")
    submitted = st.form_submit_button("Submit feedback", type="primary", use_container_width=False)


# ── Handle submission ─────────────────────────────────────────────────────────
if submitted:
    row = {
        "timestamp":    datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "user_type":    user_type,
        "age_range":    age_range,
        "sex":          sex,
        "orientation":  orientation,
        "nys_resident": nys_resident,
        "county":       county,
        "role":         role,
        "suggestions":  suggestions.strip(),
    }
    backend = _append_response(row)
    st.success(
        "Thank you for your feedback! Your response has been recorded.",
        icon="✅",
    )
    if backend == "csv":
        st.caption("_(Stored locally — Google Sheets not configured.)_")

st.divider()
st.caption(
    "NYS Cannabis & Hemp Grower Tools · Cornell University · "
    "Feedback data used only for tool improvement · No PII collected."
)
