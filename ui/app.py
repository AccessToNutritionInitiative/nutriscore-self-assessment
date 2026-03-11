import streamlit as st


pg = st.navigation(
    [
        st.Page(page="nutriscore.py", title="Nutri-Score Calculator", icon="🥗"), 
        st.Page(page="hsr.py", title="Health Star Rating Calculator", icon="💫")
    ]
)
pg.run()