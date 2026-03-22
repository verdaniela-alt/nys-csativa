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
NUTRIENTS = [
    dict(name="pH",          unit="—",         hemp_min=6.0,  hemp_max=7.0,  mj_min=6.0,  mj_max=7.0,  note="Target 6.2–6.8 for optimal nutrient availability", mm_factor=1.0),
    dict(name="Organic Matter", unit="%",       hemp_min=3.0,  hemp_max=8.0,  mj_min=3.0,  mj_max=8.0,  note="Higher OM improves CEC, water-holding, and microbial activity", mm_factor=1.0),
    dict(name="P (Phosphorus)", unit="ppm",     hemp_min=50,   hemp_max=200,  mj_min=60,   mj_max=200,  note="Mehlich III; MM × 2.2 for equiv.", mm_factor=2.2),
    dict(name="K (Potassium)",  unit="ppm",     hemp_min=150,  hemp_max=350,  mj_min=150,  mj_max=400,  note="Mehlich III; MM × 1.2 for equiv.", mm_factor=1.2),
    dict(name="Ca (Calcium)",   unit="ppm",     hemp_min=1500, hemp_max=5000, mj_min=1500, mj_max=5000, note="Aim for Ca:Mg ratio 5:1 to 8:1", mm_factor=1.0),
    dict(name="Mg (Magnesium)", unit="ppm",     hemp_min=150,  hemp_max=500,  mj_min=150,  mj_max=500,  note="Deficiency causes interveinal chlorosis", mm_factor=1.0),
    dict(name="S (Sulfur)",     unit="ppm",     hemp_min=10,   hemp_max=50,   mj_min=10,   mj_max=50,   note="Important for terpene and cannabinoid synthesis", mm_factor=1.0),
    dict(name="Zn (Zinc)",      unit="ppm",     hemp_min=1.5,  hemp_max=6.0,  mj_min=2.0,  mj_max=8.0,  note="DTPA extraction; critical for flower and terpene quality", mm_factor=1.0),
    dict(name="Mn (Manganese)", unit="ppm",     hemp_min=5,    hemp_max=50,   mj_min=5,    mj_max=50,   note="Availability drops above pH 7", mm_factor=1.0),
    dict(name="Fe (Iron)",      unit="ppm",     hemp_min=20,   hemp_max=100,  mj_min=20,   mj_max=100,  note="High Fe can tie up Mn and Zn", mm_factor=1.0),
    dict(name="Cu (Copper)",    unit="ppm",     hemp_min=0.5,  hemp_max=5.0,  mj_min=0.5,  mj_max=5.0,  note="Enzyme cofactor; toxic above 10 ppm", mm_factor=1.0),
    dict(name="B (Boron)",      unit="ppm",     hemp_min=0.5,  hemp_max=2.0,  mj_min=0.5,  mj_max=2.0,  note="HWS extraction; narrow deficiency/toxicity window", mm_factor=1.0),
    dict(name="Na (Sodium)",    unit="ppm",     hemp_min=0,    hemp_max=75,   mj_min=0,    mj_max=50,   note="Excess causes salt stress; MJ more sensitive", mm_factor=1.0),
    dict(name="Al (Aluminum)",  unit="ppm",     hemp_min=0,    hemp_max=50,   mj_min=0,    mj_max=30,   note="Elevated Al indicates low pH; root toxicity risk", mm_factor=1.0),
    dict(name="CEC",            unit="meq/100g",hemp_min=10,   hemp_max=40,   mj_min=10,   mj_max=40,   note="Higher CEC = more nutrient buffering capacity", mm_factor=1.0),
    dict(name="Base Saturation Ca%", unit="%",  hemp_min=65,   hemp_max=80,   mj_min=65,   mj_max=80,   note="Ca should dominate cation exchange sites", mm_factor=1.0),
    dict(name="Base Saturation K%",  unit="%",  hemp_min=2,    hemp_max=5,    mj_min=2,    mj_max=5,    note="K% >5 may suppress Mg uptake", mm_factor=1.0),
]

# ── Lab conversion factors ───────────────────────────────────────────────────
LAB_FACTORS = {
    "Dairy One Modified Morgan": {
        "P (Phosphorus)": 2.2,
        "K (Potassium)":  1.2,
    },
    "Agro-One Modified Morgan": {
        "P (Phosphorus)": 2.2,
        "K (Potassium)":  1.2,
    },
    "Logan Labs (Mehlich III)": {},   # no conversion needed
    "A&L Eastern (Mehlich III)": {},
    "Cornell Nutrient Analysis (Mehlich III)": {},
    "Other / Mehlich III": {},
}

# ── Amendment recommendations ────────────────────────────────────────────────
# Each dict: condition, amendment, rate, notes
AMENDMENTS = [
    dict(condition="pH < 6.0",
         amendment="Agricultural Lime (calcitic)",
         rate="1–3 tons/acre depending on buffering pH and target",
         notes="Apply 6 months before planting if possible; have soil re-tested after 3 months"),
    dict(condition="pH > 7.0",
         amendment="Elemental Sulfur",
         rate="100–500 lbs/acre; adjust based on buffer pH",
         notes="Soil bacteria oxidize S to H₂SO₄; effect takes 2–6 months"),
    dict(condition="pH > 7.0 (fast fix)",
         amendment="Ferrous Sulfate",
         rate="10–20 lbs/acre broadcast, or 1–2 oz/gal drench",
         notes="Faster than elemental S but shorter-lasting; good for in-season correction"),
    dict(condition="P Deficient",
         amendment="Rock Phosphate (soft)",
         rate="300–600 lbs/acre",
         notes="Slow-release; best at pH < 6.5; combine with mycorrhizae inoculant"),
    dict(condition="P Deficient (fast fix)",
         amendment="Mono-ammonium Phosphate (MAP 11-52-0)",
         rate="50–150 lbs/acre",
         notes="Fast-acting; avoid over-application — excess P suppresses mycorrhizae"),
    dict(condition="K Deficient",
         amendment="Greensand (Glauconite)",
         rate="50–100 lbs/100 sq ft (organic)",
         notes="Very slow release; useful to build long-term K reserves"),
    dict(condition="K Deficient (fast fix)",
         amendment="Potassium Sulfate (0-0-50)",
         rate="100–250 lbs/acre",
         notes="Preferred over KCl for cannabis; sulfate form also adds S"),
    dict(condition="Ca Deficient",
         amendment="Gypsum (Calcium Sulfate)",
         rate="500–1000 lbs/acre",
         notes="Does not raise pH; good choice when pH is already in range; also adds S"),
    dict(condition="Mg Deficient",
         amendment="Dolomitic Lime",
         rate="1–2 tons/acre (also raises pH)",
         notes="Use when both pH and Mg need to be raised; monitor Ca:Mg ratio"),
    dict(condition="Mg Deficient (in-season)",
         amendment="Epsom Salt (Magnesium Sulfate)",
         rate="10–20 lbs/acre foliar or 25–50 lbs/acre soil drench",
         notes="Fast uptake; do not over-apply — excess Mg competes with Ca"),
    dict(condition="S Deficient",
         amendment="Gypsum (Calcium Sulfate)",
         rate="200–500 lbs/acre",
         notes="Preferred S source; also improves soil structure in clay soils"),
    dict(condition="Zn Deficient",
         amendment="Zinc Sulfate (36% Zn)",
         rate="5–10 lbs/acre broadcast; 0.5–1 lb/acre foliar",
         notes="Foliar application is most efficient; apply at vegetative stage"),
    dict(condition="Mn Deficient",
         amendment="Manganese Sulfate",
         rate="5–10 lbs/acre broadcast; 1–2 lbs/acre foliar",
         notes="Availability drops at high pH — consider acidifying if pH > 7"),
    dict(condition="Fe Deficient",
         amendment="Chelated Iron (EDTA or EDDHA)",
         rate="1–2 lbs/acre foliar",
         notes="EDDHA more stable at high pH; avoid applying to dry foliage"),
    dict(condition="B Deficient",
         amendment="Solubor (20.5% B) or Borax",
         rate="0.5–1 lb/acre foliar; 1–3 lbs/acre soil",
         notes="Very narrow window — do not exceed 3 lbs/acre soil; toxic above 5 ppm"),
    dict(condition="Low Organic Matter (< 3%)",
         amendment="Compost (finished, OMRI-listed preferred)",
         rate="2–5 tons/acre incorporated",
         notes="Annual applications over 3–5 years to build OM; also feeds soil biology"),
]

# ── Quick amendment lookup by nutrient status ─────────────────────────────
QUICK_AMEND = {
    "pH":           {"low": "Agricultural Lime", "high": "Elemental Sulfur or Ferrous Sulfate"},
    "P":            {"low": "MAP or Rock Phosphate", "high": "Reduce P inputs; leach if possible"},
    "K":            {"low": "Potassium Sulfate (0-0-50)", "high": "Reduce K inputs"},
    "Ca":           {"low": "Gypsum or Calcitic Lime", "high": "Usually not a concern; check pH"},
    "Mg":           {"low": "Dolomite or Epsom Salt", "high": "Check K:Mg ratio; reduce Mg inputs"},
    "S":            {"low": "Gypsum or K-Sulfate", "high": "Rarely toxic; leach excess"},
    "Zn":           {"low": "Zinc Sulfate (foliar preferred)", "high": "Reduce Zn inputs; raise pH"},
    "Mn":           {"low": "Manganese Sulfate; check pH", "high": "Raise pH to reduce availability"},
    "Fe":           {"low": "Chelated Fe (EDDHA for high pH)", "high": "Usually not a concern"},
    "Cu":           {"low": "Copper Sulfate (foliar)", "high": "Raise pH; avoid copper-based pesticides"},
    "B":            {"low": "Solubor foliar @ 0.5–1 lb/ac", "high": "Leach; do not add more B"},
    "Organic Matter": {"low": "Compost 2–5 tons/acre annually", "high": "N/A"},
}

# ── NY Soil Reference (25 common series) ─────────────────────────────────────
NY_SOILS = [
    dict(series="Honeoye",   texture="Loam / silt loam",       drainage="Well drained",          hydgrp="B",  ph_range="6.1–7.3",  om_range="1.5–4.0",  region="Finger Lakes / WNY"),
    dict(series="Lansing",   texture="Silt loam",               drainage="Well drained",          hydgrp="B",  ph_range="6.0–7.3",  om_range="1.5–3.5",  region="Finger Lakes"),
    dict(series="Mardin",    texture="Gravelly silt loam",      drainage="Mod. well drained",     hydgrp="D",  ph_range="5.5–6.8",  om_range="2.0–5.0",  region="Hudson Valley / Catskills"),
    dict(series="Volusia",   texture="Channery silt loam",      drainage="Somewhat poorly drained",hydgrp="D", ph_range="5.0–6.5",  om_range="2.5–6.0",  region="Southern Tier"),
    dict(series="Erie",      texture="Silt loam",               drainage="Somewhat poorly drained",hydgrp="C", ph_range="5.5–6.8",  om_range="2.5–5.5",  region="Lake Erie Plain"),
    dict(series="Cayuga",    texture="Silty clay loam",         drainage="Well drained",          hydgrp="B",  ph_range="6.5–7.8",  om_range="1.5–3.5",  region="Lake Ontario Plain"),
    dict(series="Palmyra",   texture="Gravelly loam",           drainage="Well drained",          hydgrp="A/B",ph_range="5.8–7.0",  om_range="1.0–3.0",  region="Lake Ontario Plain"),
    dict(series="Dunkirk",   texture="Fine sandy loam / loam",  drainage="Well drained",          hydgrp="B",  ph_range="6.0–7.3",  om_range="1.5–3.5",  region="Lake Erie Plain"),
    dict(series="Howard",    texture="Gravelly loam",           drainage="Well drained",          hydgrp="B",  ph_range="5.5–7.0",  om_range="1.5–3.5",  region="Finger Lakes"),
    dict(series="Collamer",  texture="Silt loam",               drainage="Mod. well drained",     hydgrp="B",  ph_range="6.0–7.5",  om_range="2.0–4.0",  region="Lake Ontario Plain"),
    dict(series="Chenango",  texture="Gravelly loam",           drainage="Well drained",          hydgrp="B",  ph_range="5.5–6.8",  om_range="1.0–3.0",  region="Southern Tier / Catskills"),
    dict(series="Lordstown", texture="Channery silt loam",      drainage="Well drained",          hydgrp="B",  ph_range="5.0–6.5",  om_range="2.0–5.0",  region="Catskills / Southern Tier"),
    dict(series="Bath",      texture="Channery silt loam",      drainage="Well drained",          hydgrp="B",  ph_range="5.0–6.5",  om_range="2.0–5.5",  region="Southern Tier"),
    dict(series="Alton",     texture="Gravelly loam",           drainage="Excessively drained",   hydgrp="A",  ph_range="5.5–7.0",  om_range="0.5–2.0",  region="Mohawk / Hudson valleys"),
    dict(series="Hudson",    texture="Silty clay / clay",       drainage="Well drained",          hydgrp="C",  ph_range="6.5–8.0",  om_range="1.5–3.5",  region="Hudson Valley"),
    dict(series="Rhinebeck", texture="Silty clay loam",         drainage="Somewhat poorly drained",hydgrp="C", ph_range="6.5–7.8",  om_range="2.0–4.0",  region="Hudson Valley"),
    dict(series="Nassau",    texture="Silty clay loam",         drainage="Well drained (shallow)", hydgrp="D", ph_range="6.0–7.5",  om_range="1.5–3.5",  region="Hudson Valley"),
    dict(series="Livingston",texture="Clay / silty clay",       drainage="Poorly drained",        hydgrp="D",  ph_range="6.5–8.0",  om_range="2.0–5.0",  region="Lake Ontario Plain / WNY"),
    dict(series="Madalin",   texture="Silty clay",              drainage="Poorly drained",        hydgrp="D",  ph_range="6.0–7.5",  om_range="3.0–8.0",  region="Hudson Valley"),
    dict(series="Scio",      texture="Silt loam",               drainage="Mod. well drained",     hydgrp="C",  ph_range="5.5–6.8",  om_range="2.5–5.0",  region="Southern Tier"),
    dict(series="Phelps",    texture="Fine sandy loam",         drainage="Mod. well drained",     hydgrp="B/C",ph_range="5.5–7.0",  om_range="1.5–3.5",  region="Finger Lakes / Lake Ontario Plain"),
    dict(series="Arkport",   texture="Fine sandy loam",         drainage="Well drained",          hydgrp="B",  ph_range="5.5–7.0",  om_range="0.5–2.0",  region="Finger Lakes"),
    dict(series="Teel",      texture="Fine sandy loam",         drainage="Well drained",          hydgrp="B",  ph_range="5.8–7.2",  om_range="1.0–3.0",  region="Mohawk Valley"),
    dict(series="Plainfield", texture="Sand / loamy sand",      drainage="Excessively drained",   hydgrp="A",  ph_range="4.5–6.0",  om_range="0.3–1.5",  region="Long Island / Hudson Valley"),
    dict(series="Deerfield",  texture="Fine sandy loam",        drainage="Well drained",          hydgrp="A",  ph_range="4.5–6.0",  om_range="0.5–2.0",  region="Long Island"),
]
