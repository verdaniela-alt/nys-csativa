"""
utils/sidebar.py — Custom sidebar navigation for all NYS Cannabis Tool pages.
Call render_sidebar() near the top of every page, after set_page_config().
"""
import streamlit as st

# Hides the auto-generated Streamlit page list so our custom nav is the only one shown.
# Multiple selectors cover different Streamlit versions (1.32 – 1.44+).
_HIDE_AUTO_NAV_CSS = """
<style>
/* Streamlit <= 1.35 */
section[data-testid="stSidebarNav"]          { display: none !important; }
/* Streamlit 1.36 – 1.40 */
div[data-testid="stSidebarNavContainer"]     { display: none !important; }
[data-testid="stSidebarNav"]                 { display: none !important; }
/* Streamlit 1.41+ */
ul[data-testid="stSidebarNavItems"]          { display: none !important; }
nav[data-testid="stSidebarNav"]              { display: none !important; }
/* Catch-all: hide the entire collapsible nav block at the top of the sidebar */
[data-testid="stSidebarNavSeparator"]        { display: none !important; }
</style>
"""


def render_sidebar():
    """Inject custom branded navigation into st.sidebar."""
    st.markdown(_HIDE_AUTO_NAV_CSS, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### 🌿 NYS Grower Tools")
        st.page_link("app.py", label="🏠 Home")

        st.divider()

        st.page_link("pages/1_Soil_Assessment.py", label="🌱 Soil Assessment")

        st.divider()

        st.page_link("pages/2_Economics.py", label="💰 Economics")

        st.divider()

        st.page_link("pages/3_Crop_Overview.py", label="🌿 Crop Overview")
        st.markdown(
            "<div style='font-size:0.82rem; padding-left:20px; color:#888; "
            "margin-top:-4px; line-height:2.0;'>"
            "↳ Pre-Harvest<br>"
            "↳ Post-Harvest<br>"
            "↳ Batch Dashboard"
            "</div>",
            unsafe_allow_html=True,
        )

        st.divider()

        st.page_link("pages/6_CIP_Form.py", label="📋 CIP Form Builder")

        st.divider()

        st.page_link("pages/7_Resources.py", label="📂 SOP Library")

        st.divider()

        st.page_link("pages/8_Feedback.py", label="💬 Feedback")

        st.divider()

        st.caption(
            "Built for NYS licensed cultivators\n"
            "Data: USDA NRCS · US Census Geocoder\n"
            "Targets: NY State Extension / CCE frameworks"
        )
