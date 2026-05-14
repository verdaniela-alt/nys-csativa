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

# Per-tool anonymity descriptions shown to the user.
# Each entry is (what_we_collect, what_we_do_not_collect).
_TOOL_PRIVACY = {
    "soil": (
        "Soil nutrient levels, pH, organic matter, crop type, soil lab used, "
        "and — only if you choose to share it — your county.",
        "Your farm address, field coordinates, name, license number, or any "
        "information that could identify you or your operation.",
    ),
    "econ": (
        "Operation type, crop type, acreage, estimated yield, and summarized "
        "cost and revenue totals (labor, variable costs, fixed costs, gross margin, "
        "breakeven figures). No line-item costs.",
        "Your farm name, address, license number, specific vendor costs, "
        "or any contact information. No location data is collected for this tool.",
    ),
    "crop": (
        "Strain name, growing method, plant counts, cultivated area, yield weights, "
        "cannabinoid percentages (THC/CBD), soil inputs used, and disease presence.",
        "Your batch ID, farm name, address, license number, Certificate of Analysis "
        "details beyond pass/fail, or any identifier that could trace back to you.",
    ),
    "cip": (
        "County, OCM region, license type, budget period, number of community goals "
        "selected, and reporting frequency.",
        "Your applicant name, business name, address, phone number, email, "
        "or any specific financial or narrative content from your CIP application.",
    ),
}


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
    what_collect, what_not = _TOOL_PRIVACY.get(
        tool_key,
        ("Agronomic and financial summary data only.", "Any personally identifying information."),
    )

    st.divider()
    st.markdown("### 🔒 Would you like to share your results with us?")
    st.markdown(
        "Sharing is **entirely voluntary**. If you choose to share, your data helps us "
        "understand the NYS *Cannabis sativa* industry better and improve these free tools "
        "for all growers. We are committed to keeping your information anonymous — "
        "**we cannot identify you, your farm, or your operation from what is collected.**"
    )

    col_yes_info, col_no_info = st.columns(2)
    with col_yes_info:
        st.success(
            f"**✅ If you share — what we collect:**\n\n{what_collect}",
        )
    with col_no_info:
        st.error(
            f"**🚫 What we will NEVER collect:**\n\n{what_not}",
        )

    st.caption(
        "Selecting **No** sends absolutely nothing. Your data stays only on your device "
        "and is never transmitted anywhere. There is no tracking of any kind."
    )

    done_key   = f"_share_{tool_key}_done"
    choice_key = f"_share_{tool_key}_choice"
    county_key = f"_share_{tool_key}_county"

    if st.session_state.get(done_key):
        if st.session_state.get(choice_key) == "yes":
            st.success(
                "Thank you! Your anonymized data has been shared with us and will help "
                "improve these tools for NYS growers.",
                icon="✅",
            )
        else:
            st.info("No problem — your data was not shared and nothing was transmitted.", icon="👍")
        return

    county = ""
    if county_widget:
        sel = st.selectbox(
            "Your county *(optional — helps us understand regional patterns across NYS)*",
            NYS_COUNTIES,
            key=county_key,
        )
        county = "" if sel.startswith("—") else sel

    col1, col2, _ = st.columns([1, 1, 4])
    with col1:
        yes_btn = st.button(
            "Yes, share anonymously",
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
