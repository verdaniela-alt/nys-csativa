"""
2_Economics.py — NY Cannabis / Hemp Economics Tool
Multi-page Streamlit app page.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd

try:
    import plotly.graph_objects as go
    import plotly.express as px
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

st.set_page_config(
    page_title="Economics | NYS Cannabis Tool",
    page_icon="💰",
    layout="wide",
)

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

    # ── 2. Production & Yield ─────────────────────────────────────────────
    with st.expander("🌿 2. Production & Yield", expanded=True):
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
            n_pl = gv(f"{p}n_plants")
            y_pp = gv(f"{p}yield_pp")
            cyc  = int(gv(f"{p}cycles", 1))
            total_yield = n_pl * y_pp * cyc
            st.metric("Total dry yield / yr (lbs)", f"{total_yield:,.1f}")
        with c4:
            st.number_input("Moisture loss %", min_value=50.0, max_value=95.0,
                            value=82.0, step=1.0, key=f"{p}moisture",
                            help="~82% moisture lost during drying (18% of wet weight remains as dry flower)")

        area = gv(f"{p}area_sqft")
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

        wage2      = gv(f"{p}wage", 20.0)
        total_hrs2 = sum(gv(f"{p}{s}") for _, s in LABOR_TASKS)
        total_lbr2 = wage2 * total_hrs2
        total_vc   = sum(gv(f"{p}{s}") for _, s in VC_KEYS) + total_lbr2

        # ── NYS Excise Tax — Cannabis (MJ) only ───────────────────────────
        _is_mj = st.session_state.get(f"{p}crop_type", "Cannabis (MJ)") == "Cannabis (MJ)"
        if _is_mj:
            ty_vc  = gv(f"{p}n_plants") * gv(f"{p}yield_pp") * int(gv(f"{p}cycles", 1))
            fl_p   = gv(f"{p}fl_price"); pr_p = gv(f"{p}pr_price"); ex_p = gv(f"{p}ex_price")
            fl_pct = gv(f"{p}fl_pct");   pr_pct = gv(f"{p}pr_pct"); ex_pct = gv(f"{p}ex_pct")
            rev_est   = ty_vc * (fl_pct/100*fl_p + pr_pct/100*pr_p + ex_pct/100*ex_p)
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
            flower_pct     = st.number_input("% → Whole Flower",   0.0, 100.0, 60.0, 5.0, key=f"{p}fl_pct")
            preroll_pct    = st.number_input("% → Pre-rolls",      0.0, 100.0, 25.0, 5.0, key=f"{p}pr_pct")
            extraction_pct = st.number_input("% → Extraction/Biomass", 0.0, 100.0, 15.0, 5.0, key=f"{p}ex_pct")
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

        # Live preview
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

    area    = gv(f"{p}area_sqft")
    cycles  = int(gv(f"{p}cycles", 1))
    acres   = gv(f"{p}acres") or (area / 43560)
    n_pl    = gv(f"{p}n_plants")
    y_pp    = gv(f"{p}yield_pp")
    t_yield = n_pl * y_pp * cycles

    wage       = gv(f"{p}wage", 20.0)
    total_hrs  = sum(gv(f"{p}{s}") for _, s in LABOR_TASKS)
    total_lbr  = wage * total_hrs

    vc_vals = {label: gv(f"{p}{s}") for label, s in VC_KEYS}
    total_vc = sum(vc_vals.values()) + total_lbr

    is_mj     = st.session_state.get(f"{p}crop_type", "Cannabis (MJ)") == "Cannabis (MJ)"
    excise_tax = gv(f"{p}vc_excise") if is_mj else 0.0
    total_vc  += excise_tax

    fc_vals = {label: gv(f"{p}{s}") for label, s in FC_KEYS}
    total_fc = sum(fc_vals.values())

    total_costs = total_vc + total_fc

    fl_rev = t_yield * gv(f"{p}fl_pct") / 100 * gv(f"{p}fl_price")
    pr_rev = t_yield * gv(f"{p}pr_pct") / 100 * gv(f"{p}pr_price")
    ex_rev = t_yield * gv(f"{p}ex_pct") / 100 * gv(f"{p}ex_price")
    total_rev = fl_rev + pr_rev + ex_rev

    wt_price  = total_rev / t_yield if t_yield > 0 else 0
    bep_price = total_costs / t_yield if t_yield > 0 else 0
    bep_yield = total_costs / wt_price if wt_price > 0 else 0

    # 280E analysis (MJ only)
    # Federal: only COGS (variable costs) deductible
    # NYS: all expenses deductible (decoupled from 280E since 1/1/2023)
    fed_taxable_income = total_rev - total_vc if is_mj else total_rev - total_costs
    nys_taxable_income = total_rev - total_costs
    fed_tax_est        = max(fed_taxable_income * 0.24, 0) if is_mj else max(fed_taxable_income * 0.24, 0)
    nys_tax_est        = max(nys_taxable_income * 0.0685, 0)
    e280_penalty       = fed_tax_est - max((total_rev - total_costs) * 0.24, 0) if is_mj else 0

    return {
        "name":               st.session_state.get(f"{p}name", f"Scenario {i+1}"),
        "crop_type":          st.session_state.get(f"{p}crop_type", "Cannabis (MJ)"),
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
        "rev_breakdown":      {"Flower": fl_rev, "Pre-rolls": pr_rev, "Extraction": ex_rev},
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
            "Operation":         f"{r['op_type']} {r['plant_type']}",
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

    # Download
    csv_data = pd.DataFrame(kpi_rows).to_csv(index=False)
    st.download_button("⬇ Download Summary (CSV)", data=csv_data,
                       file_name="cannabis_economics_summary.csv", mime="text/csv")
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
        fig_rev = go.Figure()
        for stream, color in [("Flower", "#4CAF50"), ("Pre-rolls", "#FF9800"), ("Extraction", "#9C27B0")]:
            fig_rev.add_trace(go.Bar(
                name=stream, x=names,
                y=[r["rev_breakdown"].get(stream, 0) for r in results],
                marker_color=color,
            ))
        fig_rev.update_layout(barmode="stack", yaxis_tickprefix="$",
                              yaxis_title="Revenue ($)", height=360,
                              legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig_rev, use_container_width=True)


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
    "Price references: NYS OCM market reports & Cannabis Benchmarks (2024–25). "
    "Cost structure: adapted from Ruterbories, Hanchar & Vergara (2025). "
    "This tool is for planning purposes only."
)
