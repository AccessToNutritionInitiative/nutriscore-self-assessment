from pathlib import Path

import streamlit as st

st.sidebar.image(str(Path(__file__).parent / "assets" / "atni.png"))

pg = st.navigation(
    [
        st.Page(page="nutriscore.py", title="Nutri-Score Calculator", icon="🥗"),
        st.Page(page="hsr.py", title="Health Star Rating Calculator", icon="💫"),
    ]
)
pg.run()

st.sidebar.divider()
st.sidebar.caption(
    "**Disclaimer:** This tool is provided for self-assessment purposes only. "
    "Results are not validated and may not accurately reflect official Nutri-Score "
    "or Health Star Rating outcomes. Do not rely on these results for regulatory "
    "compliance or labelling decisions."
)
