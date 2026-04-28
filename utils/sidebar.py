"""
utils/sidebar.py — Custom sidebar navigation for all NYS Cannabis Tool pages.
Call render_sidebar() near the top of every page, after set_page_config().
"""
import streamlit as st

# Hides the auto-generated Streamlit page list so our custom nav is the only one shown
_HIDE_AUTO_NAV_CSS = """
<style>
section[data-testid="stSidebarNav"] { display: none !important; }
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

        st.caption(
            "Built for NYS licensed cultivators\n"
            "Data: USDA NRCS · US Census Geocoder\n"
            "Targets: NY State Extension / CCE frameworks"
        )
