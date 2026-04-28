"""
2_Economics.py — NY Cannabis / Hemp Economics Tool
Multi-page Streamlit app page.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
from io import BytesIO

try:
    import plotly.graph_objects as go
    import plotly.express as px
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

try:
    import openpyxl  # noqa: F401
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.sidebar import render_sidebar

st.set_page_config(
    page_title="Economics | NYS Cannabis Tool",
    page_icon="💰",
    layout="wide",
)
render_sidebar()

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.disclaimer-box {
    background: #fff3cd; border: 2px solid #e0a800;
    border-radius: 8px; padding: 16px 20px; margin-bottom: 20px; font-size: 0.92rem;
}
.metric-card {
    background: #f8f9fa; border-radius: 8px; padding: 14px 16px;
    border-left: 4px solid #1565C0; margin-bottom: 8px;
}
.positive { color: #155724; font-weight: bold; }
.negative { color: #8b0000; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "econ_n_scenarios" not in st.session_state:
    st.session_state.econ_n_scenarios = 1
if "econ_results" not in st.session_state:
    st.session_state.econ_results = None

# Amendment cost from soil assessment page
amend_cost_mid  = st.session_state.get("soil_amendment_cost_mid", None)
amend_cost_low  = st.session_state.get("soil_amendment_cost_low", None)
amend_cost_high = st.session_state.get("soil_amendment_cost_high", None)
amend_acres     = st.session_state.get("soil_amendment_acres", 1.0)

# ── NYS wholesale price reference (2024-25) ───────────────────────────────────
NYS_PRICES = {
    "Outdoor": {
        "Photoperiod": {"flower": (200, 600),  "preroll": (150, 300),  "extraction": (75, 175)},
        "Autoflower":  {"flower": (150, 400),  "preroll": (100, 250),  "extraction": (60, 150)},
    },
    "Greenhouse": {
        "Photoperiod": {"flower": (400, 1200), "preroll": (350, 700),  "extraction": (150, 300)},
        "Autoflower":  {"flower": (400, 1200), "preroll": (300, 700),  "extraction": (150, 300)},
    },
    "Indoor": {
        "Photoperiod": {"flower": (1000, 3000),"preroll": (700, 1200), "extraction": (300, 600)},
        "Autoflower":  {"flower": (1000, 2500),"preroll": (700, 1200), "extraction": (300, 500)},
    },
}

LABOR_TASKS = [
    ("Pre-season & Setup",                  "labor_setup"),
    ("Planting & Transplanting",            "labor_planting"),
    ("Crop Maintenance",                    "labor_maintenance"),
    ("Harvest",                             "labor_harvest"),
    ("Post-Harvest (dry, trim, pack)",      "labor_post"),
    ("Compliance & Record Keeping",         "labor_compliance"),
    ("Other Labor",                         "labor_other"),
]

VC_KEYS = [
    ("Seeds / Clones",              "vc_seeds"),
    ("Fertilizer & Amendments",     "vc_amendments"),
    ("Crop Protection",             "vc_crop_prot"),
    ("Water & Irrigation Supplies", "vc_water"),
    ("Energy / Electricity",        "vc_energy"),
    ("Packaging & Supplies",        "vc_packaging"),
    ("Testing / Lab Fees (COA)",    "vc_testing"),
    ("Other Variable Costs",        "vc_other"),
    # Excise tax is only shown/used for Cannabis (MJ) — handled separately in render/compute
]

NYS_EXCISE_RATE = 0.09   # 9% of gross wholesale revenue — NYS TP-600

# ── Hemp production models & price benchmarks ─────────────────────────────────
# Source: hemp_budgets_2021_MarkKentucky.xlsx (Bader, U. Kentucky 2021)
# Prices adjusted for current (2024-25) NY market conditions.
HEMP_PROD_MODELS = [
    "CBD Flower (Transplant)",
    "CBD Flower (Plasticulture)",
    "CBD Row Crop",
    "Grain Hemp",
    "Fiber Hemp",
]

# price range ($/lb), label, and Kentucky 2021 reference note
HEMP_PRICES = {
    "CBD Flower (Transplant)":    {"label": "Dry Floral Material (DFM)", "low": 2.00, "high": 5.00,
                                   "ref": "KY 2021: $4.50/lb · NY 2024–25 market: $2–5/lb"},
    "CBD Flower (Plasticulture)": {"label": "Dry Floral Material (DFM)", "low": 2.00, "high": 5.00,
                                   "ref": "KY 2021: $4.50/lb · NY 2024–25 market: $2–5/lb"},
    "CBD Row Crop":               {"label": "CBD Biomass / Dry Matter",  "low": 1.50, "high": 3.00,
                                   "ref": "KY 2021: $1.80–2.10/lb · NY 2024–25 market: $1.50–3.00/lb"},
    "Grain Hemp":                 {"label": "Hemp Grain",                "low": 0.35, "high": 0.65,
                                   "ref": "KY 2021: $0.48/lb · current market: $0.35–0.65/lb"},
    "Fiber Hemp":                 {"label": "Hemp Fiber",                "low": 0.08, "high": 0.18,
                                   "ref": "KY 2021: $0.11/lb · current market: $0.08–0.18/lb"},
}

# Kentucky 2021 reference budgets per acre (used for help text / defaults)
HEMP_REF = {
    "CBD Flower (Transplant)":    {"yield_ac": 2586, "spacing": "4×4 ft", "plants_ac": 2722,
                                   "transplant_$/plant": 2.17, "harvest_hrs": 32.4,
                                   "total_vc": 7419, "total_fc": 107, "net": 4112},
    "CBD Flower (Plasticulture)": {"yield_ac": 1655, "spacing": "5×5 ft", "plants_ac": 1742,
                                   "transplant_$/plant": 2.17, "harvest_hrs": 32.4,
                                   "plastic_mulch": 724, "plastic_removal": 156,
                                   "total_vc": 6347, "total_fc": 71,  "net": 1030},
    "CBD Row Crop":               {"yield_ac": 1400, "seed_lbs_ac": 30,  "seed_$/lb": 2.0,
                                   "total_vc": 873,  "total_fc": 122, "net": 1898},
    "Grain Hemp":                 {"yield_ac": 1200, "seed_lbs_ac": 30,  "seed_$/lb": 2.0,
                                   "total_vc": 336,  "total_fc": 121, "net": 120},
    "Fiber Hemp":                 {"yield_ac": 8000, "seed_lbs_ac": 50,  "seed_$/lb": 2.0,
                                   "total_vc": 442,  "total_fc": 122, "net": 316},
}

# Hemp VC keys that are always included in compute
HEMP_VC_KEYS = [
    ("Seeds / Transplants",           "vc_seeds"),
    ("Fertilizer & Amendments",       "vc_amendments"),
    ("Crop Protection",               "vc_crop_prot"),
    ("Water & Irrigation",            "vc_water"),
    ("Drying / Processing",           "vc_energy"),
    ("Packaging & Supplies",          "vc_packaging"),
    ("Testing / Lab Fees (COA)",      "vc_testing"),
    ("Hauling & Transport",           "vc_hauling"),
    ("Transplant Cost",               "vc_transplants"),
    ("Plastic Mulch & Drip Line",     "vc_plastic_mulch"),
    ("Plastic Removal",               "vc_plastic_removal"),
    ("Interest on Operating Capital", "vc_interest_oc"),
    ("Other Variable Costs",          "vc_other"),
]

FC_KEYS = [
    ("Land Rent / Lease",               "fc_land"),
    ("Buildings & Infrastructure",      "fc_buildings"),
    ("Equipment",                       "fc_equipment"),
    ("Licenses & Compliance (NYS OCM)", "fc_licenses"),
    ("Insurance",                       "fc_insurance"),
    ("Other Fixed Costs",               "fc_other"),
]


def gv(key, default=0.0):
    """Get widget value from session state safely."""
    v = st.session_state.get(key, default)
    return v if v is not None else default


def render_scenario(i):
    """Render all input sections for scenario i."""
    p = f"e{i}_"

    # ── 1. Operation Setup ────────────────────────────────────────────────
    with st.expander("🏗️ 1. Operation Setup", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.text_input("Scenario name",
                          value=st.session_state.get(f"{p}name", f"Scenario {i+1}"),
                          key=f"{p}name",
                          help="E.g. 'Outdoor Round 1', 'Greenhouse Auto', 'Indoor Photo'")
        with c2:
            st.selectbox("Crop type", ["Cannabis (MJ)", "Hemp"],
                         key=f"{p}crop_type",
                         help="Cannabis (MJ): subject to NYS 9% excise tax and federal §280E. "
                              "Hemp: federally legal — standard deductions apply, no excise tax.")
        with c3:
            st.selectbox("Operation type", ["Outdoor", "Greenhouse", "Indoor"],
                         key=f"{p}op_type")
        with c4:
            st.selectbox("Plant type", ["Photoperiod", "Autoflower"],
                         key=f"{p}plant_type")

        _crop_now = st.session_state.get(f"{p}crop_type", "Cannabis (MJ)")
        if _crop_now == "Hemp":
            _hmc1, _hmc2 = st.columns([2, 3])
            with _hmc1:
                st.selectbox("Hemp production model", HEMP_PROD_MODELS,
                             key=f"{p}hemp_prod_model",
                             help="Transplant models use per-plant yield; row-crop/grain/fiber use per-acre yield.")
            with _hmc2:
                _hpm_sel = st.session_state.get(f"{p}hemp_prod_model", HEMP_PROD_MODELS[0])
                _hpm_href = HEMP_REF.get(_hpm_sel, {})
                _hpm_hp   = HEMP_PRICES.get(_hpm_sel, {})
                st.caption(
                    f"**KY 2021 reference ({_hpm_sel}):** "
                    f"{_hpm_href.get('yield_ac', 0):,} lbs/acre · "
                    f"Net return: **${_hpm_href.get('net', 0):,}/acre** · "
                    f"Price: {_hpm_hp.get('ref', '')}"
                )

        c1, c2, c3 = st.columns(3)
        with c1:
            st.number_input("Total growing area (sq ft)", min_value=0.0, step=500.0,
                            key=f"{p}area_sqft",
                            help="Total canopy / field area for this scenario")
        with c2:
            st.number_input("Harvests / cycles per year", min_value=1, max_value=12,
                            value=1, step=1, key=f"{p}cycles",
                            help="Outdoor: 1–2. Greenhouse autoflower: up to 5. Indoor: 4–6.")
        with c3:
            st.number_input("Cultivated acres (optional override)",
                            min_value=0.0, step=0.1, key=f"{p}acres",
                            help="If blank, calculated from sq ft above. Used for amendment cost scaling.")

    # Derive crop/hemp flags (used by sections 2, 4, 6)
    _crop = st.session_state.get(f"{p}crop_type", "Cannabis (MJ)")
    _hpm  = st.session_state.get(f"{p}hemp_prod_model", HEMP_PROD_MODELS[0])
    _is_hemp           = _crop == "Hemp"
    _is_hemp_transplant = _is_hemp and _hpm in ["CBD Flower (Transplant)", "CBD Flower (Plasticulture)"]
    _is_hemp_rowcrop    = _is_hemp and _hpm in ["CBD Row Crop", "Grain Hemp", "Fiber Hemp"]
    _is_plasticulture   = _hpm == "CBD Flower (Plasticulture)"
    area   = gv(f"{p}area_sqft")
    cycles = int(gv(f"{p}cycles", 1))
    acres  = gv(f"{p}acres") or (area / 43560)

    # ── 2. Production & Yield ─────────────────────────────────────────────
    with st.expander("🌿 2. Production & Yield", expanded=True):
        if _is_hemp_transplant:
            _href2 = HEMP_REF.get(_hpm, {})
            st.markdown("**Plant Spacing Calculator** — plants/acre from row × in-row spacing")
            sc1, sc2, sc3 = st.columns(3)
            with sc1:
                _sp_str = _href2.get("spacing", "4×4 ft")
                try:
                    _sp_parts = _sp_str.replace("ft", "").split("×")
                    _def_row = float(_sp_parts[0].strip())
                    _def_inrow = float(_sp_parts[1].strip())
                except (ValueError, IndexError):
                    _def_row, _def_inrow = 4.0, 4.0
                row_sp = st.number_input("Row spacing (ft)", min_value=0.5, value=_def_row,
                                         step=0.5, key=f"{p}row_spacing",
                                         help=f"KY ref: {_sp_str}")
            with sc2:
                inrow_sp = st.number_input("In-row spacing (ft)", min_value=0.5, value=_def_inrow,
                                            step=0.5, key=f"{p}inrow_spacing")
            with sc3:
                calc_pl_ac = 43560 / (row_sp * inrow_sp) if row_sp > 0 and inrow_sp > 0 else 0
                st.metric("Plants / acre (calculated)", f"{calc_pl_ac:,.0f}",
                          help=f"KY 2021: {_href2.get('plants_ac', 0):,} plants/acre at {_sp_str}")
            calc_total_pl = calc_pl_ac * acres if acres > 0 else 0

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.number_input("Plants per cycle (override)", min_value=0.0, step=10.0,
                                value=float(round(calc_total_pl)),
                                key=f"{p}n_plants",
                                help="Auto-calculated from spacing × acres. Override if needed.")
            with c2:
                _ypp_ref = (_href2.get("yield_ac", 0) / max(_href2.get("plants_ac", 1), 1))
                st.number_input("Dry yield per plant (lbs)", min_value=0.0, step=0.01,
                                format="%.3f", key=f"{p}yield_pp",
                                help=f"After drying. KY 2021 ref: {_ypp_ref:.3f} lbs/plant")
            with c3:
                n_pl = gv(f"{p}n_plants"); y_pp = gv(f"{p}yield_pp")
                total_yield = n_pl * y_pp * cycles
                st.metric("Total dry yield / yr (lbs)", f"{total_yield:,.1f}",
                          help=f"KY ref: {_href2.get('yield_ac', 0) * acres:.0f} lbs for {acres:.1f} acres")
            with c4:
                st.number_input("Moisture loss %", min_value=50.0, max_value=95.0,
                                value=82.0, step=1.0, key=f"{p}moisture")
            if _href2.get("yield_ac") and acres > 0:
                st.caption(f"KY 2021 reference yield for {acres:.1f} acres: "
                           f"**{_href2['yield_ac'] * acres:,.0f} lbs** ({_href2['yield_ac']:,} lbs/acre)")

        elif _is_hemp_rowcrop:
            _href2 = HEMP_REF.get(_hpm, {})
            c1, c2, c3 = st.columns(3)
            with c1:
                st.number_input("Yield per acre (lbs/acre)", min_value=0.0,
                                value=float(_href2.get("yield_ac", 0)), step=50.0,
                                key=f"{p}yield_per_acre",
                                help=f"KY 2021 reference: {_href2.get('yield_ac', 0):,} lbs/acre")
            with c2:
                y_ac = gv(f"{p}yield_per_acre")
                total_yield = y_ac * acres * cycles
                st.metric("Total dry yield / yr (lbs)", f"{total_yield:,.1f}")
            with c3:
                st.number_input("Moisture loss %", min_value=50.0, max_value=95.0,
                                value=82.0, step=1.0, key=f"{p}moisture")
            if acres > 0:
                st.caption(f"Yield = {y_ac:,.0f} lbs/acre × {acres:.1f} acres × {cycles} cycle(s)")

        else:  # Cannabis MJ
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.number_input("Plants per cycle", min_value=0.0, step=10.0,
                                key=f"{p}n_plants",
                                help="Reference: greenhouse ~450 auto / 3,150 photo per 30,000 sq ft")
            with c2:
                st.number_input("Dry yield per plant (lbs)", min_value=0.0,
                                step=0.01, format="%.3f", key=f"{p}yield_pp",
                                help="After drying & trimming. Ref: auto ~0.04 lbs; photoperiod ~0.18 lbs (greenhouse)")
            with c3:
                n_pl = gv(f"{p}n_plants"); y_pp = gv(f"{p}yield_pp")
                total_yield = n_pl * y_pp * cycles
                st.metric("Total dry yield / yr (lbs)", f"{total_yield:,.1f}")
            with c4:
                st.number_input("Moisture loss %", min_value=50.0, max_value=95.0,
                                value=82.0, step=1.0, key=f"{p}moisture",
                                help="~82% moisture lost during drying (18% of wet weight remains as dry flower)")
            if area > 0 and total_yield > 0:
                st.caption(f"Yield density: **{total_yield/area*1000:.2f} g/sq ft/yr** "
                           f"| **{total_yield/area*43560:.1f} lbs/acre/yr**")

    # ── 3. Labor Costs ────────────────────────────────────────────────────
    with st.expander("👷 3. Labor Costs", expanded=True):
        c1, _ = st.columns([1, 4])
        with c1:
            st.number_input("Hourly wage ($/hr)", min_value=0.0, value=20.0,
                            step=0.50, key=f"{p}wage",
                            help="Reference: $20/hr (Ruterbories et al. 2025). Include benefits if applicable.")

        st.markdown("**Total hours for the season / year by task category:**")
        if _is_hemp_transplant or _is_hemp_rowcrop:
            _lhref = HEMP_REF.get(_hpm, {})
            if _lhref.get("harvest_hrs"):
                st.caption(f"KY 2021 reference harvest labor: **{_lhref['harvest_hrs']} hrs/acre** for {_hpm}")
        cols = st.columns(4)
        for j, (label, suffix) in enumerate(LABOR_TASKS):
            with cols[j % 4]:
                st.number_input(f"{label} (hrs)", min_value=0.0, step=1.0,
                                key=f"{p}{suffix}")

        wage        = gv(f"{p}wage", 20.0)
        total_hrs   = sum(gv(f"{p}{s}") for _, s in LABOR_TASKS)
        total_labor = wage * total_hrs
        st.metric("Total Labor Cost", f"${total_labor:,.0f}",
                  delta=f"{total_hrs:.0f} hrs × ${wage:.2f}/hr", delta_color="off")

    # ── 4. Variable Costs ─────────────────────────────────────────────────
    with st.expander("🧪 4. Variable Costs (Annual / Seasonal)", expanded=True):

        # Pre-fill amendments from soil assessment if available and not yet set
        if amend_cost_mid is not None:
            acres_here = gv(f"{p}acres") or (gv(f"{p}area_sqft") / 43560) or amend_acres
            amend_prefill = round(amend_cost_mid * (acres_here / max(amend_acres, 0.01)), 0)
            st.info(
                f"🌱 **From Soil Assessment:** Amendment cost ≈ **${amend_prefill:,.0f}** "
                f"(scaled to {acres_here:.2f} acres). Pre-filled below — edit if needed."
            )
            if f"{p}vc_amendments" not in st.session_state:
                st.session_state[f"{p}vc_amendments"] = float(amend_prefill)

        wage2      = gv(f"{p}wage", 20.0)
        total_hrs2 = sum(gv(f"{p}{s}") for _, s in LABOR_TASKS)
        total_lbr2 = wage2 * total_hrs2

        if _is_hemp:
            _vc_href = HEMP_REF.get(_hpm, {})
            st.caption(f"KY 2021 total variable costs reference: **${_vc_href.get('total_vc', 0):,}/acre**")
            _hemp_vc_left = [
                ("Seeds / Transplants ($)", "vc_seeds",
                 (f"Transplant purchase. KY ref: ${_vc_href.get('transplant_$/plant', 2.17):.2f}/plant")
                 if _is_hemp_transplant else
                 f"Seed. KY ref: {_vc_href.get('seed_lbs_ac', '')} lbs/acre × ${_vc_href.get('seed_$/lb', '')} /lb"),
                ("Fertilizer & Amendments ($)", "vc_amendments",
                 "Pre-filled from Soil Assessment if available"),
                ("Crop Protection ($)", "vc_crop_prot",
                 "Pesticides, biologicals, fungicides, beneficial insects"),
                ("Water & Irrigation ($)", "vc_water",
                 "Municipal water, well costs, drip tape, irrigation supplies"),
                ("Drying / Processing ($)", "vc_energy",
                 "Drying, curing, processing energy costs"),
                ("Packaging & Supplies ($)", "vc_packaging",
                 "Bags, labels, trim bins, drying nets"),
            ]
            _hemp_vc_right = [
                ("Testing / Lab Fees (COA) ($)", "vc_testing",
                 "Compliance COA testing: ~$50–150/sample"),
                ("Hauling & Transport ($)", "vc_hauling",
                 "Transport to processor/buyer. Include haul distance & rate."),
                ("Other Variable Costs ($)", "vc_other", ""),
            ]
            if _is_hemp_transplant:
                _hemp_vc_right.insert(0, (
                    "Transplant Cost ($)", "vc_transplants",
                    f"Cost to purchase/grow transplants. KY ref: ${_vc_href.get('transplant_$/plant', 2.17):.2f}/plant"))
            if _is_plasticulture:
                _hemp_vc_right.insert(1, (
                    "Plastic Mulch & Drip Line ($)", "vc_plastic_mulch",
                    f"KY 2021 reference: ${_vc_href.get('plastic_mulch', 724):,}/acre"))
                _hemp_vc_right.insert(2, (
                    "Plastic Removal ($)", "vc_plastic_removal",
                    f"KY 2021 reference: ${_vc_href.get('plastic_removal', 156):,}/acre"))

            c1, c2 = st.columns(2)
            with c1:
                for label, suffix, help_txt in _hemp_vc_left:
                    st.number_input(label, min_value=0.0, step=10.0,
                                    key=f"{p}{suffix}", help=help_txt)
            with c2:
                for label, suffix, help_txt in _hemp_vc_right:
                    st.number_input(label, min_value=0.0, step=10.0,
                                    key=f"{p}{suffix}", help=help_txt)

            # Interest on Operating Capital
            st.divider()
            st.markdown("**Interest on Operating Capital**")
            ioc_c1, ioc_c2, ioc_c3 = st.columns(3)
            with ioc_c1:
                ioc_months = st.number_input("Months capital is tied up", min_value=1, max_value=12,
                                             value=6, step=1, key=f"{p}ioc_months",
                                             help="Outdoor hemp: ~4–6 months (KY 2021 used 6 months)")
            with ioc_c2:
                ioc_rate = st.number_input("Interest rate (%)", min_value=0.0, max_value=30.0,
                                           value=6.0, step=0.5, key=f"{p}ioc_rate",
                                           help="KY 2021 used 6.0% annual rate on operating loan")
            with ioc_c3:
                _all_hemp_suf = [s for _, s in HEMP_VC_KEYS if s != "vc_interest_oc"]
                _ioc_base = sum(gv(f"{p}{s}") for s in _all_hemp_suf) + total_lbr2
                _ioc_est  = _ioc_base * (ioc_rate / 100) * (ioc_months / 12)
                st.metric("Interest on OC (estimated)", f"${_ioc_est:,.0f}")
            st.session_state[f"{p}vc_interest_oc_calc"] = _ioc_est

            total_vc = sum(gv(f"{p}{s}") for s in _all_hemp_suf) + total_lbr2 + _ioc_est
            st.metric("Total Variable Costs (incl. labor & interest on OC)", f"${total_vc:,.0f}")

        else:  # Cannabis MJ
            c1, c2 = st.columns(2)
            vc_items = [
                ("Seeds / Clones ($)", "vc_seeds",
                 "Auto seeds ~$1.50/seed; photoperiod clones ~$13.50/clone"),
                ("Fertilizer & Amendments ($)", "vc_amendments",
                 "Pre-filled from Soil Assessment if available"),
                ("Crop Protection ($)", "vc_crop_prot",
                 "Pesticides, biologicals, fungicides, beneficial insects"),
                ("Water & Irrigation Supplies ($)", "vc_water",
                 "Municipal water, well costs, drip tape, irrigation supplies"),
            ]
            vc_items2 = [
                ("Energy / Electricity ($)", "vc_energy",
                 "Lighting, HVAC, dehumidifiers (indoor/greenhouse); pumps (outdoor)"),
                ("Packaging & Supplies ($)", "vc_packaging",
                 "Bags, jars, labels, trim bins, drying nets, zip ties"),
                ("Testing / Lab Fees (COA) ($)", "vc_testing",
                 "NYS compliance COA testing: ~$50–150/sample. Budget 1 sample per lot/variety."),
                ("Other Variable Costs ($)", "vc_other", ""),
            ]
            with c1:
                for label, suffix, help_txt in vc_items:
                    st.number_input(label, min_value=0.0, step=10.0,
                                    key=f"{p}{suffix}", help=help_txt)
            with c2:
                for label, suffix, help_txt in vc_items2:
                    st.number_input(label, min_value=0.0, step=10.0,
                                    key=f"{p}{suffix}", help=help_txt)

            total_vc = sum(gv(f"{p}{s}") for _, s in VC_KEYS) + total_lbr2

            # ── NYS Excise Tax — Cannabis (MJ) only ───────────────────────
            ty_vc  = gv(f"{p}n_plants") * gv(f"{p}yield_pp") * int(gv(f"{p}cycles", 1))
            fl_p   = gv(f"{p}fl_price"); pr_p = gv(f"{p}pr_price"); ex_p = gv(f"{p}ex_price")
            fl_pct = gv(f"{p}fl_pct");   pr_pct = gv(f"{p}pr_pct"); ex_pct = gv(f"{p}ex_pct")
            rev_est    = ty_vc * (fl_pct/100*fl_p + pr_pct/100*pr_p + ex_pct/100*ex_p)
            excise_est = round(rev_est * NYS_EXCISE_RATE, 2)
            st.divider()
            st.markdown("**NYS Cannabis Excise Tax — Cannabis (MJ) only**")
            st.caption(
                "9% of gross wholesale revenue. Remit quarterly via **NYS TP-600**. "
                "Treated as COGS (Account 5100) — deductible under §280E federally and in NYS. "
                "Auto-estimated from your revenue inputs; edit if your actual figure differs."
            )
            st.number_input(
                "NYS Excise Tax — 9% of gross revenue ($)",
                min_value=0.0, step=10.0,
                value=float(excise_est) if excise_est > 0 else 0.0,
                key=f"{p}vc_excise",
                help=f"Auto-estimate: ${excise_est:,.0f}  (9% × ${rev_est:,.0f} estimated revenue). "
                     "Fill in Step 6 prices first for an accurate estimate.",
            )
            total_vc += gv(f"{p}vc_excise")
            st.metric("Total Variable Costs (incl. labor)", f"${total_vc:,.0f}")

    # ── 5. Fixed Costs ────────────────────────────────────────────────────
    with st.expander("🏠 5. Fixed Costs (Annual)", expanded=True):
        st.caption(
            "Enter annual costs. For owned assets use depreciation "
            "(purchase price ÷ useful life in years). "
            "NYS OCM cultivator license fee varies by canopy tier — check current fee schedule."
        )
        c1, c2 = st.columns(2)
        fc_items = [
            ("Land Rent / Lease ($)",            "fc_land",
             "Annual rent, or opportunity cost if owned. NY farmland: ~$50–300/acre/yr"),
            ("Buildings & Infrastructure ($)",   "fc_buildings",
             "Greenhouse, barn, drying facility, fencing — annual depreciation"),
            ("Equipment ($)",                    "fc_equipment",
             "Tractor, lighting, HVAC, irrigation system — annual depreciation"),
        ]
        fc_items2 = [
            ("Licenses & Compliance — NYS OCM ($)", "fc_licenses",
             "State license fees + compliance costs + legal. NY cultivator license: varies by tier"),
            ("Insurance ($)",                    "fc_insurance",
             "Crop, liability, and property insurance"),
            ("Other Fixed Costs ($)",            "fc_other", ""),
        ]
        with c1:
            for label, suffix, help_txt in fc_items:
                st.number_input(label, min_value=0.0, step=100.0,
                                key=f"{p}{suffix}", help=help_txt)
        with c2:
            for label, suffix, help_txt in fc_items2:
                st.number_input(label, min_value=0.0, step=100.0,
                                key=f"{p}{suffix}", help=help_txt)

        total_fc = sum(gv(f"{p}{s}") for _, s in FC_KEYS)
        st.metric("Total Annual Fixed Costs", f"${total_fc:,.0f}")

    # ── 6. Revenue ────────────────────────────────────────────────────────
    with st.expander("💰 6. Revenue", expanded=True):
        if _is_hemp:
            _hpinfo = HEMP_PRICES.get(_hpm, list(HEMP_PRICES.values())[0])
            st.markdown(f"**Hemp price reference — {_hpm} ({_hpinfo['label']}) (2024–25):**")
            st.caption(_hpinfo["ref"])
            st.divider()
            _mid_hp = (_hpinfo["low"] + _hpinfo["high"]) / 2
            rc1, rc2 = st.columns(2)
            with rc1:
                st.number_input(f"Wholesale price / lb — {_hpinfo['label']} ($/lb)",
                                min_value=0.0, step=0.10, format="%.2f",
                                value=float(_mid_hp),
                                key=f"{p}hemp_price",
                                help=f"Market range: ${_hpinfo['low']:.2f}–${_hpinfo['high']:.2f}/lb")
                st.caption(f"Low: ${_hpinfo['low']:.2f} · High: ${_hpinfo['high']:.2f} · Mid: ${_mid_hp:.2f}/lb")
            with rc2:
                if _is_hemp_rowcrop:
                    _yld_prev = gv(f"{p}yield_per_acre") * acres * cycles
                else:
                    _yld_prev = gv(f"{p}n_plants") * gv(f"{p}yield_pp") * cycles
                _rev_prev = _yld_prev * gv(f"{p}hemp_price", _mid_hp)
                st.metric("Revenue preview", f"${_rev_prev:,.0f}",
                          help=f"{_yld_prev:,.1f} lbs × ${gv(f'{p}hemp_price', _mid_hp):.2f}/lb")
                _rev_href3 = HEMP_REF.get(_hpm, {})
                if _rev_href3.get("net") and acres > 0:
                    st.caption(f"KY 2021 ref net return for {acres:.1f} acres: "
                               f"**${_rev_href3['net'] * acres:,.0f}**")
        else:  # Cannabis MJ
            op  = st.session_state.get(f"{p}op_type", "Outdoor")
            pt  = st.session_state.get(f"{p}plant_type", "Photoperiod")
            ref = NYS_PRICES.get(op, NYS_PRICES["Outdoor"]).get(pt, NYS_PRICES["Outdoor"]["Photoperiod"])

            st.markdown(f"**NYS wholesale price reference — {op} {pt} (2024–25):**")
            rc1, rc2, rc3 = st.columns(3)
            rc1.caption(f"🌸 Flower: ${ref['flower'][0]:,}–${ref['flower'][1]:,} /lb")
            rc2.caption(f"🚬 Pre-rolls: ${ref['preroll'][0]:,}–${ref['preroll'][1]:,} /lb")
            rc3.caption(f"⚗️ Extraction: ${ref['extraction'][0]:,}–${ref['extraction'][1]:,} /lb")
            st.divider()

            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**% of dry yield per product stream (must sum to 100%)**")
                flower_pct     = st.number_input("% → Whole Flower",        0.0, 100.0, 60.0, 5.0, key=f"{p}fl_pct")
                preroll_pct    = st.number_input("% → Pre-rolls",           0.0, 100.0, 25.0, 5.0, key=f"{p}pr_pct")
                extraction_pct = st.number_input("% → Extraction/Biomass",  0.0, 100.0, 15.0, 5.0, key=f"{p}ex_pct")
                total_pct = flower_pct + preroll_pct + extraction_pct
                if abs(total_pct - 100) > 0.5:
                    st.warning(f"⚠️ Sum = {total_pct:.0f}% — adjust to reach 100%")
                else:
                    st.success("✅ Sums to 100%")
            with c2:
                st.markdown("**Wholesale price per lb**")
                mid_fl = (ref["flower"][0]    + ref["flower"][1])    / 2
                mid_pr = (ref["preroll"][0]   + ref["preroll"][1])   / 2
                mid_ex = (ref["extraction"][0] + ref["extraction"][1]) / 2
                st.number_input("Flower price ($/lb)",     0.0, step=25.0, value=float(mid_fl), key=f"{p}fl_price")
                st.number_input("Pre-roll price ($/lb)",   0.0, step=25.0, value=float(mid_pr), key=f"{p}pr_price")
                st.number_input("Extraction price ($/lb)", 0.0, step=25.0, value=float(mid_ex), key=f"{p}ex_price")

            ty_prev = gv(f"{p}n_plants") * gv(f"{p}yield_pp") * int(gv(f"{p}cycles", 1))
            rev_prev = (
                ty_prev * gv(f"{p}fl_pct") / 100 * gv(f"{p}fl_price") +
                ty_prev * gv(f"{p}pr_pct") / 100 * gv(f"{p}pr_price") +
                ty_prev * gv(f"{p}ex_pct") / 100 * gv(f"{p}ex_price")
            )
            if rev_prev > 0:
                st.metric("Revenue preview", f"${rev_prev:,.0f}",
                          help="Preliminary — run full analysis in the Summary tab")


def compute_scenario(i):
    """Collect all inputs for scenario i and return computed results."""
    p = f"e{i}_"

    area   = gv(f"{p}area_sqft")
    cycles = int(gv(f"{p}cycles", 1))
    acres  = gv(f"{p}acres") or (area / 43560)

    is_mj  = st.session_state.get(f"{p}crop_type", "Cannabis (MJ)") == "Cannabis (MJ)"
    is_hemp = not is_mj
    _hpm   = st.session_state.get(f"{p}hemp_prod_model", HEMP_PROD_MODELS[0])
    _is_hemp_rowcrop  = is_hemp and _hpm in ["CBD Row Crop", "Grain Hemp", "Fiber Hemp"]
    _is_plasticulture = _hpm == "CBD Flower (Plasticulture)"

    # ── Yield ─────────────────────────────────────────────────────────────
    if _is_hemp_rowcrop:
        t_yield = gv(f"{p}yield_per_acre") * acres * cycles
    else:
        t_yield = gv(f"{p}n_plants") * gv(f"{p}yield_pp") * cycles

    # ── Labor ─────────────────────────────────────────────────────────────
    wage      = gv(f"{p}wage", 20.0)
    total_hrs = sum(gv(f"{p}{s}") for _, s in LABOR_TASKS)
    total_lbr = wage * total_hrs

    # ── Variable Costs ────────────────────────────────────────────────────
    if is_hemp:
        _hemp_suf = [s for _, s in HEMP_VC_KEYS if s != "vc_interest_oc"]
        # Zero out inapplicable line items
        if not _is_plasticulture:
            for _s in ["vc_plastic_mulch", "vc_plastic_removal"]:
                if f"{p}{_s}" not in st.session_state:
                    st.session_state[f"{p}{_s}"] = 0.0
        if _is_hemp_rowcrop:
            if f"{p}vc_transplants" not in st.session_state:
                st.session_state[f"{p}vc_transplants"] = 0.0
        vc_vals = {label: gv(f"{p}{s}") for label, s in HEMP_VC_KEYS if s != "vc_interest_oc"}
        ioc = st.session_state.get(f"{p}vc_interest_oc_calc", 0.0)
        vc_vals["Interest on Operating Capital"] = ioc
        total_vc   = sum(vc_vals.values()) + total_lbr
        excise_tax = 0.0
    else:
        vc_vals    = {label: gv(f"{p}{s}") for label, s in VC_KEYS}
        excise_tax = gv(f"{p}vc_excise") if is_mj else 0.0
        total_vc   = sum(vc_vals.values()) + total_lbr + excise_tax

    fc_vals     = {label: gv(f"{p}{s}") for label, s in FC_KEYS}
    total_fc    = sum(fc_vals.values())
    total_costs = total_vc + total_fc

    # ── Revenue ───────────────────────────────────────────────────────────
    if is_hemp:
        _hpinfo   = HEMP_PRICES.get(_hpm, list(HEMP_PRICES.values())[0])
        _mid_hp   = (_hpinfo["low"] + _hpinfo["high"]) / 2
        hemp_price = gv(f"{p}hemp_price", _mid_hp)
        total_rev  = t_yield * hemp_price
        wt_price   = hemp_price
        rev_breakdown = {_hpinfo["label"]: total_rev}
    else:
        fl_rev  = t_yield * gv(f"{p}fl_pct") / 100 * gv(f"{p}fl_price")
        pr_rev  = t_yield * gv(f"{p}pr_pct") / 100 * gv(f"{p}pr_price")
        ex_rev  = t_yield * gv(f"{p}ex_pct") / 100 * gv(f"{p}ex_price")
        total_rev = fl_rev + pr_rev + ex_rev
        wt_price  = total_rev / t_yield if t_yield > 0 else 0
        rev_breakdown = {"Flower": fl_rev, "Pre-rolls": pr_rev, "Extraction": ex_rev}

    bep_price = total_costs / t_yield if t_yield > 0 else 0
    bep_yield = total_costs / wt_price if wt_price > 0 else 0

    # ── Tax Analysis (§280E — MJ only) ────────────────────────────────────
    fed_taxable_income = total_rev - total_vc if is_mj else total_rev - total_costs
    nys_taxable_income = total_rev - total_costs
    fed_tax_est        = max(fed_taxable_income * 0.24, 0)
    nys_tax_est        = max(nys_taxable_income * 0.0685, 0)
    e280_penalty       = fed_tax_est - max((total_rev - total_costs) * 0.24, 0) if is_mj else 0

    return {
        "name":               st.session_state.get(f"{p}name", f"Scenario {i+1}"),
        "crop_type":          st.session_state.get(f"{p}crop_type", "Cannabis (MJ)"),
        "hemp_prod_model":    _hpm if is_hemp else None,
        "op_type":            st.session_state.get(f"{p}op_type", "Outdoor"),
        "plant_type":         st.session_state.get(f"{p}plant_type", "Photoperiod"),
        "area_sqft":          area,
        "acres":              acres,
        "cycles":             cycles,
        "total_yield_lbs":    t_yield,
        "total_labor":        total_lbr,
        "labor_hours":        total_hrs,
        "vc_breakdown":       {"Labor": total_lbr, **vc_vals,
                               **({"NYS Excise Tax (9%)": excise_tax} if is_mj and excise_tax > 0 else {})},
        "excise_tax":         excise_tax,
        "total_vc":           total_vc,
        "fc_breakdown":       fc_vals,
        "total_fc":           total_fc,
        "total_costs":        total_costs,
        "rev_breakdown":      rev_breakdown,
        "total_revenue":      total_rev,
        "gross_margin":       total_rev - total_vc,
        "net_return":         total_rev - total_costs,
        "cost_per_lb":        total_costs / t_yield if t_yield > 0 else 0,
        "breakeven_price":    bep_price,
        "breakeven_yield":    bep_yield,
        "weighted_avg_price": wt_price,
        "is_mj":              is_mj,
        "fed_taxable_income": fed_taxable_income,
        "nys_taxable_income": nys_taxable_income,
        "fed_tax_est":        fed_tax_est,
        "nys_tax_est":        nys_tax_est,
        "e280_penalty":       e280_penalty,
    }


def render_summary(results):
    """Render the summary dashboard for all computed scenarios."""
    if not results:
        st.info("No scenario data yet — fill in at least one scenario and click Calculate.")
        return

    names = [r["name"] for r in results]

    # ── KPI table ─────────────────────────────────────────────────────────
    st.markdown("### 📋 Summary Table")
    kpi_rows = []
    for r in results:
        sign = "+" if r["net_return"] >= 0 else ""
        kpi_rows.append({
            "Scenario":          r["name"],
            "Operation":         r["hemp_prod_model"] if r.get("hemp_prod_model") else f"{r['op_type']} {r['plant_type']}",
            "Total Yield (lbs)": f"{r['total_yield_lbs']:,.1f}",
            "Total Revenue":     f"${r['total_revenue']:,.0f}",
            "Variable Costs":    f"${r['total_vc']:,.0f}",
            "Fixed Costs":       f"${r['total_fc']:,.0f}",
            "Total Costs":       f"${r['total_costs']:,.0f}",
            "Gross Margin":      f"${r['gross_margin']:,.0f}",
            "Net Return":        f"{sign}${r['net_return']:,.0f}",
            "Cost / lb":         f"${r['cost_per_lb']:,.2f}",
            "Break-even Price":  f"${r['breakeven_price']:,.2f}/lb",
        })
    st.dataframe(pd.DataFrame(kpi_rows), use_container_width=True, hide_index=True)

    summary_df = pd.DataFrame(kpi_rows)
    st.divider()

    # ── Revenue vs Costs bar chart ────────────────────────────────────────
    st.markdown("### 📊 Revenue vs. Costs")
    if not HAS_PLOTLY:
        st.warning("Install plotly to see charts: `pip install plotly`")
        return
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(name="Total Revenue",  x=names,
                             y=[r["total_revenue"] for r in results],
                             marker_color="#2e7d32"))
    fig_bar.add_trace(go.Bar(name="Variable Costs", x=names,
                             y=[r["total_vc"] for r in results],
                             marker_color="#e57373"))
    fig_bar.add_trace(go.Bar(name="Fixed Costs",    x=names,
                             y=[r["total_fc"] for r in results],
                             marker_color="#ffb74d"))
    fig_bar.update_layout(barmode="group", yaxis_tickprefix="$",
                          yaxis_title="Dollars", height=380,
                          legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig_bar, use_container_width=True)

    # ── Net return ────────────────────────────────────────────────────────
    st.markdown("### 💵 Net Return (Revenue − Total Costs)")
    fig_net = go.Figure(go.Bar(
        x=names,
        y=[r["net_return"] for r in results],
        marker_color=["#2e7d32" if r["net_return"] >= 0 else "#c62828" for r in results],
        text=[f"${r['net_return']:,.0f}" for r in results],
        textposition="outside",
    ))
    fig_net.update_layout(yaxis_tickprefix="$", yaxis_title="Net Return ($)",
                          height=320, showlegend=False)
    fig_net.add_hline(y=0, line_dash="dash", line_color="gray")
    st.plotly_chart(fig_net, use_container_width=True)

    # ── Cost breakdown per scenario ───────────────────────────────────────
    st.markdown("### 🥧 Cost Breakdown")
    pie_cols = st.columns(min(len(results), 3))
    for col, r in zip(pie_cols, results):
        all_costs = {**r["vc_breakdown"], **r["fc_breakdown"]}
        filtered  = {k: v for k, v in all_costs.items() if v > 0}
        if filtered:
            fig_pie = px.pie(
                values=list(filtered.values()),
                names=list(filtered.keys()),
                title=r["name"],
                hole=0.35,
            )
            fig_pie.update_layout(height=350, showlegend=True,
                                  legend=dict(font=dict(size=10)))
            col.plotly_chart(fig_pie, use_container_width=True)

    # ── Break-even analysis ───────────────────────────────────────────────
    st.divider()
    st.markdown("### ⚖️ Break-Even Analysis")
    be_rows = []
    for r in results:
        be_rows.append({
            "Scenario":                        r["name"],
            "Break-even price ($/lb)":         f"${r['breakeven_price']:,.2f}",
            "Break-even yield (lbs/yr)":       f"{r['breakeven_yield']:,.1f}",
            "Actual yield (lbs/yr)":           f"{r['total_yield_lbs']:,.1f}",
            "Actual weighted avg price ($/lb)":f"${r['weighted_avg_price']:,.2f}",
            "Yield surplus / gap (lbs)":       f"{r['total_yield_lbs'] - r['breakeven_yield']:+,.1f}",
            "Price surplus / gap ($/lb)":      f"${r['weighted_avg_price'] - r['breakeven_price']:+,.2f}",
        })
    st.dataframe(pd.DataFrame(be_rows), use_container_width=True, hide_index=True)
    st.caption(
        "Break-even price = total costs ÷ total yield. "
        "Break-even yield = total costs ÷ weighted average price. "
        "A positive surplus means the operation covers all costs at current inputs."
    )

    # ── §280E / Tax Analysis (MJ only) ───────────────────────────────────
    mj_results = [r for r in results if r["is_mj"]]
    tax_rows   = []
    if mj_results:
        st.divider()
        st.markdown("### 🏛️ Federal §280E & NYS Tax Analysis — Cannabis (MJ) Scenarios")
        st.info(
            "**IRS §280E** disallows deductions for businesses trafficking in Schedule I substances. "
            "Cannabis (MJ) businesses may only deduct **COGS / variable costs** federally. "
            "**NYS is decoupled** (Tax Law §208(9)(o), eff. 1/1/2023) — all expenses remain deductible in NY."
        )
        tax_rows = []
        for r in mj_results:
            penalty_pct = (r["e280_penalty"] / r["total_revenue"] * 100) if r["total_revenue"] > 0 else 0
            tax_rows.append({
                "Scenario":                        r["name"],
                "Gross Revenue":                   f"${r['total_revenue']:,.0f}",
                "COGS / Var. Costs (fed. deduct.)":f"${r['total_vc']:,.0f}",
                "Fixed / Op. Costs (NYS only)":    f"${r['total_fc']:,.0f}",
                "Fed. Taxable Income":             f"${r['fed_taxable_income']:,.0f}",
                "NYS Taxable Income":              f"${r['nys_taxable_income']:,.0f}",
                "Est. Federal Tax (24%)":          f"${r['fed_tax_est']:,.0f}",
                "Est. NYS Tax (6.85%)":            f"${r['nys_tax_est']:,.0f}",
                "§280E Penalty (extra fed. tax)":  f"${r['e280_penalty']:,.0f}  ({penalty_pct:.1f}% of revenue)",
            })
        st.dataframe(pd.DataFrame(tax_rows), use_container_width=True, hide_index=True)

        # Bar chart: federal vs NYS taxable income
        if HAS_PLOTLY and len(mj_results) > 0:
            mj_names = [r["name"] for r in mj_results]
            fig_tax = go.Figure()
            fig_tax.add_trace(go.Bar(
                name="Fed. Taxable Income (rev − COGS only)",
                x=mj_names,
                y=[r["fed_taxable_income"] for r in mj_results],
                marker_color="#ef5350",
            ))
            fig_tax.add_trace(go.Bar(
                name="NYS Taxable Income (rev − all costs)",
                x=mj_names,
                y=[r["nys_taxable_income"] for r in mj_results],
                marker_color="#42a5f5",
            ))
            fig_tax.add_trace(go.Bar(
                name="§280E Penalty (extra fed. tax)",
                x=mj_names,
                y=[r["e280_penalty"] for r in mj_results],
                marker_color="#ff7043",
            ))
            fig_tax.update_layout(
                barmode="group", yaxis_tickprefix="$",
                yaxis_title="Dollars", height=360,
                legend=dict(orientation="h", y=-0.25),
            )
            fig_tax.add_hline(y=0, line_dash="dash", line_color="gray")
            st.plotly_chart(fig_tax, use_container_width=True)

        st.caption(
            "Federal tax rate: 24% flat (C-corp / illustrative). NYS rate: 6.85% (illustrative marginal rate). "
            "§280E penalty = estimated federal tax under 280E minus what federal tax would be if all costs were deductible. "
            "Consult a licensed CPA for your actual tax obligations."
        )

    # ── Revenue breakdown stacked bar ────────────────────────────────────
    if len(results) > 0 and any(r["total_revenue"] > 0 for r in results):
        st.divider()
        st.markdown("### 🌸 Revenue by Product Stream")
        _stream_colors = {
            "Flower": "#4CAF50", "Pre-rolls": "#FF9800", "Extraction": "#9C27B0",
            "Dry Floral Material (DFM)": "#66BB6A",
            "CBD Biomass / Dry Matter": "#FFA726",
            "Hemp Grain": "#FFCA28",
            "Hemp Fiber": "#8D6E63",
        }
        _all_streams = sorted({s for r in results for s in r["rev_breakdown"].keys()})
        fig_rev = go.Figure()
        for stream in _all_streams:
            fig_rev.add_trace(go.Bar(
                name=stream, x=names,
                y=[r["rev_breakdown"].get(stream, 0) for r in results],
                marker_color=_stream_colors.get(stream, "#90A4AE"),
            ))
        fig_rev.update_layout(barmode="stack", yaxis_tickprefix="$",
                              yaxis_title="Revenue ($)", height=360,
                              legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig_rev, use_container_width=True)

    # ── Downloads ─────────────────────────────────────────────────────────
    st.divider()
    st.markdown("### ⬇ Download Results")
    _csv = summary_df.to_csv(index=False)
    _dc1, _dc2 = st.columns(2)
    with _dc1:
        st.download_button("⬇ Summary (CSV)", data=_csv,
                           file_name="cannabis_economics_summary.csv",
                           mime="text/csv", use_container_width=True)
    with _dc2:
        if HAS_OPENPYXL:
            _ebuf = BytesIO()
            _tax_rows_local = tax_rows if mj_results else []
            with pd.ExcelWriter(_ebuf, engine="openpyxl") as _ew:
                summary_df.to_excel(_ew, index=False, sheet_name="Summary")
                pd.DataFrame(be_rows).to_excel(_ew, index=False, sheet_name="Break-Even")
                if _tax_rows_local:
                    pd.DataFrame(_tax_rows_local).to_excel(_ew, index=False, sheet_name="Tax Analysis (MJ)")
            st.download_button(
                "⬇ Summary (Excel, 2–3 sheets)", data=_ebuf.getvalue(),
                file_name="cannabis_economics_summary.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        else:
            st.caption("Install openpyxl for Excel export.")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE LAYOUT
# ─────────────────────────────────────────────────────────────────────────────

# Disclaimer
st.markdown("""
<div class="disclaimer-box">
<b>⚠️ Important Disclaimer — Please Read Before Using This Tool</b><br><br>
This tool provides <b>general economic guidance only</b> for planning and educational purposes.
<b>These are estimates, not financial projections.</b> Market prices, yields, and costs vary
significantly by operation, season, and market conditions.<br><br>
<b>This tool and its developers assume no responsibility or liability</b> for any financial
decisions, losses, or outcomes arising from use of this tool.
Always consult a <b>licensed accountant, financial advisor, or business advisor</b>
before making investment or operational decisions.
NYS OCM regulations and license fee schedules change — verify all compliance costs
directly with the <b>NY Office of Cannabis Management</b>.
</div>
""", unsafe_allow_html=True)

st.title("💰 NY Cannabis & Hemp Economics Tool")
st.caption("Enterprise budget analysis for licensed NYS cultivators | Based on Ruterbories, Hanchar & Vergara (2025)")

# Soil assessment link banner
if amend_cost_mid is not None:
    st.success(
        f"🌱 **Soil Assessment data detected:** Amendment cost estimate "
        f"**${amend_cost_low:,.0f}–${amend_cost_high:,.0f}** "
        f"({amend_acres:.2f} acres) pre-filled in Fertilizer & Amendments below."
    )

st.divider()

# Add / remove scenario controls
ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([4, 1, 1])
with ctrl_col2:
    if st.button("➕ Add Scenario", use_container_width=True,
                 disabled=st.session_state.econ_n_scenarios >= 5):
        st.session_state.econ_n_scenarios += 1
        st.session_state.econ_results = None
        st.rerun()
with ctrl_col3:
    if st.button("➖ Remove Last", use_container_width=True,
                 disabled=st.session_state.econ_n_scenarios <= 1):
        st.session_state.econ_n_scenarios -= 1
        st.session_state.econ_results = None
        st.rerun()

# ── Upload section ────────────────────────────────────────────────────────────
_ECON_TEMPLATE_COLS = [
    "scenario_name","crop_type","op_type","plant_type",
    "area_sqft","cycles","acres","n_plants","yield_pp","moisture","wage",
    "labor_setup","labor_planting","labor_maintenance","labor_harvest",
    "labor_post","labor_compliance","labor_other",
    "vc_seeds","vc_amendments","vc_crop_prot","vc_water",
    "vc_energy","vc_packaging","vc_testing","vc_other",
    "fc_land","fc_buildings","fc_equipment","fc_licenses","fc_insurance","fc_other",
    "fl_pct","pr_pct","ex_pct","fl_price","pr_price","ex_price",
]
_ECON_DEFAULTS = {
    "crop_type": "Cannabis (MJ)", "op_type": "Outdoor", "plant_type": "Photoperiod",
    "area_sqft": 0.0, "cycles": 1, "acres": 0.0, "n_plants": 0.0,
    "yield_pp": 0.0, "moisture": 82.0, "wage": 20.0,
    "fl_pct": 60.0, "pr_pct": 25.0, "ex_pct": 15.0,
    "fl_price": 400.0, "pr_price": 325.0, "ex_price": 125.0,
}

with st.expander("📂 Upload Scenario Data (CSV or Excel)", expanded=False):
    st.caption(
        "Upload a CSV or Excel file with one scenario per row to pre-populate input fields. "
        "Up to 5 scenarios will be loaded. Download the template below to see the expected format."
    )
    _tmpl_df = pd.DataFrame(columns=_ECON_TEMPLATE_COLS)
    _tmpl_csv = _tmpl_df.to_csv(index=False)
    uc1, uc2 = st.columns(2)
    with uc1:
        st.download_button("⬇ Download CSV Template", data=_tmpl_csv,
                           file_name="economics_template.csv", mime="text/csv",
                           use_container_width=True)
    with uc2:
        if HAS_OPENPYXL:
            _tbuf = BytesIO()
            _tmpl_df.to_excel(_tbuf, index=False, sheet_name="Scenarios")
            st.download_button("⬇ Download Excel Template", data=_tbuf.getvalue(),
                               file_name="economics_template.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               use_container_width=True)

    econ_upload = st.file_uploader("Upload scenario file", type=["csv", "xlsx"],
                                   label_visibility="collapsed")
    if econ_upload is not None:
        try:
            fname = econ_upload.name.lower()
            raw_bytes = econ_upload.read()
            if fname.endswith(".xlsx"):
                _udf = pd.read_excel(BytesIO(raw_bytes), dtype=str)
            else:
                _udf = pd.read_csv(BytesIO(raw_bytes), dtype=str)
            _udf.columns = [c.strip().lower().replace(" ", "_") for c in _udf.columns]
            _udf = _udf.dropna(how="all")
            n_load = min(len(_udf), 5)
            if n_load == 0:
                st.warning("No data rows found in uploaded file.")
            else:
                if st.button(f"▶ Apply {n_load} scenario(s) from file", type="primary"):
                    st.session_state.econ_n_scenarios = n_load
                    for _i, (_idx, _row) in enumerate(list(_udf.iterrows())[:n_load]):
                        _p = f"e{_i}_"
                        def _sv(col, cast=float):
                            val = _row.get(col, "")
                            if pd.isna(val) or str(val).strip() == "":
                                return _ECON_DEFAULTS.get(col, 0.0)
                            try:
                                return cast(str(val).strip())
                            except Exception:
                                return _ECON_DEFAULTS.get(col, 0.0)
                        st.session_state[f"{_p}name"]       = str(_row.get("scenario_name", f"Scenario {_i+1}")).strip() or f"Scenario {_i+1}"
                        st.session_state[f"{_p}crop_type"]  = str(_row.get("crop_type", "Cannabis (MJ)")).strip() or "Cannabis (MJ)"
                        st.session_state[f"{_p}op_type"]    = str(_row.get("op_type", "Outdoor")).strip() or "Outdoor"
                        st.session_state[f"{_p}plant_type"] = str(_row.get("plant_type", "Photoperiod")).strip() or "Photoperiod"
                        for _col in ["area_sqft","acres","n_plants","yield_pp","moisture","wage",
                                     "labor_setup","labor_planting","labor_maintenance","labor_harvest",
                                     "labor_post","labor_compliance","labor_other",
                                     "vc_seeds","vc_amendments","vc_crop_prot","vc_water",
                                     "vc_energy","vc_packaging","vc_testing","vc_other",
                                     "fc_land","fc_buildings","fc_equipment","fc_licenses","fc_insurance","fc_other",
                                     "fl_pct","pr_pct","ex_pct","fl_price","pr_price","ex_price"]:
                            st.session_state[f"{_p}{_col}"] = _sv(_col)
                        st.session_state[f"{_p}cycles"] = int(_sv("cycles", int))
                    st.session_state.econ_results = None
                    st.rerun()
                st.success(f"Found {n_load} scenario row(s). Click the button above to load.")
                st.dataframe(_udf.head(n_load), use_container_width=True, hide_index=True)
        except Exception as _e:
            st.error(f"Could not parse file: {_e}")

n = st.session_state.econ_n_scenarios
tab_labels = [f"📋 Scenario {i+1}" for i in range(n)] + ["📊 Summary & Charts"]
tabs = st.tabs(tab_labels)

for i in range(n):
    with tabs[i]:
        render_scenario(i)

with tabs[-1]:
    st.markdown("## 📊 Summary & Analysis")
    calc_btn = st.button("▶ Calculate All Scenarios", type="primary", use_container_width=True)
    if calc_btn:
        with st.spinner("Calculating…"):
            st.session_state.econ_results = [compute_scenario(i) for i in range(n)]
    if st.session_state.econ_results:
        render_summary(st.session_state.econ_results)
    else:
        st.info("Fill in your scenario data in the tabs above, then click **Calculate All Scenarios**.")

st.divider()
st.caption(
    "Cannabis price references: NYS OCM market reports & Cannabis Benchmarks (2024–25) · "
    "Cannabis cost structure: adapted from Ruterbories, Hanchar & Vergara (2025) · "
    "Hemp enterprise budgets: Bader (Univ. of Kentucky, 2021) · "
    "Hemp marketing & economics: UK Hemp Tool (hemp.mgcafe.uky.edu/marketing-economics) · "
    "This tool is for planning purposes only."
)
