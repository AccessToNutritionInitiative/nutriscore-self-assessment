import pandas as pd
import requests
import streamlit as st

API_BASE_URL = "http://localhost:8000"
CATEGORIES = ["1D-dairy-beverage", "1-beverage", "2-food", "2D-dairy-food", "3-fat", "3D-cheese"]
UNSUPPORTED_CATEGORIES = {"1-beverage"}
RATING = {
    0.5: "#038141",
    1.0: "#85BB2F",
    1.5: "#FECB02",
    2.0: "#EE8100",
    2.5: "#E63E11",
    3.0: "white",
    3.5: "white", 
    4.0: "white", 
    4.5: "yellow", 
    5.0: "green",
}

st.set_page_config(page_title="Health Star Rating Calculator", page_icon="💫", layout="centered")
st.title("💫 HSR Calculator")
st.caption("Powered by the ATNi HSR API")

tab_single, tab_bulk = st.tabs(["Single Product", "Bulk CSV"])

# ── Single product ─────────────────────────────────────────────────────────────
with tab_single:
    st.subheader("Calculate score for one product")
    st.caption("The values have to be per 100 g")

    with st.form("single_product_form"):
        col1, col2 = st.columns(2)

        with col1:
            energy_kj = st.number_input("Energy (kJ)", min_value=0.0, value=0.0, step=1.0)
            sugar_g = st.number_input("Sugars (g)", min_value=0.0, value=0.0, step=0.1)
            satfat_g = st.number_input("Saturated fat (g)", min_value=0.0, value=0.0, step=0.1)
            sodium_mg = st.number_input("Sodium (mg)", min_value=0.0, value=0.0, step=0.1)
            fvnl_percent = st.number_input("Fruits, vegetables, nuts and legumes (%)", min_value=0.0, max_value=100.0, value=0.0, step=1.0)

        with col2:
            fibre_g = st.number_input("Fibre (g)", min_value=0.0, value=0.0, step=0.1)
            protein_g = st.number_input("Protein (g)", min_value=0.0, value=0.0, step=0.1)
            category = st.selectbox(
                "Category",
                CATEGORIES,
                format_func=lambda c: f"{c} — not fully supported yet" if c in UNSUPPORTED_CATEGORIES else c,
            )
            is_concentrated = st.checkbox("Is concentrated")

        if category in UNSUPPORTED_CATEGORIES:
            st.warning("This category is not supported yet. Please select other categories.")

        submitted = st.form_submit_button(
            "Calculate health star rating",
            use_container_width=True,
            disabled=category in UNSUPPORTED_CATEGORIES,
        )

    if submitted and category not in UNSUPPORTED_CATEGORIES:
        payload = {
            "energy_kj": energy_kj,
            "sugar_g": sugar_g,
            "satfat_g": satfat_g,
            "sodium_mg": sodium_mg,
            "fvnl_percent": fvnl_percent,
            "fibre_g": fibre_g,
            "protein_g": protein_g,
            "is_concentrated": is_concentrated,
            "category": category,
        }
        try:
            response = requests.post(f"{API_BASE_URL}/hsr", json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            star_rating = data["star_rating"]
            score = data["final_score"]
            color = RATING.get(star_rating, "#888888")

            st.markdown("---")
            col_rating, col_score = st.columns([1, 2])
            with col_rating:
                st.markdown(
                    f"""
                    <div style="
                        background-color:{color};
                        color:white;
                        font-size:4rem;
                        font-weight:bold;
                        text-align:center;
                        border-radius:12px;
                        padding:0.4rem 1rem;
                    ">{star_rating}</div>
                    """,
                    unsafe_allow_html=True,
                )
            with col_score:
                st.metric("HSR score", score)
        except requests.exceptions.ConnectionError:
            st.error("Cannot reach the API. Make sure the server is running on " + API_BASE_URL)
        except requests.exceptions.HTTPError as exc:
            detail = exc.response.json().get("detail", str(exc))
            st.error(f"API error: {detail}")