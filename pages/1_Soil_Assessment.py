"""
1_Soil_Assessment.py — NY Cannabis/Hemp Soil Assessment Tool
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd

from utils.nutrient_data import (
    NUTRIENTS, AMENDMENTS, QUICK_AMEND, LAB_FACTORS, UNIT_CONVERSIONS
)
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
.disclaimer-box {
    background: #fff3cd;
    border: 2px solid #e0a800;
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 20px;
    font-size: 0.92rem;
}
.disclaimer-box b { color: #856404; }
.deficient  { background-color: #ffd6d6; color: #8b0000; font-weight: bold; padding: 2px 8px; border-radius: 4px; }
.adequate   { background-color: #d6f0d6; color: #006400; font-weight: bold; padding: 2px 8px; border-radius: 4px; }
.excess     { background-color: #fff3cd; color: #856404; font-weight: bold; padding: 2px 8px; border-radius: 4px; }
.soil-card  { background: #f0f7ff; border-left: 4px solid #1565C0; padding: 12px 16px; border-radius: 6px; margin-bottom: 12px; }
.amend-card { background: #fafafa; border: 1px solid #ddd; border-radius: 8px; padding: 14px 16px; margin-bottom: 10px; }
.amend-card h4 { margin: 0 0 6px 0; }
.tag { display: inline-block; padding: 2px 9px; border-radius: 10px; font-size: 0.78rem; font-weight: bold; margin-right: 4px; }
.tag-organic    { background: #d4edda; color: #155724; }
.tag-synthetic  { background: #e2e3e5; color: #383d41; }
.tag-powder     { background: #cfe2ff; color: #084298; }
.tag-liquid     { background: #d1ecf1; color: #0c5460; }
.tag-granular   { background: #fff3cd; color: #856404; }
.tag-pellet     { background: #f8d7da; color: #721c24; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "soil_data"       not in st.session_state: st.session_state.soil_data       = None
if "assessment_done" not in st.session_state: st.session_state.assessment_done = False

# ─────────────────────────────────────────────────────────────────────────────
# DISCLAIMER — TOP OF PAGE
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="disclaimer-box">
<b>⚠️ Important Disclaimer — Please Read Before Using This Tool</b><br><br>
This tool provides <b>general agronomic guidance only</b>, based on cannabis and hemp
soil fertility literature and NY State extension frameworks.
<b>The suggestions presented here are possible options, not prescriptions.</b>
Results should be interpreted by a qualified professional before any action is taken.<br><br>
<b>This tool and its developers assume no responsibility or liability</b> for any
decisions, actions, crop losses, financial outcomes, or regulatory consequences
arising from the use of this tool. Targets and recommendations are based on
Mehlich III (or converted equivalent) extractions at the surface horizon (0–20 cm / 0–8 in)
and may not reflect the full complexity of your specific field conditions.<br><br>
Always consult a <b>certified crop advisor (CCA)</b>, licensed agronomist, or your local
Cornell Cooperative Extension office before making large-scale amendment applications.
Compliance with all applicable <b>NY State Cannabis Control Board</b> regulations is
the sole responsibility of the grower.
</div>
""", unsafe_allow_html=True)

# ── Page header ───────────────────────────────────────────────────────────────
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

    if st.session_state.soil_data:
        soil    = st.session_state.soil_data
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
<b>Map Unit:</b> {comp.get('map_unit','—')}<br>
<b>Dominant Series:</b> {comp.get('series','—')} ({comp.get('pct','—')}% of map unit)<br>
<b>Taxonomy:</b> {comp.get('taxonomy','—')}<br>
<b>Drainage Class:</b> {comp.get('drainage','—')}<br>
<b>Hydrologic Group:</b> {comp.get('hydro_grp','—')}<br>
<b>Representative Slope:</b> {comp.get('slope','—')}%
</div>""", unsafe_allow_html=True)
                else:
                    st.warning("No component data — address may be outside SSURGO coverage.")
            with c2:
                st.markdown("**Surface Horizon (0 cm)**")
                if horizon:
                    st.markdown(f"""
<div class="soil-card">
<b>Horizon:</b> {horizon.get('horizon','—')} ({horizon.get('depth_top','?')}–{horizon.get('depth_bot','?')} cm)<br>
<b>Texture Class:</b> {horizon.get('texture','—')}<br>
<b>pH (1:1 H₂O):</b> {horizon.get('ph','—') or '—'}<br>
<b>CEC:</b> {f"{horizon['cec']} meq/100g" if horizon.get('cec') else '—'}<br>
<b>Organic Matter:</b> {f"{horizon['om']}%" if horizon.get('om') else '—'}
</div>""", unsafe_allow_html=True)
                else:
                    st.warning("No horizon data returned.")
        else:
            st.warning("⚠️ No NRCS data found. You can still enter data manually below.")

    st.caption("Data from USDA NRCS SSURGO. For an interactive map visit "
               "[SoilWeb](https://casoilresource.lawr.ucdavis.edu/gmap/).")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 — CROP & LAB SELECTION
# ─────────────────────────────────────────────────────────────────────────────
with st.expander("🌿 Step 2: Crop Type & Laboratory", expanded=True):
    col1, col2 = st.columns(2)

    with col1:
        crop = st.selectbox(
            "Crop Type",
            ["Hemp (fiber / grain / CBD)", "Cannabis (MJ, Adult-Use / Medical)"],
            key="crop_select",
        )

    with col2:
        lab = st.selectbox(
            "Soil Laboratory / Extraction Method",
            list(LAB_FACTORS.keys()),
            key="lab_select",
            help="Selects the conversion method for P and K. Modified Morgan values are multiplied by 2.2 (P) and 1.2 (K) to estimate Mehlich III equivalents.",
        )

    crop_key = "hemp" if "Hemp" in crop else "mj"

    if "Modified Morgan" in lab:
        st.info("ℹ️ **Modified Morgan detected.** P will be multiplied ×2.2 and K ×1.2 to approximate Mehlich III before comparing to targets.")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 3 — SOIL TEST INPUT
# ─────────────────────────────────────────────────────────────────────────────
with st.expander("🧪 Step 3: Enter Soil Test Results", expanded=True):
    st.markdown(
        "Enter values from your lab report. Leave blank if not measured. "
        "**pH, Organic Matter %, CEC, and Base Saturation %** always use their own fixed units. "
        "For all other sections, select the unit your lab report uses."
    )

    lab_factors = LAB_FACTORS.get(lab, {})

    # ── Section unit selectors ────────────────────────────────────────────
    unit_options = list(UNIT_CONVERSIONS.keys())
    unit_help = (
        "• ppm (mg/kg) — most common for Mehlich III labs\n"
        "• lbs/acre — some labs report exchangeable cations this way\n"
        "• kg/ha — metric equivalent\n\n"
        "The app will automatically convert to ppm before comparing to targets."
    )

    u_col1, u_col2, u_col3 = st.columns(3)
    with u_col1:
        unit_macro = st.selectbox(
            "Macronutrient units (P, K, Ca, Mg, S)",
            unit_options, key="unit_macro", help=unit_help,
        )
    with u_col2:
        unit_micro = st.selectbox(
            "Micronutrient units (Zn, Mn, Fe, Cu, B)",
            unit_options, key="unit_micro", help=unit_help,
        )
    with u_col3:
        unit_salts = st.selectbox(
            "Salts & Other units (Na, Al)",
            unit_options, key="unit_salts", help=unit_help,
        )

    # Map each nutrient to its section unit factor
    section_units = {
        "P (Phosphorus)":    unit_macro,
        "K (Potassium)":     unit_macro,
        "Ca (Calcium)":      unit_macro,
        "Mg (Magnesium)":    unit_macro,
        "S (Sulfur)":        unit_macro,
        "Zn (Zinc)":         unit_micro,
        "Mn (Manganese)":    unit_micro,
        "Fe (Iron)":         unit_micro,
        "Cu (Copper)":       unit_micro,
        "B (Boron)":         unit_micro,
        "Na (Sodium)":       unit_salts,
        "Al (Aluminum)":     unit_salts,
    }

    st.divider()

    # ── Per-nutrient help text ────────────────────────────────────────────
    help_texts = {
        "pH":                  "Dimensionless. Look for 'pH', 'Soil pH', or 'pH (1:1 water)' on your report.",
        "Organic Matter":      "Always enter as %. Look for 'Organic Matter %' or 'OM %'.",
        "P (Phosphorus)":      f"Dairy One: use 'Mod. Morgan P. ppm' column. Modified Morgan values will be auto-converted (×2.2).",
        "K (Potassium)":       f"Dairy One: use 'Mod. Morgan K. ppm' column. Modified Morgan values will be auto-converted (×1.2).",
        "Ca (Calcium)":        f"Dairy One: use 'Mod. Morgan Ca. ppm'. This is NOT the same as Base Saturation Ca%.",
        "Mg (Magnesium)":      f"Dairy One: use 'Mod. Morgan Mg. ppm'.",
        "S (Sulfur)":          f"Dairy One: use 'Mod. Morgan S. ppm'.",
        "Zn (Zinc)":           f"Dairy One: use 'Mod. Morgan Zn. ppm'.",
        "Mn (Manganese)":      f"Dairy One: use 'Mod. Morgan Mn. ppm'.",
        "Fe (Iron)":           f"Dairy One: use 'Mod. Morgan Fe. ppm'.",
        "Cu (Copper)":         f"Dairy One: use 'Mod. Morgan Cu. ppm'.",
        "B (Boron)":           f"Dairy One: use 'HWS Boron' or 'Mod. Morgan B. ppm'.",
        "Na (Sodium)":         f"Dairy One: use 'Mod. Morgan Na. ppm'.",
        "Al (Aluminum)":       f"Dairy One: use 'Mod. Morgan Al. ppm'.",
        "CEC":                 "Always enter in meq/100g. Also reported as 'Total Exchange Capacity (M.E.)' or 'T.E.C.' on some lab reports — these are the same thing.",
        "Base Saturation Ca%": "Always enter as %. This is the % of CEC occupied by Ca ions — different from Ca in ppm.",
        "Base Saturation K%":  "Always enter as %. This is the % of CEC occupied by K ions — different from K in ppm.",
    }

    groups = {
        "Basic Properties": ["pH", "Organic Matter"],
        "Macronutrients":   ["P (Phosphorus)", "K (Potassium)", "Ca (Calcium)", "Mg (Magnesium)", "S (Sulfur)"],
        "Micronutrients":   ["Zn (Zinc)", "Mn (Manganese)", "Fe (Iron)", "Cu (Copper)", "B (Boron)"],
        "Salts & Other":    ["Na (Sodium)", "Al (Aluminum)", "CEC", "Base Saturation Ca%", "Base Saturation K%"],
    }

    user_values  = {}
    section_unit_map = {}   # nname → unit string (for gap analysis)

    for group_name, nutrient_names in groups.items():
        st.markdown(f"**{group_name}**")
        cols = st.columns(min(len(nutrient_names), 4))
        for i, nname in enumerate(nutrient_names):
            nutrient = next((n for n in NUTRIENTS if n["name"] == nname), None)
            if nutrient is None:
                continue
            col = cols[i % 4]
            with col:
                # Display unit: fixed for non-convertible, section unit for others
                if not nutrient["allow_unit_conversion"]:
                    display_unit = nutrient["unit"]
                else:
                    display_unit = section_units.get(nname, "ppm (mg/kg)")

                section_unit_map[nname] = display_unit
                mm_note = " *(MM→M3)*" if nname in lab_factors else ""

                # Special label for CEC
                label = "CEC / Total Exchange Capacity (M.E.)" if nname == "CEC" else nname

                val = st.number_input(
                    f"{label} [{display_unit}]{mm_note}",
                    min_value=0.0,
                    max_value=50000.0,
                    value=None,
                    step=0.1,
                    format="%.2f",
                    key=f"nutrient_{nname}",
                    placeholder="—",
                    help=help_texts.get(nname, ""),
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

    lab_factors = LAB_FACTORS.get(lab, {})

    rows = []
    deficient_nutrients = []
    excess_nutrients    = []

    for n in NUTRIENTS:
        nname = n["name"]
        raw   = user_values.get(nname)

        if raw is None:
            rows.append({
                "Nutrient":         nname,
                "Unit (target)":    n["unit"],
                "Value entered":    "—",
                "Value (ppm equiv)":"—",
                "Target min":       n["hemp_min"] if crop_key == "hemp" else n["mj_min"],
                "Target max":       n["hemp_max"] if crop_key == "hemp" else n["mj_max"],
                "Status":           "— No data",
                "Note":             n["note"],
            })
            continue

        # 1. Convert section unit → ppm (only for nutrients that allow it)
        entered_unit = section_unit_map.get(nname, "ppm (mg/kg)")
        unit_conv    = UNIT_CONVERSIONS.get(entered_unit, 1.0) if n["allow_unit_conversion"] else 1.0
        # 2. Apply Modified Morgan → Mehlich III factor
        mm_conv   = lab_factors.get(nname, 1.0)
        converted = round(raw * unit_conv * mm_conv, 2)

        t_min = n["hemp_min"] if crop_key == "hemp" else n["mj_min"]
        t_max = n["hemp_max"] if crop_key == "hemp" else n["mj_max"]

        if converted < t_min:
            status = "⚠ DEFICIENT"
            deficient_nutrients.append(nname)
        elif converted > t_max:
            status = "▲ EXCESS"
            excess_nutrients.append(nname)
        else:
            status = "✓ ADEQUATE"

        needs_conv = (unit_conv != 1.0 or mm_conv != 1.0)
        show_conv  = converted if needs_conv else "—"
        rows.append({
            "Nutrient":         nname,
            "Unit (target)":    n["unit"],
            "Value entered":    raw,
            "Value (ppm equiv)":show_conv,
            "Target min":       t_min,
            "Target max":       t_max,
            "Status":           status,
            "Note":             n["note"],
        })

    df = pd.DataFrame(rows)

    def style_status(val):
        if "DEFICIENT" in str(val): return "background-color: #ffd6d6; color: #8b0000; font-weight: bold"
        if "EXCESS"    in str(val): return "background-color: #fff3cd; color: #856404; font-weight: bold"
        if "ADEQUATE"  in str(val): return "background-color: #d6f0d6; color: #006400; font-weight: bold"
        return "color: #888; font-style: italic"

    styled = df.style.map(style_status, subset=["Status"])
    st.dataframe(styled, use_container_width=True, hide_index=True)

    csv = df.to_csv(index=False)
    st.download_button("⬇ Download Results (CSV)", data=csv,
                       file_name="soil_gap_analysis.csv", mime="text/csv")

    # ── Possible Amendments ────────────────────────────────────────────────
    st.divider()
    st.markdown("## 🌾 Possible Amendments")
    st.caption(
        "The following are **possible options** based on the deficiencies and excesses identified above. "
        "These are not prescriptions. Always verify rates and products with a certified crop advisor "
        "before purchasing or applying anything. "
        "**Prices are estimates based on 2025–2026 US market data and will vary by supplier, region, "
        "quantity, and season — treat as rough budgeting guidance only.**"
    )

    if not deficient_nutrients and not excess_nutrients:
        st.success("🎉 All entered nutrients are within target range — no amendments indicated based on this data.")
    else:
        def form_tag(form_str):
            f = form_str.lower()
            if "liquid"   in f: cls, label = "tag-liquid",   "💧 Liquid"
            elif "pellet" in f: cls, label = "tag-pellet",   "🔵 Pellet"
            elif "granul" in f or "prill" in f: cls, label = "tag-granular", "🟡 Granular"
            else:               cls, label = "tag-powder",   "⚪ Powder"
            return f'<span class="tag {cls}">{label}</span>'

        def organic_tag(is_organic):
            if is_organic:
                return '<span class="tag tag-organic">🌿 Organic / OMRI</span>'
            return '<span class="tag tag-synthetic">🔬 Conventional</span>'

        if deficient_nutrients:
            st.markdown(f"### ⚠ Addressing Deficiencies: {', '.join(deficient_nutrients)}")
            shown = set()
            for nname in deficient_nutrients:
                short = nname.split("(")[0].strip().lower()
                for a in AMENDMENTS:
                    cond_lower = a["condition"].lower()
                    if short in cond_lower or nname.lower() in cond_lower:
                        key = a["amendment"]
                        if key in shown:
                            continue
                        shown.add(key)
                        price_str = (
                            f"<b>💲 Estimated price:</b> "
                            f"${a['price_low']:.2f}–${a['price_high']:.2f} {a['price_unit']}"
                            f"<br><i style='font-size:0.85rem;color:#666'>{a['price_note']}</i>"
                        ) if "price_low" in a else ""
                        st.markdown(f"""
<div class="amend-card">
<h4>{a['amendment']}</h4>
{organic_tag(a['organic'])} {form_tag(a['form'])}
<br><br>
<b>Addresses:</b> {a['condition']}<br>
<b>How to apply:</b> {a['application']}<br>
<b>Typical rate:</b> {a['rate']}<br>
<b>Notes:</b> {a['notes']}<br><br>
{price_str}
</div>""", unsafe_allow_html=True)

        if excess_nutrients:
            st.markdown(f"### ▲ Addressing Excess Levels: {', '.join(excess_nutrients)}")
            for nname in excess_nutrients:
                action = QUICK_AMEND.get(nname, {}).get("high", "Reduce inputs; re-test in 60–90 days")
                st.markdown(f"""
<div class="amend-card" style="border-left: 3px solid #e67e22;">
<h4>{nname} — Excess</h4>
<b>Suggested action:</b> {action}
</div>""", unsafe_allow_html=True)

    # ── Soil health context ───────────────────────────────────────────────
    with st.expander("💡 Soil Health Context & General Guidelines"):
        st.markdown("""
**pH** is the most important lever — it controls availability of nearly every nutrient.
Target **6.2–6.8** for cannabis and hemp. At pH < 6.0, Al and Mn become toxic;
at pH > 7.2, Fe, Zn, Mn, and B become unavailable.

**Organic matter** feeds the soil microbiome, buffers nutrients, and improves water retention.
A minimum of 3% OM is recommended; 5–8% is ideal for NY outdoor cultivation.

**Ca:Mg ratio** should be approximately 5:1 to 8:1 by weight (ppm).
High Mg relative to Ca can cause compaction in the silt loam soils common in NY.

**K:Mg ratio** should stay below 3:1.
High K suppresses Mg uptake — a common cause of Mg deficiency in NY cannabis fields.

**Micronutrients** (Zn, Mn, Fe, Cu, B) are primarily affected by pH.
Foliar applications are the fastest in-season correction.

For questions about NY-specific hemp or cannabis licensing and agronomy,
contact your local Cornell Cooperative Extension office.
""")

    # ── Amendment Budget Estimator ─────────────────────────────────────────
    if deficient_nutrients:
        st.divider()
        st.markdown("## 💰 Amendment Budget Estimator")
        st.caption(
            "Rough cost estimate for the amendments indicated above. "
            "Enter your field size to calculate total estimated cost. "
            "This estimate flows automatically into the Economics Tool."
        )

        col_a, _ = st.columns([1, 3])
        with col_a:
            acres_est = st.number_input(
                "Field size (acres)",
                min_value=0.01, max_value=10000.0, value=1.0, step=0.25,
                key="budget_acres",
                help="Total cultivated acreage for this field or season"
            )

        # Build cost table: one row per deficient nutrient, first matching amendment
        budget_rows = []
        total_low = 0.0
        total_high = 0.0
        seen_amend = set()

        for nname in deficient_nutrients:
            short = nname.split("(")[0].strip().lower()
            for a in AMENDMENTS:
                cond_lower = a["condition"].lower()
                if (short in cond_lower or nname.lower() in cond_lower) and a.get("cost_acre_low", 0) > 0:
                    key_a = a["amendment"]
                    if key_a in seen_amend:
                        continue
                    seen_amend.add(key_a)
                    low  = round(a["cost_acre_low"]  * acres_est, 2)
                    high = round(a["cost_acre_high"] * acres_est, 2)
                    total_low  += low
                    total_high += high
                    budget_rows.append({
                        "Deficiency":  nname,
                        "Amendment":   a["amendment"],
                        "$/acre (low)": f"${a['cost_acre_low']:.0f}",
                        "$/acre (high)":f"${a['cost_acre_high']:.0f}",
                        f"Est. cost ({acres_est:.2f} ac) low":  f"${low:,.0f}",
                        f"Est. cost ({acres_est:.2f} ac) high": f"${high:,.0f}",
                    })
                    break

        if budget_rows:
            budget_mid = (total_low + total_high) / 2
            st.dataframe(pd.DataFrame(budget_rows), use_container_width=True, hide_index=True)

            c1, c2, c3 = st.columns(3)
            c1.metric("Estimated Low", f"${total_low:,.0f}")
            c2.metric("Estimated Mid", f"${budget_mid:,.0f}")
            c3.metric("Estimated High", f"${total_high:,.0f}")

            # Store in session state for economics tool
            st.session_state["soil_amendment_cost_low"] = total_low
            st.session_state["soil_amendment_cost_high"] = total_high
            st.session_state["soil_amendment_cost_mid"] = budget_mid
            st.session_state["soil_amendment_acres"] = acres_est

            st.info(
                "💡 These estimates will be **pre-filled in the Economics Tool** "
                "under Fertilizer & Amendments. Open the Economics Tool from the sidebar."
            )
        else:
            st.caption("No per-acre cost data available for the detected deficiencies.")

st.divider()
st.markdown("## How This Tool Works")
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

st.caption("Built for NYS licensed cultivators · Data: USDA NRCS + US Census Geocoder · "
           "Targets: NY State Extension / CCE agronomic frameworks")
