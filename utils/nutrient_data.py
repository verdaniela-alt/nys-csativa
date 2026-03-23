"""
nutrient_data.py — Nutrient targets, amendments, and NY soil reference data
for the NY Cannabis/Hemp Soil Assessment Tool.

All targets expressed as Mehlich III equivalents (ppm unless noted).
Modified Morgan values should be converted before comparison:
    P  × 2.2  →  M3 equiv
    K  × 1.2  →  M3 equiv
    (all other nutrients: MM ≈ M3 for practical purposes)
"""

# ── Nutrient targets ────────────────────────────────────────────────────────
# Each dict: name, unit, hemp_min, hemp_max, mj_min, mj_max, note, mm_factor
# mm_factor: multiply raw Modified Morgan value to get Mehlich III equivalent
# input_unit: the unit the target values are expressed in (for display)
# allow_unit_conversion: whether to offer ppm/lbs/kg conversion for this nutrient
NUTRIENTS = [
    dict(name="pH",               unit="—",          hemp_min=6.0,  hemp_max=7.0,  mj_min=6.0,  mj_max=7.0,  note="Target 6.2–6.8 for optimal nutrient availability", mm_factor=1.0, allow_unit_conversion=False),
    dict(name="Organic Matter",   unit="%",           hemp_min=3.0,  hemp_max=8.0,  mj_min=3.0,  mj_max=8.0,  note="Higher OM improves CEC, water-holding, and microbial activity", mm_factor=1.0, allow_unit_conversion=False),
    dict(name="P (Phosphorus)",   unit="ppm",         hemp_min=50,   hemp_max=200,  mj_min=60,   mj_max=200,  note="Mehlich III; MM × 2.2 for equiv.", mm_factor=2.2, allow_unit_conversion=True),
    dict(name="K (Potassium)",    unit="ppm",         hemp_min=150,  hemp_max=350,  mj_min=150,  mj_max=400,  note="Mehlich III; MM × 1.2 for equiv.", mm_factor=1.2, allow_unit_conversion=True),
    dict(name="Ca (Calcium)",     unit="ppm",         hemp_min=1500, hemp_max=5000, mj_min=1500, mj_max=5000, note="Aim for Ca:Mg ratio 5:1 to 8:1", mm_factor=1.0, allow_unit_conversion=True),
    dict(name="Mg (Magnesium)",   unit="ppm",         hemp_min=150,  hemp_max=500,  mj_min=150,  mj_max=500,  note="Deficiency causes interveinal chlorosis", mm_factor=1.0, allow_unit_conversion=True),
    dict(name="S (Sulfur)",       unit="ppm",         hemp_min=10,   hemp_max=50,   mj_min=10,   mj_max=50,   note="Important for terpene and cannabinoid synthesis", mm_factor=1.0, allow_unit_conversion=True),
    dict(name="Zn (Zinc)",        unit="ppm",         hemp_min=1.5,  hemp_max=6.0,  mj_min=2.0,  mj_max=8.0,  note="DTPA extraction; critical for flower and terpene quality", mm_factor=1.0, allow_unit_conversion=True),
    dict(name="Mn (Manganese)",   unit="ppm",         hemp_min=5,    hemp_max=50,   mj_min=5,    mj_max=50,   note="Availability drops above pH 7", mm_factor=1.0, allow_unit_conversion=True),
    dict(name="Fe (Iron)",        unit="ppm",         hemp_min=20,   hemp_max=100,  mj_min=20,   mj_max=100,  note="High Fe can tie up Mn and Zn", mm_factor=1.0, allow_unit_conversion=True),
    dict(name="Cu (Copper)",      unit="ppm",         hemp_min=0.5,  hemp_max=5.0,  mj_min=0.5,  mj_max=5.0,  note="Enzyme cofactor; toxic above 10 ppm", mm_factor=1.0, allow_unit_conversion=True),
    dict(name="B (Boron)",        unit="ppm",         hemp_min=0.5,  hemp_max=2.0,  mj_min=0.5,  mj_max=2.0,  note="HWS extraction; narrow deficiency/toxicity window", mm_factor=1.0, allow_unit_conversion=True),
    dict(name="Na (Sodium)",      unit="ppm",         hemp_min=0,    hemp_max=75,   mj_min=0,    mj_max=50,   note="Excess causes salt stress; MJ more sensitive", mm_factor=1.0, allow_unit_conversion=True),
    dict(name="Al (Aluminum)",    unit="ppm",         hemp_min=0,    hemp_max=50,   mj_min=0,    mj_max=30,   note="Elevated Al indicates low pH; root toxicity risk", mm_factor=1.0, allow_unit_conversion=True),
    dict(name="CEC",              unit="meq/100g",    hemp_min=10,   hemp_max=40,   mj_min=10,   mj_max=40,   note="Also reported as 'Total Exchange Capacity (M.E.)' — same thing", mm_factor=1.0, allow_unit_conversion=False),
    dict(name="Base Saturation Ca%", unit="%",        hemp_min=65,   hemp_max=80,   mj_min=65,   mj_max=80,   note="Ca should dominate cation exchange sites", mm_factor=1.0, allow_unit_conversion=False),
    dict(name="Base Saturation K%",  unit="%",        hemp_min=2,    hemp_max=5,    mj_min=2,    mj_max=5,    note="K% >5 may suppress Mg uptake", mm_factor=1.0, allow_unit_conversion=False),
]

# ── Unit conversion factors to ppm ──────────────────────────────────────────
# Based on standard 2-million lb/acre furrow slice (0–20 cm, bulk density ~1.33 g/cm³)
UNIT_CONVERSIONS = {
    "ppm (mg/kg)":   1.0,
    "lbs / acre":    0.5,     # lbs/acre ÷ 2 = ppm
    "kg / ha":       0.446,   # kg/ha ÷ 2.24 = ppm
}

# ── Lab conversion factors (Modified Morgan → Mehlich III equiv) ─────────────
LAB_FACTORS = {
    "Dairy One (Modified Morgan)": {
        "P (Phosphorus)": 2.2,
        "K (Potassium)":  1.2,
    },
    "Agro-One (Modified Morgan)": {
        "P (Phosphorus)": 2.2,
        "K (Potassium)":  1.2,
    },
    "Logan Labs (Mehlich III)": {},
    "A&L Eastern (Mehlich III)": {},
    "Cornell Nutrient Analysis (Mehlich III)": {},
    "Other / Mehlich III": {},
    "Other / Modified Morgan": {
        "P (Phosphorus)": 2.2,
        "K (Potassium)":  1.2,
    },
}

# ── Amendment recommendations ────────────────────────────────────────────────
# Fields:
#   condition   — what triggers this recommendation
#   amendment   — product name
#   organic     — True = OMRI-listed organic option; False = conventional/synthetic
#   form        — physical form of the product
#   application — how it is applied
#   rate        — typical rate
#   notes       — additional guidance
AMENDMENTS = [
    dict(
        condition="pH < 6.0",
        amendment="Agricultural Lime (calcitic)",
        organic=True,
        form="Powder or pellet",
        application="Broadcast on surface and incorporate; pelletized lime can be applied with a spreader",
        rate="1–3 tons/acre depending on buffering pH and target pH",
        notes="Apply 6 months before planting if possible; re-test soil after 3 months. Calcitic lime raises pH and adds Ca but not Mg.",
        price_low=35,   price_high=200,  price_unit="per ton",
        price_note="Bulk powder $35–70/ton; delivered & spread $80–130/ton; pelletized bagged ~$150–200/ton. Prices vary by region and quantity.",
        cost_acre_low=35, cost_acre_high=210,
    ),
    dict(
        condition="pH > 7.0",
        amendment="Elemental Sulfur",
        organic=True,
        form="Powder or granular",
        application="Broadcast and incorporate into top 6 inches; do not apply to dry soil in hot weather",
        rate="100–500 lbs/acre; adjust based on buffer pH and target",
        notes="Soil bacteria oxidize S to sulfuric acid — effect takes 2–6 months. Best applied fall before spring planting.",
        price_low=200,  price_high=400,  price_unit="per ton",
        price_note="Bulk agricultural sulfur $200–400/ton; bagged (50 lb) ~$0.50–1.00/lb ($1,000–2,000/ton equivalent). Prices surged in 2025.",
        cost_acre_low=10, cost_acre_high=100,
    ),
    dict(
        condition="pH > 7.0 (faster correction)",
        amendment="Ferrous Sulfate",
        organic=False,
        form="Powder or granular (also available as liquid drench)",
        application="Broadcast and water in, or dissolve and apply as soil drench",
        rate="10–20 lbs/acre broadcast; 1–2 oz/gal as drench",
        notes="Faster acting than elemental S but shorter-lasting. Good for in-season correction. Also adds Fe.",
        price_low=0.40, price_high=0.90, price_unit="per lb",
        price_note="Typically $0.40–0.90/lb at farm/garden supply; ~$350–600/ton in bulk. Small quantities available at most farm stores.",
        cost_acre_low=4, cost_acre_high=18,
    ),
    dict(
        condition="P Deficient",
        amendment="Rock Phosphate (soft / colloidal)",
        organic=True,
        form="Powder",
        application="Broadcast and incorporate before planting; works best when mixed into root zone",
        rate="300–600 lbs/acre",
        notes="Slow-release; best at pH < 6.5. Effectiveness increases with mycorrhizal fungi — consider inoculant.",
        price_low=0.35, price_high=0.70, price_unit="per lb",
        price_note="Retail $0.35–0.70/lb (50 lb bag); bulk ~$300–500/ton. Fedco Seeds and Ohio Earth Food are common NE suppliers.",
        cost_acre_low=105, cost_acre_high=420,
    ),
    dict(
        condition="P Deficient (fast correction)",
        amendment="Mono-ammonium Phosphate (MAP 11-52-0)",
        organic=False,
        form="Granular/prill",
        application="Broadcast and incorporate or band-apply near root zone",
        rate="50–150 lbs/acre",
        notes="Fast-acting water-soluble P. Avoid over-application — excess P suppresses mycorrhizae and can lock out Zn.",
        price_low=880,  price_high=1270, price_unit="per ton",
        price_note="US retail $880–1,270/ton (March 2026 USDA data). One of the more expensive fertilizers currently — price elevated due to supply chain pressures.",
        cost_acre_low=22, cost_acre_high=95,
    ),
    dict(
        condition="K Deficient",
        amendment="Greensand (Glauconite)",
        organic=True,
        form="Powder",
        application="Broadcast and incorporate; best applied in fall",
        rate="50–100 lbs/100 sq ft",
        notes="Very slow-release; useful to build long-term K reserves over multiple seasons. Does not provide quick correction.",
        price_low=0.50, price_high=1.20, price_unit="per lb",
        price_note="Typically $0.50–1.20/lb retail (50 lb bag ~$25–60). Widely available at organic farm suppliers in the Northeast.",
        cost_acre_low=0, cost_acre_high=0,
    ),
    dict(
        condition="K Deficient (fast correction)",
        amendment="Potassium Sulfate (SOP, 0-0-50)",
        organic=False,
        form="Granular or powder",
        application="Broadcast and water in, or dissolve in water and drench",
        rate="100–250 lbs/acre",
        notes="Preferred over potassium chloride (KCl/MOP) for cannabis — chloride can reduce terpene quality. SOP also adds sulfur.",
        price_low=750,  price_high=900,  price_unit="per ton",
        price_note="North America SOP ~$750–900/ton (late 2025 data). Bagged retail significantly higher (~$1.50–2.50/lb). OMRI-listed grades available.",
        cost_acre_low=37, cost_acre_high=112,
    ),
    dict(
        condition="Ca Deficient",
        amendment="Gypsum (Calcium Sulfate Dihydrate)",
        organic=True,
        form="Granular or powder",
        application="Broadcast on surface; no incorporation needed — water-soluble",
        rate="500–1000 lbs/acre",
        notes="Does NOT raise pH — ideal when pH is already in target range. Also supplies sulfur and improves structure in clay soils.",
        price_low=30,   price_high=60,   price_unit="per ton",
        price_note="One of the most affordable amendments: $30–60/ton delivered and spread. Widely available in NY from agricultural gypsum suppliers.",
        cost_acre_low=7, cost_acre_high=30,
    ),
    dict(
        condition="Mg Deficient",
        amendment="Dolomitic Lime",
        organic=True,
        form="Powder or pellet",
        application="Broadcast and incorporate; same as calcitic lime",
        rate="1–2 tons/acre",
        notes="Use when BOTH pH and Mg need to be raised. Monitor Ca:Mg ratio — target 5:1 to 8:1. Avoid if pH is already ≥ 6.5.",
        price_low=35,   price_high=180,  price_unit="per ton",
        price_note="Bulk $35–80/ton; delivered $80–130/ton; pelletized bagged $130–180/ton. Similar pricing to calcitic lime.",
        cost_acre_low=35, cost_acre_high=360,
    ),
    dict(
        condition="Mg Deficient (in-season)",
        amendment="Epsom Salt (Magnesium Sulfate)",
        organic=True,
        form="Crystalline powder (dissolves in water)",
        application="Foliar spray (1–2% solution) or soil drench; foliar is fastest uptake",
        rate="10–20 lbs/acre foliar; 25–50 lbs/acre soil drench",
        notes="Fast uptake via foliar. Do not exceed recommended rates — excess Mg competes with Ca and K at root uptake sites.",
        price_low=0.40, price_high=0.90, price_unit="per lb",
        price_note="Agricultural grade $0.40–0.90/lb; bulk ~$400–700/ton. Garden/feed store bags widely available. Food-grade costs more.",
        cost_acre_low=10, cost_acre_high=45,
    ),
    dict(
        condition="S Deficient",
        amendment="Gypsum (Calcium Sulfate)",
        organic=True,
        form="Granular or powder",
        application="Broadcast on surface and water in",
        rate="200–500 lbs/acre",
        notes="Preferred S source — also adds Ca and improves soil structure. Good choice when Ca is also low.",
        price_low=30,   price_high=60,   price_unit="per ton",
        price_note="Same product as for Ca deficiency. $30–60/ton delivered and spread — very cost-effective S source.",
        cost_acre_low=3, cost_acre_high=15,
    ),
    dict(
        condition="Zn Deficient",
        amendment="Zinc Sulfate (36% Zn)",
        organic=False,
        form="Granular or powder (liquid chelate also available)",
        application="Foliar spray (0.5–1 lb/acre in 20–30 gal water) or broadcast soil application",
        rate="5–10 lbs/acre broadcast; 0.5–1 lb/acre foliar",
        notes="Foliar application is the most efficient and fastest correction. Apply at vegetative stage before flowering. High pH reduces soil Zn availability — check pH first.",
        price_low=0.80, price_high=1.60, price_unit="per lb",
        price_note="Retail $0.80–1.60/lb (50 lb bag ~$40–80). Foliar use is very efficient so a single bag covers significant acreage.",
        cost_acre_low=4, cost_acre_high=16,
    ),
    dict(
        condition="Mn Deficient",
        amendment="Manganese Sulfate",
        organic=False,
        form="Powder (foliar) or granular (soil)",
        application="Foliar spray or broadcast and incorporate",
        rate="5–10 lbs/acre broadcast; 1–2 lbs/acre foliar",
        notes="Mn availability drops sharply above pH 7 — consider acidifying amendment if pH is high. Foliar correction is faster for in-season use.",
        price_low=0.80, price_high=1.50, price_unit="per lb",
        price_note="Typically $0.80–1.50/lb retail; $600–900/ton bulk. Available at most farm and garden supply stores.",
        cost_acre_low=4, cost_acre_high=15,
    ),
    dict(
        condition="Fe Deficient",
        amendment="Chelated Iron (EDTA or EDDHA)",
        organic=False,
        form="Liquid or soluble powder",
        application="Foliar spray or drip/drench application; avoid applying to dry foliage in direct sun",
        rate="1–2 lbs/acre foliar",
        notes="EDDHA chelate is more stable at high pH (> 7) than EDTA. Fe deficiency at neutral/high pH is usually pH-induced — address pH first for lasting correction.",
        price_low=3.00, price_high=8.00, price_unit="per lb",
        price_note="Most expensive micronutrient amendment: $3–8/lb depending on chelate type (EDDHA > EDTA). Low use rate (1–2 lb/acre) keeps per-acre cost manageable.",
        cost_acre_low=3, cost_acre_high=16,
    ),
    dict(
        condition="B Deficient",
        amendment="Solubor (20.5% B) or Borax",
        organic=False,
        form="Soluble powder (Solubor) or granular (Borax)",
        application="Foliar spray (Solubor) or broadcast soil application (Borax); foliar preferred for quick correction",
        rate="0.5–1 lb/acre foliar; 1–3 lbs/acre soil broadcast",
        notes="⚠ Very narrow deficiency/toxicity window. Do NOT exceed 3 lbs/acre soil application. Toxic to plants above 5 ppm soil B. Always start at lower end of rate.",
        price_low=1.50, price_high=3.00, price_unit="per lb (Solubor)",
        price_note="Solubor $1.50–3.00/lb; Borax $0.40–0.80/lb. Very low use rates — a small bag goes a long way. Solubor preferred for foliar.",
        cost_acre_low=1, cost_acre_high=3,
    ),
    dict(
        condition="Low Organic Matter (< 3%)",
        amendment="Finished Compost (OMRI-listed preferred)",
        organic=True,
        form="Bulk solid",
        application="Broadcast and incorporate 4–6 inches; or use as surface mulch in no-till systems",
        rate="2–5 tons/acre; repeat annually for 3–5 years to build OM",
        notes="Choose compost with C:N ratio < 20:1 (well-finished). Feeds soil biology, improves CEC and water-holding. Most impactful long-term investment for NY cannabis soils.",
        price_low=30,   price_high=80,   price_unit="per ton",
        price_note="Bulk $30–70/ton; delivered $40–80/ton. At 2–5 tons/acre that is $60–400/acre/year. Local farm compost is often cheaper than commercial.",
        cost_acre_low=60, cost_acre_high=400,
    ),
]

# ── Quick amendment lookup by nutrient status ─────────────────────────────
QUICK_AMEND = {
    "pH":                    {"low": "Agricultural Lime", "high": "Elemental Sulfur or Ferrous Sulfate"},
    "P (Phosphorus)":        {"low": "MAP or Rock Phosphate", "high": "Reduce P inputs; leach if possible"},
    "K (Potassium)":         {"low": "Potassium Sulfate (0-0-50)", "high": "Reduce K inputs"},
    "Ca (Calcium)":          {"low": "Gypsum or Calcitic Lime", "high": "Usually not a concern; check pH"},
    "Mg (Magnesium)":        {"low": "Dolomite or Epsom Salt", "high": "Check K:Mg ratio; reduce Mg inputs"},
    "S (Sulfur)":            {"low": "Gypsum or K-Sulfate", "high": "Rarely toxic; leach excess"},
    "Zn (Zinc)":             {"low": "Zinc Sulfate (foliar preferred)", "high": "Reduce Zn inputs; raise pH"},
    "Mn (Manganese)":        {"low": "Manganese Sulfate; check pH", "high": "Raise pH to reduce availability"},
    "Fe (Iron)":             {"low": "Chelated Fe (EDDHA for high pH)", "high": "Usually not a concern"},
    "Cu (Copper)":           {"low": "Copper Sulfate (foliar)", "high": "Raise pH; avoid copper-based pesticides"},
    "B (Boron)":             {"low": "Solubor foliar @ 0.5–1 lb/ac", "high": "Leach; do not add more B"},
    "Organic Matter":        {"low": "Compost 2–5 tons/acre annually", "high": "N/A"},
    "Na (Sodium)":           {"low": "N/A", "high": "Leach with good-quality water; add Ca (gypsum) to displace Na"},
    "Al (Aluminum)":         {"low": "N/A", "high": "Raise pH with lime — Al toxicity is a pH problem"},
}

# ── NY Soil Reference (25 common series) ─────────────────────────────────────
NY_SOILS = [
    dict(series="Honeoye",    texture="Loam / silt loam",        drainage="Well drained",           hydgrp="B",   ph_range="6.1–7.3", om_range="1.5–4.0", region="Finger Lakes / WNY"),
    dict(series="Lansing",    texture="Silt loam",                drainage="Well drained",           hydgrp="B",   ph_range="6.0–7.3", om_range="1.5–3.5", region="Finger Lakes"),
    dict(series="Mardin",     texture="Gravelly silt loam",       drainage="Mod. well drained",      hydgrp="D",   ph_range="5.5–6.8", om_range="2.0–5.0", region="Hudson Valley / Catskills"),
    dict(series="Volusia",    texture="Channery silt loam",       drainage="Somewhat poorly drained", hydgrp="D",  ph_range="5.0–6.5", om_range="2.5–6.0", region="Southern Tier"),
    dict(series="Erie",       texture="Silt loam",                drainage="Somewhat poorly drained", hydgrp="C",  ph_range="5.5–6.8", om_range="2.5–5.5", region="Lake Erie Plain"),
    dict(series="Cayuga",     texture="Silty clay loam",          drainage="Well drained",           hydgrp="B",   ph_range="6.5–7.8", om_range="1.5–3.5", region="Lake Ontario Plain"),
    dict(series="Palmyra",    texture="Gravelly loam",            drainage="Well drained",           hydgrp="A/B", ph_range="5.8–7.0", om_range="1.0–3.0", region="Lake Ontario Plain"),
    dict(series="Dunkirk",    texture="Fine sandy loam / loam",   drainage="Well drained",           hydgrp="B",   ph_range="6.0–7.3", om_range="1.5–3.5", region="Lake Erie Plain"),
    dict(series="Howard",     texture="Gravelly loam",            drainage="Well drained",           hydgrp="B",   ph_range="5.5–7.0", om_range="1.5–3.5", region="Finger Lakes"),
    dict(series="Collamer",   texture="Silt loam",                drainage="Mod. well drained",      hydgrp="B",   ph_range="6.0–7.5", om_range="2.0–4.0", region="Lake Ontario Plain"),
    dict(series="Chenango",   texture="Gravelly loam",            drainage="Well drained",           hydgrp="B",   ph_range="5.5–6.8", om_range="1.0–3.0", region="Southern Tier / Catskills"),
    dict(series="Lordstown",  texture="Channery silt loam",       drainage="Well drained",           hydgrp="B",   ph_range="5.0–6.5", om_range="2.0–5.0", region="Catskills / Southern Tier"),
    dict(series="Bath",       texture="Channery silt loam",       drainage="Well drained",           hydgrp="B",   ph_range="5.0–6.5", om_range="2.0–5.5", region="Southern Tier"),
    dict(series="Alton",      texture="Gravelly loam",            drainage="Excessively drained",    hydgrp="A",   ph_range="5.5–7.0", om_range="0.5–2.0", region="Mohawk / Hudson valleys"),
    dict(series="Hudson",     texture="Silty clay / clay",        drainage="Well drained",           hydgrp="C",   ph_range="6.5–8.0", om_range="1.5–3.5", region="Hudson Valley"),
    dict(series="Rhinebeck",  texture="Silty clay loam",          drainage="Somewhat poorly drained", hydgrp="C",  ph_range="6.5–7.8", om_range="2.0–4.0", region="Hudson Valley"),
    dict(series="Nassau",     texture="Silty clay loam",          drainage="Well drained (shallow)", hydgrp="D",   ph_range="6.0–7.5", om_range="1.5–3.5", region="Hudson Valley"),
    dict(series="Livingston", texture="Clay / silty clay",        drainage="Poorly drained",         hydgrp="D",   ph_range="6.5–8.0", om_range="2.0–5.0", region="Lake Ontario Plain / WNY"),
    dict(series="Madalin",    texture="Silty clay",               drainage="Poorly drained",         hydgrp="D",   ph_range="6.0–7.5", om_range="3.0–8.0", region="Hudson Valley"),
    dict(series="Scio",       texture="Silt loam",                drainage="Mod. well drained",      hydgrp="C",   ph_range="5.5–6.8", om_range="2.5–5.0", region="Southern Tier"),
    dict(series="Phelps",     texture="Fine sandy loam",          drainage="Mod. well drained",      hydgrp="B/C", ph_range="5.5–7.0", om_range="1.5–3.5", region="Finger Lakes / Lake Ontario Plain"),
    dict(series="Arkport",    texture="Fine sandy loam",          drainage="Well drained",           hydgrp="B",   ph_range="5.5–7.0", om_range="0.5–2.0", region="Finger Lakes"),
    dict(series="Teel",       texture="Fine sandy loam",          drainage="Well drained",           hydgrp="B",   ph_range="5.8–7.2", om_range="1.0–3.0", region="Mohawk Valley"),
    dict(series="Plainfield",  texture="Sand / loamy sand",       drainage="Excessively drained",    hydgrp="A",   ph_range="4.5–6.0", om_range="0.3–1.5", region="Long Island / Hudson Valley"),
    dict(series="Deerfield",   texture="Fine sandy loam",         drainage="Well drained",           hydgrp="A",   ph_range="4.5–6.0", om_range="0.5–2.0", region="Long Island"),
]
