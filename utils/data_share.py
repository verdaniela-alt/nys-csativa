"""
Shared data-sharing consent UI and Google Sheets backend used by all tool pages.
Uses the same gcp_service_account / feedback_sheet_url secrets as 8_Feedback.py,
but writes to separate tabs so grower data stays separate from user feedback.
"""
import streamlit as st
import datetime

_GSPREAD_AVAILABLE = False
try:
    import gspread
    _GSPREAD_AVAILABLE = True
except ImportError:
    pass

NYS_COUNTIES = [
    "— select county (optional) —",
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
    "Outside NYS",
]


def _get_or_create_tab(tab_name: str):
    """Return a gspread Worksheet for tab_name, creating it if it doesn't exist."""
    if not _GSPREAD_AVAILABLE:
        return None
    try:
        creds = st.secrets.get("gcp_service_account")
        url   = st.secrets.get("feedback_sheet_url")
        if not creds or not url:
            return None
        gc = gspread.service_account_from_dict(dict(creds))
        sh = gc.open_by_url(url)
        try:
            return sh.worksheet(tab_name)
        except gspread.WorksheetNotFound:
            return sh.add_worksheet(title=tab_name, rows=1000, cols=60)
    except Exception:
        return None


def _write_rows(tab_name: str, columns: list, rows: list):
    """Append one or more anonymized data rows to the named sheet tab."""
    ws = _get_or_create_tab(tab_name)
    if ws is None:
        return
    try:
        existing = ws.get_all_values()
        if not existing:
            ws.append_row(columns)
        for row in rows:
            ws.append_row([str(row.get(c, "")) for c in columns])
    except Exception:
        pass


def render_share_block(
    tool_key: str,
    tab_name: str,
    columns: list,
    row_builder,
    county_widget: bool = False,
):
    """
    Render the data-sharing consent block at the end of a tool results section.

    tool_key:      short ID used for session state keys ("soil", "econ", "crop", "cip")
    tab_name:      Google Sheet tab to write to (e.g. "Soil Data")
    columns:       ordered list of column names; must include "timestamp"
    row_builder:   callable(county: str) -> list[dict]
                   county is "" when county_widget=False
    county_widget: if True, show an optional NYS county selector before the buttons
    """
    st.divider()
    st.markdown("### Would you like to share your data with us?")
    st.info(
        "Sharing is entirely voluntary and helps us improve these tools for NYS growers.\n\n"
        "**What we collect — and what we do NOT collect:**\n"
        "- Your location is reduced to **county only** to avoid identifying your farm — "
        "no address, street name, or GPS coordinates are ever stored\n"
        "- **No personally identifying information** of any kind — no names, emails, "
        "phone numbers, or business names — pure agronomic and financial data only\n"
        "- **No batch numbers** or any identifier that could trace back to a specific "
        "grower — all crop data is fully anonymized before being recorded\n"
        "- For the CIP tool: only **county and license type** are shared — "
        "no applicant name, address, or contact details\n\n"
        "Selecting **No** sends nothing. Your data stays on your device.",
        icon="🔒",
    )

    done_key   = f"_share_{tool_key}_done"
    choice_key = f"_share_{tool_key}_choice"
    county_key = f"_share_{tool_key}_county"

    if st.session_state.get(done_key):
        if st.session_state.get(choice_key) == "yes":
            st.success("Thank you! Your anonymized data has been shared with us.", icon="✅")
        else:
            st.info("No problem — your data was not shared.", icon="👍")
        return

    county = ""
    if county_widget:
        sel = st.selectbox(
            "Your county *(optional — helps us understand regional patterns)*",
            NYS_COUNTIES,
            key=county_key,
        )
        county = "" if sel.startswith("—") else sel

    col1, col2, _ = st.columns([1, 1, 4])
    with col1:
        yes_btn = st.button(
            "Yes, share my data",
            key=f"_share_{tool_key}_yes",
            type="primary",
            use_container_width=True,
        )
    with col2:
        no_btn = st.button(
            "No, keep my data private",
            key=f"_share_{tool_key}_no",
            use_container_width=True,
        )

    if yes_btn:
        ts   = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        rows = row_builder(county)
        for row in rows:
            row["timestamp"] = ts
        _write_rows(tab_name, columns, rows)
        st.session_state[done_key]   = True
        st.session_state[choice_key] = "yes"
        st.rerun()

    if no_btn:
        st.session_state[done_key]   = True
        st.session_state[choice_key] = "no"
        st.rerun()
