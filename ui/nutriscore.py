import json
import os

import pandas as pd
import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
CATEGORIES = ["beverage", "general", "fats"]
UNSUPPORTED_CATEGORIES = {"general", "fats"}
GRADE_COLORS = {
    "A": "#038141",
    "B": "#85BB2F",
    "C": "#FECB02",
    "D": "#EE8100",
    "E": "#E63E11",
}

st.set_page_config(page_title="Nutri-Score Calculator", page_icon="🥗", layout="centered")
st.title("🥗 Nutriscore Calculator")
st.caption("Powered by the ATNi Nutriscore API")

tab_single, tab_bulk = st.tabs(["Single Product", "Bulk CSV"])

# ── Single product ─────────────────────────────────────────────────────────────
with tab_single:
    st.subheader("Calculate score for one product")

    with st.form("single_product_form"):
        col1, col2 = st.columns(2)

        with col1:
            energy_kj = st.number_input("Energy (kJ)", min_value=0.0, value=0.0, step=1.0)
            sugar_g = st.number_input("Sugars (g)", min_value=0.0, value=0.0, step=0.1)
            sat_fat_g = st.number_input("Saturated fat (g)", min_value=0.0, value=0.0, step=0.1)
            salt_g = st.number_input("Salt (g)", min_value=0.0, value=0.0, step=0.01)
            fruit_veg_pct = st.number_input("Fruits & vegetables (%)", min_value=0.0, max_value=100.0, value=0.0, step=1.0)

        with col2:
            fibre_g = st.number_input("Fibre (g)", min_value=0.0, value=0.0, step=0.1)
            protein_g = st.number_input("Protein (g)", min_value=0.0, value=0.0, step=0.1)
            category = st.selectbox(
                "Category",
                CATEGORIES,
                format_func=lambda c: f"{c} — not supported yet" if c in UNSUPPORTED_CATEGORIES else c,
            )
            has_sweeteners = st.checkbox("Contains sweeteners")
            is_water = st.checkbox("Is water")

        if category in UNSUPPORTED_CATEGORIES:
            st.warning("This category is not supported yet. Please select **beverage**.")

        submitted = st.form_submit_button(
            "Calculate Nutri-Score",
            use_container_width=True,
            disabled=category in UNSUPPORTED_CATEGORIES,
        )

    if submitted and category not in UNSUPPORTED_CATEGORIES:
        payload = {
            "energy_kj": energy_kj,
            "sugar_g": sugar_g,
            "sat_fat_g": sat_fat_g,
            "salt_g": salt_g,
            "fruit_veg_pct": fruit_veg_pct,
            "fibre_g": fibre_g,
            "protein_g": protein_g,
            "has_sweeteners": has_sweeteners,
            "is_water": is_water,
            "category": category,
        }
        try:
            response = requests.post(f"{API_BASE_URL}/nutriscore", json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            grade = data["grade"]
            score = data["score"]
            color = GRADE_COLORS.get(grade, "#888888")

            st.markdown("---")
            col_grade, col_score = st.columns([1, 2])
            with col_grade:
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
                    ">{grade}</div>
                    """,
                    unsafe_allow_html=True,
                )
            with col_score:
                st.metric("Nutri-Score points", score)
        except requests.exceptions.ConnectionError:
            st.error("Cannot reach the API. Make sure the server is running on " + API_BASE_URL)
        except requests.exceptions.HTTPError as exc:
            body = exc.response.json()
            if "errors" in body:
                msgs = [f"**{e['field']}**: {e['message']}" for e in body["errors"]]
                st.error("Invalid product data:\n\n" + "\n\n".join(msgs))
            else:
                detail = body.get("detail", str(exc))
                st.error(f"API error: {detail}")

# ── Bulk CSV ───────────────────────────────────────────────────────────────────
with tab_bulk:
    st.subheader("Calculate scores for multiple products")

    st.info(
        "Upload a CSV with the following columns:\n"
        "`energy_kj`, `sugar_g`, `sat_fat_g`, `salt_g`, `fruit_veg_pct`, "
        "`fibre_g`, `protein_g`, `has_sweeteners`, `is_water`, `category`"
    )

    uploaded_file = st.file_uploader("Choose a CSV file (max 5 MB)", type=["csv"], max_upload_size=5)

    if uploaded_file is not None:
        # Preview the uploaded data
        try:
            preview_df = pd.read_csv(uploaded_file)
            st.write(f"**{len(preview_df)} products loaded.**")
            uploaded_file.seek(0)
        except Exception as exc:
            st.error(f"Could not read file: {exc}")
            st.stop()

        if st.button("Calculate Nutri-Scores", use_container_width=True):
            with st.spinner("Sending to API…"):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/nutriscores",
                        files={"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")},
                        timeout=30,
                        stream=True,
                    )
                    response.raise_for_status()

                    results = []
                    for line in response.iter_lines():
                        if not line:
                            continue
                        results.append(json.loads(line))

                    n_errors = sum(1 for r in results if r.get("grade") is None)
                    if n_errors:
                        st.warning(f"**{n_errors} row(s)** could not be scored (invalid data) — they appear with `score=-100` and no grade.")

                    if results:
                        results_df = pd.DataFrame(results)
                        combined_df = pd.concat(
                            [preview_df.reset_index(drop=True), results_df.reset_index(drop=True)],
                            axis=1,
                        )

                        st.success(f"Processed **{len(results)}** products.")
                        csv_bytes = combined_df.to_csv(index=False).encode()
                        st.download_button(
                            "Download results as CSV",
                            data=csv_bytes,
                            file_name="nutriscore_results.csv",
                            mime="text/csv",
                            use_container_width=True,
                        )
                except requests.exceptions.ConnectionError:
                    st.error("Cannot reach the API. Make sure the server is running on " + API_BASE_URL)
                except requests.exceptions.HTTPError as exc:
                    detail = exc.response.json().get("detail", str(exc))
                    st.error(f"API error: {detail}")
