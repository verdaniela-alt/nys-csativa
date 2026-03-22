"""
1_Soil_Assessment.py — NY Cannabis/Hemp Soil Assessment Tool
Multi-page Streamlit app page.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd

from utils.nutrient_data import NUTRIENTS, AMENDMENTS, QUICK_AMEND, LAB_FACTORS
from utils.soil_api import get_soil_data

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Soil Assessment | NYS Cannabis Tool",
    page_icon="🌱",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.deficient  { background-color: #ffd6d6; color: #8b0000; font-weight: bold; padding: 2px 8px; border-radius: 4px; }
.adequate   { background-color: #d6f0d6; color: #006400; font-weight: bold; padding: 2px 8px; border-radius: 4px; }
.excess     { background-color: #fff3cd; color: #856404; font-weight: bold; padding: 2px 8px; border-radius: 4px; }
.nodata     { color: #888; font-style: italic; }
.soil-card  { background: #f0f7ff; border-left: 4px solid #1565C0; padding: 12px 16px; border-radius: 6px; margin-bottom: 12px; }
.amend-card { background: #fff8e1; border-left: 4px solid #e65100; padding: 10px 14px; border-radius: 6px; margin-bottom: 8px; }
</style>
""", unsafe_allow_html=True)

# ── Session state init ────────────────────────────────────────────────────────
if "soil_data" not in st.session_state:
    st.session_state.soil_data = None
if "assessment_done" not in st.session_state:
    st.session_state.assessment_done = False

# ─────────────────────────────────────────────────────────────────────────────
# PAGE HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.title("🌱 NY Cannabis & Hemp Soil Assessment")
st.caption("Outdoor & greenhouse cultivation — New York State | Data: USDA NRCS SSURGO + your lab report")

st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — SITE LOCATION
# ─────────────────────────────────────────────────────────────────────────────
with st.expander("📍 Step 1: Site Location & Soil Survey Lookup", expanded=True):
    st.markdown("Enter your farm address to automatically pull USDA NRCS soil data for your field.")

    col1, col2 = st.columns([3, 1])
    with col1:
        address_input = st.text_input(
            "Farm / Field Address",
            placeholder="e.g.  42 Example Farm Rd, Penn Yan, NY 14527",
            key="address_input",
        )
    with col2:
        st.write("")
        st.write("")
        lookup_btn = st.button("🔍 Look Up Soil Data", use_container_width=True)

    if lookup_btn and address_input.strip():
        with st.spinner("Geocoding address and querying NRCS Soil Data Access…"):
            try:
                soil = get_soil_data(address_input.strip())
                st.session_state.soil_data = soil
                st.success(f"✅ Matched: **{soil['matched_address']}**  "
                           f"| Coordinates: {soil['lat']:.5f}°N, {soil['lon']:.5f}°W")
            except ValueError as e:
                st.error(f"❌ Address not found: {e}")
            except Exception as e:
                st.error(f"❌ Lookup error: {e}")

    # Display results if available
    if st.session_state.soil_data:
        soil = st.session_state.soil_data
        comp    = soil.get("comp")
        horizon = soil.get("horizon")

        if comp or horizon:
            st.markdown("### 🗺️ NRCS Soil Survey Results")
            c1, c2 = st.columns(2)

            with c1:
                st.markdown("**Soil Component**")
                if comp:
                    st.markdown(f"""
<div class="soil-card">
<b>Map Unit:</b> {comp.get('map_unit', '—')}<br>
<b>Dominant Series:</b> {comp.get('series', '—')} ({comp.get('pct', '—')}% of map unit)<br>
<b>Taxonomy:</b> {comp.get('taxonomy', '—')}<br>
<b>Drainage Class:</b> {comp.get('drainage', '—')}<br>
<b>Hydrologic Group:</b> {comp.get('hydro_grp', '—')}<br>
<b>Representative Slope:</b> {comp.get('slope', '—')}%
</div>""", unsafe_allow_html=True)
                else:
                    st.warning("No component data — address may be outside SSURGO coverage.")
                    if soil.get("error_comp"):
                        st.caption(f"API error: {soil['error_comp']}")

            with c2:
                st.markdown("**Surface Horizon (0 cm)**")
                if horizon:
                    ph_str  = f"{horizon['ph']}" if horizon.get('ph') else "—"
                    cec_str = f"{horizon['cec']} meq/100g" if horizon.get('cec') else "—"
                    om_str  = f"{horizon['om']}%" if horizon.get('om') else "—"
                    depth   = f"{horizon.get('depth_top','?')}–{horizon.get('depth_bot','?')} cm"
                    st.markdown(f"""
<div class="soil-card">
<b>Horizon:</b> {horizon.get('horizon','—')} ({depth})<br>
<b>Texture Class:</b> {horizon.get('texture','—')}<br>
<b>pH (1:1 H₂O):</b> {ph_str}<br>
<b>CEC:</b> {cec_str}<br>
<b>Organic Matter:</b> {om_str}
</div>""", unsafe_allow_html=True)
                else:
                    st.warning("No horizon data returned.")
                    if soil.get("error_horizon"):
                        st.caption(f"API error: {soil['error_horizon']}")
        else:
            st.warning("⚠️ No NRCS data found for this location. You can still run the assessment manually below.")

    st.caption("Data from USDA NRCS SSURGO via Soil Data Access API. "
               "For interactive map, visit [SoilWeb](https://casoilresource.lawr.ucdavis.edu/gmap/).")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 — CROP & LAB SELECTION
# ─────────────────────────────────────────────────────────────────────────────
with st.expander("🌿 Step 2: Crop Type & Laboratory Method", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        crop = st.selectbox(
            "Crop Type",
            ["Hemp (fiber / grain / CBD)", "Cannabis (MJ, Adult-Use / Medical)"],
            key="crop_select",
        )
    with col2:
        lab = st.selectbox(
            "Soil Lab / Extraction Method",
            list(LAB_FACTORS.keys()),
            key="lab_select",
            help="Affects how P and K values are converted to Mehlich III equivalents before comparing to targets.",
        )

    crop_key = "hemp" if "Hemp" in crop else "mj"

    if "Modified Morgan" in lab:
        st.info("ℹ️ **Modified Morgan detected.** P values will be multiplied by 2.2 and K by 1.2 to approximate Mehlich III equivalents before comparison to targets.")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 3 — SOIL TEST INPUT
# ─────────────────────────────────────────────────────────────────────────────
with st.expander("🧪 Step 3: Enter Soil Test Results", expanded=True):
    st.markdown("Enter values from your lab report. Leave blank if not measured.")

    factors = LAB_FACTORS.get(lab, {})

    # Group nutrients for display
    groups = {
        "Basic Properties": ["pH", "Organic Matter"],
        "Macronutrients": ["P (Phosphorus)", "K (Potassium)", "Ca (Calcium)", "Mg (Magnesium)", "S (Sulfur)"],
        "Micronutrients": ["Zn (Zinc)", "Mn (Manganese)", "Fe (Iron)", "Cu (Copper)", "B (Boron)"],
        "Salts & Other": ["Na (Sodium)", "Al (Aluminum)", "CEC", "Base Saturation Ca%", "Base Saturation K%"],
    }

    user_values = {}
    for group_name, nutrient_names in groups.items():
        st.markdown(f"**{group_name}**")
        cols = st.columns(min(len(nutrient_names), 4))
        for i, nname in enumerate(nutrient_names):
            nutrient = next((n for n in NUTRIENTS if n["name"] == nname), None)
            if nutrient is None:
                continue
            col = cols[i % 4]
            with col:
                label = f"{nname}"
                if nname in factors:
                    label += f" *(MM raw)*"
                unit = nutrient["unit"]
                val = st.number_input(
                    f"{label} [{unit}]",
                    min_value=0.0,
                    max_value=50000.0,
                    value=None,
                    step=0.1,
                    format="%.2f",
                    key=f"nutrient_{nname}",
                    placeholder="—",
                )
                user_values[nname] = val
        st.write("")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 4 — RUN ASSESSMENT
# ─────────────────────────────────────────────────────────────────────────────
st.divider()
run_btn = st.button("▶ Run Gap Analysis", type="primary", use_container_width=True)

if run_btn:
    st.session_state.assessment_done = True

if st.session_state.assessment_done:
    st.markdown("## 📊 Gap Analysis Results")
    st.caption(f"Crop: **{crop}** | Lab: **{lab}**")

    factors = LAB_FACTORS.get(lab, {})

    # Build results table
    rows = []
    deficient_nutrients = []
    excess_nutrients    = []

    for n in NUTRIENTS:
        nname = n["name"]
        raw   = user_values.get(nname)

        if raw is None or raw == 0.0:
            # Check if it was actually entered as 0 vs left blank
            # We'll treat None as not entered
            rows.append({
                "Nutrient":       nname,
                "Unit":           n["unit"],
                "Raw Value":      "—",
                "Converted (M3)": "—",
                "Target Min":     n["hemp_min"] if crop_key == "hemp" else n["mj_min"],
                "Target Max":     n["hemp_max"] if crop_key == "hemp" else n["mj_max"],
                "Status":         "— No data",
                "Note":           n["note"],
            })
            continue

        factor  = factors.get(nname, 1.0)
        conv    = round(raw * factor, 2)
        t_min   = n["hemp_min"] if crop_key == "hemp" else n["mj_min"]
        t_max   = n["hemp_max"] if crop_key == "hemp" else n["mj_max"]

        if conv < t_min:
            status = "⚠ DEFICIENT"
            deficient_nutrients.append(nname)
        elif conv > t_max:
            status = "▲ EXCESS"
            excess_nutrients.append(nname)
        else:
            status = "✓ ADEQUATE"

        rows.append({
            "Nutrient":       nname,
            "Unit":           n["unit"],
            "Raw Value":      raw,
            "Converted (M3)": conv if factor != 1.0 else "—",
            "Target Min":     t_min,
            "Target Max":     t_max,
            "Status":         status,
            "Note":           n["note"],
        })

    df = pd.DataFrame(rows)

    # Color-code the Status column
    def style_status(val):
        if "DEFICIENT" in str(val):
            return "background-color: #ffd6d6; color: #8b0000; font-weight: bold"
        if "EXCESS" in str(val):
            return "background-color: #fff3cd; color: #856404; font-weight: bold"
        if "ADEQUATE" in str(val):
            return "background-color: #d6f0d6; color: #006400; font-weight: bold"
        return "color: #888; font-style: italic"

    styled = df.style.map(style_status, subset=["Status"])
    st.dataframe(styled, use_container_width=True, hide_index=True)

    # Download button
    csv = df.to_csv(index=False)
    st.download_button(
        "⬇ Download Results (CSV)",
        data=csv,
        file_name="soil_gap_analysis.csv",
        mime="text/csv",
    )

    # ── Amendment Recommendations ─────────────────────────────────────────
    st.divider()
    st.markdown("## 🌾 Amendment Recommendations")

    if not deficient_nutrients and not excess_nutrients:
        st.success("🎉 All entered nutrients are within target range — no amendments needed based on this data.")
    else:
        if deficient_nutrients:
            st.markdown(f"### ⚠ Deficiencies detected: {', '.join(deficient_nutrients)}")
            for nname in deficient_nutrients:
                # Short name (strip element symbol notes)
                short = nname.split(" ")[0]
                # Find matching amendments
                matching = [a for a in AMENDMENTS if
                            short.lower() in a["condition"].lower() or
                            nname.split("(")[0].strip().lower() in a["condition"].lower()]
                if not matching and nname in QUICK_AMEND:
                    quick = QUICK_AMEND[nname]
                    st.markdown(f"""
<div class="amend-card">
<b>{nname} — Deficient</b><br>
<b>Recommended:</b> {quick.get('low', '—')}<br>
</div>""", unsafe_allow_html=True)
                for a in matching:
                    st.markdown(f"""
<div class="amend-card">
<b>{a['condition']}</b><br>
<b>Amendment:</b> {a['amendment']}<br>
<b>Rate:</b> {a['rate']}<br>
<i>{a['notes']}</i>
</div>""", unsafe_allow_html=True)

        if excess_nutrients:
            st.markdown(f"### ▲ Excess levels detected: {', '.join(excess_nutrients)}")
            for nname in excess_nutrients:
                if nname in QUICK_AMEND:
                    quick = QUICK_AMEND[nname]
                    st.markdown(f"""
<div class="amend-card" style="border-left-color:#e67e22;">
<b>{nname} — Excess</b><br>
<b>Action:</b> {quick.get('high', 'Reduce inputs; re-test in 60–90 days')}<br>
</div>""", unsafe_allow_html=True)

    # ── Soil health context ───────────────────────────────────────────────
    with st.expander("💡 Soil Health Context & General Guidelines"):
        st.markdown("""
**pH** is the most important lever — it controls the availability of nearly every nutrient.
Target **6.2–6.8** for cannabis and hemp. At pH < 6.0 Al and Mn become toxic;
at pH > 7.2 Fe, Zn, Mn, and B become unavailable.

**Organic matter** feeds the soil microbiome, buffers nutrients, and improves water-holding.
A minimum of 3% OM is recommended; 5–8% is ideal for outdoor cultivation in NY.

**Ca:Mg ratio** should be approximately 5:1 to 8:1 by weight (ppm).
High Mg relative to Ca can cause soil compaction in silty loam soils common in NY.

**K:Mg ratio** should stay < 3:1.
High K suppresses Mg uptake and is a common cause of Mg deficiency in NY cannabis fields.

**Micronutrients** (Zn, Mn, Fe, Cu, B) are primarily affected by pH.
Foliar applications are the fastest correction for in-season deficiencies.

For questions about NY-specific hemp or cannabis licensing and agronomy support,
contact your local Cornell Cooperative Extension office.
""")

    st.divider()
    st.caption("⚠️ This tool provides agronomic guidance based on general cannabis/hemp literature and "
               "NY State extension frameworks. Always consult a certified crop advisor (CCA) or licensed "
               "agronomist before making large-scale amendment applications. Targets are for Mehlich III "
               "(or converted equivalent) extractions at the surface horizon (0–20 cm / 0–8 in).")
