"""
7_Resources.py — SOP Library download page.
NYS Cannabis & Hemp Grower Tools.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from utils.sidebar import render_sidebar

st.set_page_config(
    page_title="SOP Library | NYS Cannabis Tool",
    page_icon="📋",
    layout="wide",
)
render_sidebar()

# ── Helpers ───────────────────────────────────────────────────────────────────
_BASE = os.path.join(os.path.dirname(__file__), "..", "resources", "SOPs")
_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def _dl(path, label=None):
    """Render a single download button for a .docx file."""
    fname = os.path.basename(path)
    if label is None:
        label = fname.replace(".docx", "").replace("_", " ")
    if os.path.exists(path):
        with open(path, "rb") as f:
            st.download_button(
                label=f"⬇ {label}",
                data=f.read(),
                file_name=fname,
                mime=_MIME,
                use_container_width=True,
            )
    else:
        st.caption(f"_(file not found: {fname})_")


def _section(folder, title, description):
    """Render one category expander with all SOPs inside."""
    files = sorted(f for f in os.listdir(folder) if f.endswith(".docx")) if os.path.isdir(folder) else []
    with st.expander(f"{title}  ·  {len(files)} SOPs", expanded=False):
        st.markdown(f"_{description}_")
        st.write("")
        cols = st.columns(2)
        for i, fname in enumerate(files):
            label = (fname.replace(".docx", "")
                        .replace("_OTHER_STATES", "")
                        .replace("_", " "))
            with cols[i % 2]:
                _dl(os.path.join(folder, fname), label)


# ── Page header ───────────────────────────────────────────────────────────────
st.title("📋 NYS *Cannabis sativa* SOP Library")
st.caption(
    "Standard Operating Procedures for licensed New York State cannabis and hemp operations. "
    "All documents are in Microsoft Word (.docx) format — customize with your business name, "
    "license number, and site-specific details before use."
)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — ADULT-USE CANNABIS SATIVA (OCM)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div style="background:#1a237e;border-radius:8px;padding:12px 20px;margin:24px 0 8px 0;">
  <span style="color:#ffffff;font-size:1.15rem;font-weight:700;">
    🌿 Adult-Use <em>Cannabis sativa</em> SOPs
  </span><br>
  <span style="color:#c5cae9;font-size:0.88rem;">
    Regulated by the NYS Office of Cannabis Management (OCM)
  </span>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background:#fff8e1;border:2px solid #f9a825;border-left:6px solid #e65100;
            border-radius:8px;padding:14px 18px;margin-bottom:16px;font-size:0.9rem;">
<b>⚠️ Disclaimer:</b> These SOPs are <b>generic templates only</b>. They do not constitute
legal, compliance, or regulatory advice. You are solely responsible for ensuring your
procedures meet all applicable <b>NYS OCM</b> requirements. Always have final SOPs
reviewed by a qualified compliance professional before use.
</div>
""", unsafe_allow_html=True)

st.markdown("#### 📑 Master Index")
st.caption("Start here — the Master Index lists all 164 SOPs with cross-references by topic and license type.")
_dl(os.path.join(_BASE, "000_Master_Index_and_Cross_Reference_Guide.docx"),
    "000 Master Index & Cross-Reference Guide")

st.markdown("#### SOP Categories")
_section(
    os.path.join(_BASE, "Cultivation_SOPs"),
    "🌱 Cultivation SOPs",
    "Plant propagation, maintenance, harvesting, pest management, lighting, HVAC, soil health, "
    "outdoor and greenhouse operations, seed production, and regulatory compliance for cultivators.",
)
_section(
    os.path.join(_BASE, "Processing_SOPs"),
    "⚗️ Processing SOPs",
    "Post-harvest handling, drying, curing, trimming, extraction methods (ethanol, CO₂, hydrocarbon, rosin), "
    "concentrate production, edibles, packaging, laboratory testing, and waste disposal.",
)
_section(
    os.path.join(_BASE, "Retail_SOPs"),
    "🏪 Retail SOPs",
    "Dispensary operations, age verification, POS, inventory, cash handling, delivery, "
    "customer service, loss prevention, marketing compliance, and social equity.",
)
_section(
    os.path.join(_BASE, "General_SOPs"),
    "📁 General / Facility-Wide SOPs",
    "Document control, training, personnel hygiene, sanitation, CAPA, recall, safety, "
    "equipment calibration, seed-to-sale tracking, facility access, and license renewal.",
)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — HEMP (AMS / NYS AG & MARKETS)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div style="background:#1b5e20;border-radius:8px;padding:12px 20px;margin:36px 0 8px 0;">
  <span style="color:#ffffff;font-size:1.15rem;font-weight:700;">
    🌾 Hemp SOPs
  </span><br>
  <span style="color:#c8e6c9;font-size:0.88rem;">
    Regulated by USDA Agricultural Marketing Service (AMS) and NYS Department of Agriculture &amp; Markets
  </span>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background:#f1f8e9;border:2px solid #7cb342;border-left:6px solid #33691e;
            border-radius:8px;padding:14px 18px;margin-bottom:16px;font-size:0.9rem;">
<b>⚠️ Disclaimer:</b> These SOPs are <b>generic templates only</b> for licensed hemp
(<em>Cannabis sativa</em> L., ≤0.3% THC) operations. They do not constitute legal, compliance,
or regulatory advice. Hemp regulations differ from adult-use cannabis — always verify against
current <b>USDA AMS</b> and <b>NYS Ag &amp; Markets</b> requirements. Have final SOPs reviewed
by a qualified compliance professional before use.
</div>
""", unsafe_allow_html=True)

_HEMP = os.path.join(_BASE, "Hemp_SOPs")

st.markdown("#### 📑 Hemp Master Index")
st.caption("Cross-reference guide covering all hemp compliance SOPs.")
_dl(os.path.join(_HEMP, "SOP-000_Master_Index_and_Cross_Reference_Guide.docx"),
    "SOP-000 Hemp Master Index & Cross-Reference Guide")

st.markdown("#### Hemp SOP Categories")
_section(
    os.path.join(_HEMP, "NYS_Hemp_SOPs"),
    "🗽 NYS Hemp SOPs",
    "New York State-specific hemp compliance procedures: grower license application, license amendments, "
    "FSA registration, planting reports, pre-harvest sampling and THC testing, post-harvest reporting, "
    "disposal and remediation, monthly and incident reporting, sampling agent certification, and license renewal.",
)
_section(
    os.path.join(_HEMP, "Other_States"),
    "🇺🇸 Other States — Hemp SOPs",
    "Hemp compliance SOPs applicable to states outside New York: DEA laboratory registration, crop insurance, "
    "measurement uncertainty compliance, negligent violation response, hemp-derived product compliance, "
    "sampling protocol best practices, biomass remediation, key participant background checks, "
    "and variety selection and seed documentation.",
)

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "SOP library developed for NYS licensed cannabis and hemp operations. "
    "Generic / white-label format — no Cornell authorship implied. "
    "Compliance with applicable regulations is the sole responsibility of the licensee."
)
