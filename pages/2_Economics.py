"""
2_Economics.py — NY Cannabis / Hemp Economics Tool (placeholder)
Multi-page Streamlit app page.

This page will host the economics/enterprise budget tool built separately.
"""

import streamlit as st

st.set_page_config(
    page_title="Economics Tool | NYS Cannabis Tool",
    page_icon="💰",
    layout="wide",
)

st.title("💰 NY Cannabis & Hemp Economics Tool")
st.caption("Enterprise budgets, break-even analysis, and market benchmarks for NY cultivators")

st.divider()

st.info("""
**🚧 Coming Soon**

The Economics Tool is being integrated into this platform.
It will include:

- **Enterprise budget templates** for outdoor hemp (fiber, grain, CBD) and cannabis (adult-use, medical)
- **Break-even analysis** — what yield and price do you need to cover input costs?
- **Input cost calculator** — seeds, amendments, labor, licensing, compliance
- **Market price benchmarks** for NY wholesale and retail
- **Profitability scenarios** — compare cropping systems and scale

Check back soon, or contact your local Cornell Cooperative Extension office for enterprise budget worksheets.
""")

st.divider()

col1, col2 = st.columns(2)
with col1:
    st.markdown("### 📋 Useful Resources")
    st.markdown("""
- [NYS OCM Cannabis Licensing](https://cannabis.ny.gov/licensing)
- [Cornell Small Farms Program](https://smallfarms.cornell.edu)
- [CCE Hemp Program Resources](https://cals.cornell.edu/field-crops/hemp)
- [USDA ERS Cannabis Economics](https://www.ers.usda.gov)
    """)

with col2:
    st.markdown("### 🌱 Try the Soil Assessment Tool")
    st.markdown("""
While the economics tool is being finalized, use the
**Soil Assessment tool** (left sidebar) to evaluate your
field's fertility status and generate amendment recommendations
specific to your licensed NY cannabis or hemp operation.
    """)
    if st.button("→ Go to Soil Assessment", use_container_width=True):
        st.switch_page("pages/1_Soil_Assessment.py")
