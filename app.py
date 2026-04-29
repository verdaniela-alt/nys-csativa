"""
app.py — Landing page for nys-csativa.streamlit.app
NY Cannabis & Hemp Grower Tools — multi-page Streamlit application.
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from utils.sidebar import render_sidebar

st.set_page_config(
    page_title="NYS Cannabis & Hemp Grower Tools",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)
render_sidebar(require_disclaimer=False)

# Hide sidebar entirely on homepage
st.markdown("""
<style>
[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

_accepted = st.session_state.get("disclaimer_accepted", False)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Header ── */
.site-header {
    background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 50%, #4a235a 100%);
    color: white;
    padding: 28px 32px 20px 32px;
    border-radius: 12px;
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.site-header h1 { font-size: 2rem; margin: 0 0 4px 0; }
.site-header p  { font-size: 1rem; margin: 0; opacity: 0.88; }
.newsletter-box {
    background: rgba(255,255,255,0.15);
    border: 2px solid rgba(255,255,255,0.4);
    border-radius: 10px;
    padding: 12px 18px;
    text-align: center;
    min-width: 200px;
    color: white;
    font-size: 0.9rem;
}
.newsletter-box .nl-icon { font-size: 1.8rem; display: block; margin-bottom: 4px; }
.newsletter-box .nl-label { font-weight: bold; display: block; }
.newsletter-box .nl-sub { font-size: 0.78rem; opacity: 0.8; }

/* ── Tool cards ── */
.tool-card {
    background: #ffffff;
    border: 1.5px solid #dee2e6;
    border-radius: 12px;
    overflow: hidden;
    height: 100%;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    transition: box-shadow 0.2s;
}
.tool-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.13); }
.card-preview {
    width: 100%;
    height: 160px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 4rem;
}
.card-body { padding: 16px 18px 12px 18px; }
.card-body h3 { margin: 0 0 10px 0; font-size: 1.05rem; color: #1b5e20; }
.card-body ul { margin: 0; padding-left: 18px; font-size: 0.88rem;
                color: #444; line-height: 1.7; }

/* ── Disclaimer ── */
.disclaimer-box {
    background: #fff8e1;
    border: 2px solid #f9a825;
    border-left: 6px solid #e65100;
    border-radius: 10px;
    padding: 20px 24px;
    font-size: 0.88rem;
    line-height: 1.6;
}
.disclaimer-box h4 { color: #b71c1c; margin: 0 0 8px 0; font-size: 1rem; }
</style>
""", unsafe_allow_html=True)

# ── Header + Newsletter placeholder ──────────────────────────────────────────
hcol1, hcol2 = st.columns([3, 1], gap="large")
with hcol1:
    st.markdown("""
<div class="site-header">
  <div>
    <h1>🌿 NYS Cannabis & Hemp Grower Tools</h1>
    <p>Free, science-based tools for licensed New York State adult-use cannabis and hemp cultivators.<br>
    Built on USDA NRCS soil data and NY State extension agronomic frameworks.</p>
  </div>
</div>
""", unsafe_allow_html=True)
with hcol2:
    st.markdown("""
<div style="height:12px"></div>
<div class="newsletter-box">
  <span class="nl-icon">✉️</span>
  <span class="nl-label">Sign Up for Newsletter</span>
  <span class="nl-sub">Coming soon</span>
</div>
""", unsafe_allow_html=True)

st.write("")

# ── Tool grid — Row 1 ─────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3, gap="large")

with c1:
    st.markdown("""
<div class="tool-card">
  <div class="card-preview" style="background:#e8f5e9;">🗺️</div>
  <div class="card-body">
    <h3>🌱 Soil Assessment Tool</h3>
    <ul>
      <li>Auto-fills USDA NRCS soil data from your farm address</li>
      <li>Fertility gap analysis with amendment recommendations</li>
      <li>Supports hemp &amp; adult-use cannabis targets — downloadable report</li>
    </ul>
  </div>
</div>
""", unsafe_allow_html=True)
    st.write("")
    if st.button("→ Soil Assessment", use_container_width=True, type="primary",
                 disabled=not _accepted, key="btn_soil"):
        st.switch_page("pages/1_Soil_Assessment.py")

with c2:
    st.markdown("""
<div class="tool-card">
  <div class="card-preview" style="background:#e3f2fd;">📊</div>
  <div class="card-body">
    <h3>💰 Economics Tool</h3>
    <ul>
      <li>Enterprise budgets for adult-use cannabis &amp; 5 hemp production models</li>
      <li>Break-even yield, price &amp; profitability analysis</li>
      <li>NY wholesale price benchmarks — export to Excel</li>
    </ul>
  </div>
</div>
""", unsafe_allow_html=True)
    st.write("")
    if st.button("→ Economics Tool", use_container_width=True, type="primary",
                 disabled=not _accepted, key="btn_econ"):
        st.switch_page("pages/2_Economics.py")

with c3:
    st.markdown("""
<div class="tool-card">
  <div class="card-preview" style="background:#e8f5e9;">
    <svg xmlns="http://www.w3.org/2000/svg" width="90" height="90" viewBox="0 0 100 100">
      <!-- Cannabis leaf cartoon -->
      <g fill="#2e7d32" opacity="0.85">
        <!-- center stem -->
        <rect x="48" y="45" width="4" height="38" rx="2"/>
        <!-- main center leaf -->
        <ellipse cx="50" cy="30" rx="10" ry="22" transform="rotate(0 50 50)"/>
        <!-- left leaves -->
        <ellipse cx="50" cy="38" rx="9" ry="20" transform="rotate(-35 50 50)"/>
        <ellipse cx="50" cy="38" rx="7" ry="17" transform="rotate(-65 50 50)"/>
        <ellipse cx="50" cy="38" rx="5" ry="13" transform="rotate(-90 50 50)"/>
        <!-- right leaves -->
        <ellipse cx="50" cy="38" rx="9" ry="20" transform="rotate(35 50 50)"/>
        <ellipse cx="50" cy="38" rx="7" ry="17" transform="rotate(65 50 50)"/>
        <ellipse cx="50" cy="38" rx="5" ry="13" transform="rotate(90 50 50)"/>
      </g>
      <!-- highlight -->
      <g fill="#a5d6a7" opacity="0.4">
        <ellipse cx="50" cy="28" rx="4" ry="12"/>
      </g>
    </svg>
  </div>
  <div class="card-body">
    <h3>🌿 Crop Overview</h3>
    <ul>
      <li>Pre-harvest &amp; post-harvest records linked by Batch ID</li>
      <li>Weight flow funnel, COA results, revenue breakdown</li>
      <li>Export to CSV or Excel — links to Economics Tool</li>
    </ul>
  </div>
</div>
""", unsafe_allow_html=True)
    st.write("")
    if st.button("→ Crop Overview", use_container_width=True, type="primary",
                 disabled=not _accepted, key="btn_crop"):
        st.switch_page("pages/3_Crop_Overview.py")

st.write("")

# ── Tool grid — Row 2 ─────────────────────────────────────────────────────────
c4, c5, c6 = st.columns(3, gap="large")

with c4:
    st.markdown("""
<div class="tool-card">
  <div class="card-preview" style="background:#f3e5f5;">📋</div>
  <div class="card-body">
    <h3>📋 CIP Form Builder</h3>
    <ul>
      <li>Guided form for all 7 NYS OCM CIP sections</li>
      <li>Pre-filled narrative paragraphs from your answers</li>
      <li>Download as submission-ready Word (.docx)</li>
    </ul>
  </div>
</div>
""", unsafe_allow_html=True)
    st.write("")
    if st.button("→ CIP Form Builder", use_container_width=True, type="primary",
                 disabled=not _accepted, key="btn_cip"):
        st.switch_page("pages/6_CIP_Form.py")

with c5:
    st.markdown("""
<div class="tool-card">
  <div class="card-preview" style="background:#fff3e0;">📂</div>
  <div class="card-body">
    <h3>📂 SOP Library</h3>
    <ul>
      <li>164 Standard Operating Procedure templates</li>
      <li>Cultivation, Processing, Retail &amp; General categories</li>
      <li>Customisable Word (.docx) — white-label format</li>
    </ul>
  </div>
</div>
""", unsafe_allow_html=True)
    st.write("")
    if st.button("→ SOP Library", use_container_width=True, type="primary",
                 disabled=not _accepted, key="btn_sop"):
        st.switch_page("pages/7_Resources.py")

with c6:
    st.markdown("""
<div class="tool-card">
  <div class="card-preview" style="background:#fce4ec;">💬</div>
  <div class="card-body">
    <h3>💬 Feedback</h3>
    <ul>
      <li>Help us improve — share your experience</li>
      <li>Optional demographics &amp; NYS county</li>
      <li>Anonymous — no personal data collected</li>
    </ul>
  </div>
</div>
""", unsafe_allow_html=True)
    st.write("")
    if st.button("→ Share Feedback", use_container_width=True, type="primary",
                 disabled=not _accepted, key="btn_feedback"):
        st.switch_page("pages/8_Feedback.py")

st.write("")
st.divider()

# ── Disclaimer at bottom ──────────────────────────────────────────────────────
st.markdown("""
<div class="disclaimer-box">
<h4>⚠️ Disclaimer & Data Sources — Please Read Before Using These Tools</h4>
These tools are for <b>educational and planning purposes only</b>. They do not constitute
professional agronomic, financial, or legal advice. <b>The developers assume no responsibility
or liability</b> for any decisions, crop losses, financial outcomes, or regulatory consequences
arising from use of these tools. Always consult a <b>certified crop advisor (CCA)</b> or your
local <b>Cornell Cooperative Extension</b> office before making large-scale decisions.
Compliance with all applicable <b>NYS OCM</b> regulations is the sole responsibility of the user.<br><br>
<b>Soil data:</b> USDA NRCS SSURGO ·
<b>Geocoding:</b> US Census Geocoder ·
<b>Lab conversions:</b> Cornell NMSP Conversion Tools (v7) ·
<b>Lime rates:</b> Cornell NMSP Lime Calculator v2.0 (2014) ·
<b>Hemp economics:</b> Bader (U. Kentucky, 2021) ·
<b>Cannabis economics:</b> Ruterbories, Hanchar &amp; Vergara (2025) · NYS OCM market reports · Cannabis Benchmarks (2024–25).
</div>
""", unsafe_allow_html=True)

st.write("")
disc_col, feed_col = st.columns([3, 1])
with disc_col:
    agreed = st.checkbox(
        "✅ I have read the disclaimer and understand that the developers are not liable "
        "for any information or data provided by these tools.",
        value=_accepted,
        key="disclaimer_checkbox_home",
    )
    if agreed and not _accepted:
        st.session_state["disclaimer_accepted"] = True
        st.rerun()
    if not _accepted:
        st.caption("⬆️ You must check the box above to unlock the tools.")
    else:
        st.caption("Tools unlocked. You can now access all tools above.")

with feed_col:
    st.write("")
    if st.button("💬 Share Feedback", use_container_width=True, key="btn_feedback_bottom"):
        st.switch_page("pages/8_Feedback.py")

st.write("")
st.caption(
    "Built for NYS licensed cultivators · "
    "Data: USDA NRCS + US Census Geocoder · "
    "Targets: NY State Extension / CCE agronomic frameworks"
)
