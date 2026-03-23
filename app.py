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
</style>
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

# ── How it works ──────────────────────────────────────────────────────────────
st.divider()
st.markdown("## How the Soil Assessment Tool Works")

steps = st.columns(4)
step_data = [
    ("1️⃣", "Enter Address", "Type your farm or field address. The tool geocodes it and queries the USDA NRCS SSURGO database for your soil series, texture, drainage class, and baseline pH."),
    ("2️⃣", "Select Crop & Lab", "Choose Hemp or Cannabis (MJ) and select your soil laboratory. Modified Morgan values are automatically converted to Mehlich III equivalents."),
    ("3️⃣", "Enter Lab Results", "Type in values from your soil test report — pH, OM, macro- and micronutrients. Leave fields blank if not measured."),
    ("4️⃣", "Get Recommendations", "Instant color-coded gap analysis (Deficient / Adequate / Excess) plus specific amendment products, rates, and timing for NY conditions."),
]
for col, (icon, title, desc) in zip(steps, step_data):
    with col:
        st.markdown(f"**{icon} {title}**")
        st.caption(desc)

# ── Data sources & disclaimer ─────────────────────────────────────────────────
st.divider()
with st.expander("📚 Data Sources & Disclaimer"):
    st.markdown("""
**Soil data sources:**
- USDA NRCS SSURGO (Soil Survey Geographic Database) via [Soil Data Access REST API](https://SDMDataAccess.nrcs.usda.gov)
- Spatial lookup by [SDA_Get_Mukey_from_intersection_with_WktWgs84](https://sdmdataaccess.nrcs.usda.gov/QueryFunctions.aspx) — same data used by [SoilWeb](https://casoilresource.lawr.ucdavis.edu/gmap/)
- Address geocoding by [US Census Geocoder](https://geocoding.geo.census.gov)

**Nutrient targets:**
Derived from NY State extension frameworks, peer-reviewed cannabis agronomy literature,
and licensed crop advisor (CCA) guidance for northeastern US hemp/cannabis production.
Targets are expressed as Mehlich III equivalents.

**Amendment recommendations:**
Based on general agronomic principles and NY State soil management guidelines.
Rates are representative ranges — actual application rates should be determined
with a certified crop advisor based on field-specific conditions.

**Disclaimer:**
This tool is for educational and planning purposes only. It does not constitute
professional agronomic advice. Always consult a certified crop advisor (CCA),
licensed agronomist, or your local Cornell Cooperative Extension office before
making large-scale amendment applications. Compliance with all applicable
New York State Cannabis Control Board regulations is the grower's responsibility.
""")

st.caption("Built for NYS licensed cultivators · Data: USDA NRCS + US Census Geocoder · "
           "Targets: NY State Extension / CCE agronomic frameworks")
