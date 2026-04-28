"""
utils/sidebar.py — Custom sidebar navigation for all NYS Cannabis Tool pages.
Call render_sidebar() near the top of every page, after set_page_config().
"""
import streamlit as st


def _show_disclaimer_gate():
    """Full-page disclaimer that blocks all pages until the user acknowledges."""
    st.markdown("""
<div style="max-width:720px;margin:60px auto;padding:40px;
            background:#fff8e1;border:2px solid #f9a825;
            border-left:8px solid #e65100;border-radius:12px;
            font-size:0.95rem;line-height:1.7;">
<h2 style="color:#b71c1c;margin-top:0;">⚠️ Important Disclaimer — Please Read Before Continuing</h2>
<p>
These tools are provided <b>for educational and planning purposes only</b>.
They do not constitute professional agronomic, financial, legal, or regulatory advice.
All results should be interpreted by a qualified professional before any action is taken.
</p>
<p>
<b>The developers, Cornell University, and any affiliated parties assume no responsibility
or liability</b> for any decisions, crop losses, financial outcomes, or regulatory
consequences arising from the use of these tools.
</p>
<p>
Always consult a <b>certified crop advisor (CCA)</b>, licensed agronomist, or your local
<b>Cornell Cooperative Extension</b> office before making large-scale amendment applications.
Compliance with all applicable <b>NYS OCM</b> regulations is the sole responsibility of the user.
</p>
<p style="margin-bottom:0;">
<b>Soil data:</b> USDA NRCS SSURGO · <b>Geocoding:</b> US Census Geocoder ·
<b>Nutrient targets:</b> NY State extension / CCE agronomic frameworks ·
<b>Economics:</b> Bader (U. Kentucky, 2021); Ruterbories, Hanchar &amp; Vergara (2025);
NYS OCM market reports; Cannabis Benchmarks (2024–25).
</p>
</div>
""", unsafe_allow_html=True)

    col_left, col_mid, col_right = st.columns([1, 2, 1])
    with col_mid:
        agreed = st.checkbox(
            "I understand that the developers are not liable for any of the information or data "
            "provided by these tools, and that I will use them for educational/planning purposes only."
        )
        st.button(
            "Continue →",
            type="primary",
            disabled=not agreed,
            on_click=lambda: st.session_state.update({"disclaimer_accepted": True}),
            use_container_width=True,
        )

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

    if not st.session_state.get("disclaimer_accepted", False):
        _show_disclaimer_gate()
        st.stop()

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
