"""
app.py — Landing page for nys-csativa.streamlit.app
NY Cannabis & Hemp Grower Tools — multi-page Streamlit application.
"""

import streamlit as st

st.set_page_config(
    page_title="NYS Cannabis & Hemp Grower Tools",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.hero {
    background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 50%, #4a235a 100%);
    color: white;
    padding: 40px 32px;
    border-radius: 12px;
    margin-bottom: 24px;
}
.hero h1 { font-size: 2.4rem; margin-bottom: 8px; }
.hero p  { font-size: 1.1rem; opacity: 0.9; }
.tool-card {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 10px;
    padding: 24px;
    height: 100%;
}
.tool-card h3 { margin-top: 0; }
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: bold;
    margin-left: 8px;
}
.badge-live { background: #d4edda; color: #155724; }
.badge-soon { background: #fff3cd; color: #856404; }
.disclaimer-banner {
    background: #fff8e1;
    border: 2px solid #f9a825;
    border-left: 6px solid #e65100;
    border-radius: 8px;
    padding: 20px 24px;
    margin-bottom: 24px;
    font-size: 0.92rem;
    line-height: 1.6;
}
.disclaimer-banner h4 {
    color: #b71c1c;
    margin: 0 0 10px 0;
    font-size: 1.05rem;
}
.disclaimer-banner b { color: #e65100; }
</style>
""", unsafe_allow_html=True)

# ── Disclaimer & Data Sources ─────────────────────────────────────────────────
st.markdown("""
<div class="disclaimer-banner">
<h4>⚠️ Important Disclaimer & Data Sources — Please Read Before Using These Tools</h4>
<b>These tools are for educational and planning purposes only.</b> They do not constitute
professional agronomic, financial, or legal advice. Results should be interpreted by a
qualified professional before any action is taken. <b>The developers assume no responsibility
or liability</b> for any decisions, crop losses, financial outcomes, or regulatory consequences
arising from use of these tools.<br><br>
Always consult a <b>certified crop advisor (CCA)</b>, licensed agronomist, or your local
<b>Cornell Cooperative Extension</b> office before making large-scale amendment applications.
Compliance with all applicable <b>NY State Cannabis Control Board (OCM)</b> regulations is
the sole responsibility of the grower.<br><br>
<b>Soil data:</b> USDA NRCS SSURGO via
<a href="https://SDMDataAccess.nrcs.usda.gov" target="_blank">Soil Data Access REST API</a> ·
Address geocoding by <a href="https://geocoding.geo.census.gov" target="_blank">US Census Geocoder</a> ·
<b>Nutrient targets:</b> NY State extension frameworks, peer-reviewed cannabis agronomy literature,
and CCA guidance for northeastern US production (Mehlich III equivalents) ·
<b>Amendment rates:</b> representative ranges only — determine actual rates with a CCA.
</div>
""", unsafe_allow_html=True)

# ── Hero banner ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>🌿 NYS Cannabis & Hemp Grower Tools</h1>
  <p>Free, science-based tools for licensed New York State cannabis and hemp cultivators.<br>
  Built on USDA NRCS soil data and NY State extension agronomic frameworks.</p>
</div>
""", unsafe_allow_html=True)

# ── Tool cards ────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("""
<div class="tool-card">
  <h3>🌱 Soil Assessment Tool <span class="badge badge-live">LIVE</span></h3>
  <p>Enter your farm address and soil test results to get a complete fertility gap analysis
  and amendment recommendations tailored for hemp or cannabis production.</p>
  <ul>
    <li>Auto-fills soil series, texture, drainage from USDA NRCS</li>
    <li>Supports Mehlich III and Modified Morgan labs</li>
    <li>Separate hemp and cannabis (MJ) targets</li>
    <li>Specific amendment rates for NY conditions</li>
    <li>Downloadable CSV report</li>
  </ul>
</div>
""", unsafe_allow_html=True)
    st.write("")
    if st.button("→ Open Soil Assessment Tool", use_container_width=True, type="primary"):
        st.switch_page("pages/1_Soil_Assessment.py")

with col2:
    st.markdown("""
<div class="tool-card">
  <h3>💰 Economics Tool <span class="badge badge-live">LIVE</span></h3>
  <p>Enterprise budgets and profitability analysis for NY cannabis and hemp operations.</p>
  <ul>
    <li>Break-even yield and price calculator</li>
    <li>Input cost estimator (seeds, amendments, labor, licensing)</li>
    <li>NY wholesale price benchmarks</li>
    <li>Scenario comparison: outdoor, greenhouse, indoor</li>
    <li>Export to Excel</li>
  </ul>
</div>
""", unsafe_allow_html=True)
    st.write("")
    if st.button("→ Open Economics Tool", use_container_width=True, type="primary"):
        st.switch_page("pages/2_Economics.py")

st.write("")
col3, col4, col5 = st.columns(3, gap="large")

with col3:
    st.markdown("""
<div class="tool-card">
  <h3>🌱 Pre-Harvest Data <span class="badge badge-live">LIVE</span></h3>
  <p>Record batch identity, growing environment, inputs, pest control, and sales data throughout
  the growing cycle.</p>
  <ul>
    <li>Upload existing PreHarvest Excel template</li>
    <li>Manual entry across 7 data sections</li>
    <li>Nutrient &amp; pest control event logs</li>
    <li>Cannabinoid &amp; terpene results</li>
    <li>Download as CSV or Excel</li>
  </ul>
</div>
""", unsafe_allow_html=True)
    st.write("")
    if st.button("→ Open Pre-Harvest Tool", use_container_width=True, type="primary"):
        st.switch_page("pages/3_Pre_Harvest.py")

with col4:
    st.markdown("""
<div class="tool-card">
  <h3>🌾 Post-Harvest Data <span class="badge badge-live">LIVE</span></h3>
  <p>Track processing weights, curing, COA lab testing, packaging inventory, and byproduct sales
  from cut to sale.</p>
  <ul>
    <li>Upload existing PostHarvest Excel template</li>
    <li>Weight flow: wet → bucked → dried → trimmed</li>
    <li>Curing monitoring log</li>
    <li>COA pass/fail tracking</li>
    <li>Download as CSV or Excel</li>
  </ul>
</div>
""", unsafe_allow_html=True)
    st.write("")
    if st.button("→ Open Post-Harvest Tool", use_container_width=True, type="primary"):
        st.switch_page("pages/4_Post_Harvest.py")

with col5:
    st.markdown("""
<div class="tool-card">
  <h3>📊 Batch Overview <span class="badge badge-live">LIVE</span></h3>
  <p>Linked dashboard that combines pre- and post-harvest records by Batch ID for a complete
  per-batch picture.</p>
  <ul>
    <li>Data completeness indicators</li>
    <li>Weight flow funnel chart</li>
    <li>Revenue breakdown by product stream</li>
    <li>Cannabinoid &amp; terpene summary</li>
    <li>Download combined batch report</li>
  </ul>
</div>
""", unsafe_allow_html=True)
    st.write("")
    if st.button("→ Open Batch Overview", use_container_width=True, type="primary"):
        st.switch_page("pages/5_Batch_Overview.py")

st.caption("Built for NYS licensed cultivators · Data: USDA NRCS + US Census Geocoder · "
           "Targets: NY State Extension / CCE agronomic frameworks")
