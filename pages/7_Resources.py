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


def _section(folder, prefix, title, description, color):
    """Render one category expander with all SOPs inside."""
    sop_dir = os.path.join(_BASE, folder)
    files = sorted(f for f in os.listdir(sop_dir) if f.endswith(".docx")) if os.path.isdir(sop_dir) else []
    with st.expander(f"{title}  ·  {len(files)} SOPs", expanded=False):
        st.markdown(f"_{description}_")
        st.write("")
        cols = st.columns(2)
        for i, fname in enumerate(files):
            label = fname.replace(".docx", "").replace("_", " ")
            with cols[i % 2]:
                _dl(os.path.join(sop_dir, fname), label)


# ── Page header ───────────────────────────────────────────────────────────────
st.title("📋 NYS Cannabis & Hemp SOP Library")
st.caption(
    "Standard Operating Procedures for licensed New York State cannabis and hemp operations. "
    "All documents are in Microsoft Word (.docx) format — customise with your business name, "
    "license number, and site-specific details before use."
)

st.markdown("""
<div style="background:#fff8e1;border:2px solid #f9a825;border-left:6px solid #e65100;
            border-radius:8px;padding:16px 20px;margin-bottom:20px;font-size:0.92rem;">
<b>⚠️ Disclaimer:</b> These SOPs are <b>generic templates only</b>. They do not constitute
legal, compliance, or regulatory advice. You are solely responsible for ensuring your
procedures meet all applicable <b>NYS OCM</b> requirements. Always have final SOPs
reviewed by a qualified compliance professional before use.
</div>
""", unsafe_allow_html=True)

# ── Master Index ──────────────────────────────────────────────────────────────
st.markdown("### 📑 Master Index")
st.caption("Start here — the Master Index lists all 164 SOPs with cross-references by topic and license type.")
_dl(os.path.join(_BASE, "000_Master_Index_and_Cross_Reference_Guide.docx"),
    "000 Master Index & Cross-Reference Guide")

st.divider()
st.markdown("### SOP Categories")

# ── Category sections ─────────────────────────────────────────────────────────
_section(
    "Cultivation_SOPs", "CULT", "🌱 Cultivation SOPs",
    "Plant propagation, maintenance, harvesting, pest management, lighting, HVAC, soil health, "
    "outdoor and greenhouse operations, seed production, and regulatory compliance for cultivators.",
    "#2e7d32",
)
_section(
    "Processing_SOPs", "PROC", "⚗️ Processing SOPs",
    "Post-harvest handling, drying, curing, trimming, extraction methods (ethanol, CO₂, hydrocarbon, rosin), "
    "concentrate production, edibles, packaging, laboratory testing, and waste disposal.",
    "#1565C0",
)
_section(
    "Retail_SOPs", "RET", "🏪 Retail SOPs",
    "Dispensary operations, age verification, POS, inventory, cash handling, delivery, "
    "customer service, loss prevention, marketing compliance, and social equity.",
    "#6a1b9a",
)
_section(
    "General_SOPs", "GEN", "📁 General / Facility-Wide SOPs",
    "Document control, training, personnel hygiene, sanitation, CAPA, recall, safety, "
    "equipment calibration, seed-to-sale tracking, facility access, and license renewal.",
    "#4e342e",
)

st.divider()
st.caption(
    "SOP library developed for NYS licensed cannabis and hemp operations. "
    "Generic / white-label format — no Cornell authorship implied. "
    "Compliance with NYS OCM regulations is the sole responsibility of the licensee."
)
