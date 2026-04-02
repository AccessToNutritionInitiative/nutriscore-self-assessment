import os
import requests
import streamlit as st
import pandas as pd
import numpy as np

st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet">
    <style>
        .star-filled {
            font-family: 'Material Symbols Outlined';
            font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 48;
            color: #1b75ba;
        }
        .star-half {
            font-family: 'Material Symbols Outlined';
            font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 48;
            color: #1b75ba;
        }
        .star-empty {
            font-family: 'Material Symbols Outlined';
            font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 48;
            color: #ccc;
        }
    </style>
""",
    unsafe_allow_html=True,
)


def get_stars(rating: float, html: bool = True) -> str:
    full_stars = int(rating)
    half_star = 1 if (rating % 1) == 0.5 else 0
    empty_stars = 5 - full_stars - half_star
    if html:
        full_html = '<span class="material-symbols-outlined" style="color: #1b75ba; font-variation-settings: \'FILL\' 1;">star</span>'
        half_html = '<span class="material-symbols-outlined" style="color: #1b75ba;">star_half</span>'
        empty_html = '<span class="material-symbols-outlined" style="color: #1b75ba;">star</span>'
        return '<span style = "font-size:2rem;">' + full_html * full_stars + (half_html if half_star else "") + empty_html * empty_stars + "</span>"
    return "★" * full_stars + ("⯪" if half_star else "") + "☆" * empty_stars + f" ({rating} / 5.0 stars)"


_TEMPLATE_HEADERS = [
    "product_name",
    "category",
    "energy_kj",
    "sodium_mg",
    "satfat_g",
    "sugar_g",
    "protein_g",
    "fibre_g",
    "fvnl_percent",
    "is_concentrated",
    "is_water",
    "is_unsweeten",
]
_TEMPLATE_EXAMPLE = ["product1", "1-beverage", 250, 5.0, 1.2, 0.3, 10.0, 2.1, 50.0, False, False, False]
TEMPLATE_CSV = "\n".join(
    [
        ",".join(_TEMPLATE_HEADERS),
        ",".join(str(v) for v in _TEMPLATE_EXAMPLE),
    ]
).encode()

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
HSR_PAGE_URL = "https://www.healthstarrating.gov.au/sites/default/files/2025-07/HSR%20System%20Calculator%20and%20Style%20Guide%20v8.1.pdf"
CATEGORIES = ["1-beverage", "1D-dairy-beverage", "2-food", "2D-dairy-food", "3-fat", "3D-cheese"]
UNSUPPORTED_CATEGORIES = {}
HEALTHY_THRESHOLD = 3.5
EXPLAINER_UNSWEETEN = (
    "Selected 'Unsweetened but flavored water' for packaged beverages similar in nutritional profile to water that may contain only \
                        carbon dioxide (added or naturally occurring), \
                        permitted flavouring substances (as defined by Standard 1.1.2-2 of the Code), \
                        mineral salts at Good Manufacturing Practice (GMP) (Schedule 16 of the Code), \
                        additives that provide a specific safety or stability function at GMP (Schedule 16 of the Code).  \
                        It **MUST NOT** contain added sugars, sweeteners, colours, sodium, caffeine, quinine, or any other ingredient \
                        that contains energy and is not expressly permitted above (e.g. protein)."
)
EXPLAINER_CONCENC = (
    "Only applies if a product contains solely concentrated fruits or vegetables (including dried), for example dried fruit or tomato paste. \
                        Nuts and legumes are specifically excluded from the definition of fruit and vegetables."
)
EXPLAINER_CATEGORISE = """
            **Category 1-beverage** includes beverages other dairy beverages, including jellies and water based ice confections.
                    
            **Category 1D-dairy-beverage** includes: 
            - milk and dairy beverages with >= 80 mg calcium/serve (sufficient calcium to meet the requirements for a source of calcium),
            - milk and dairy beverage alternatives derived from legumes that contain no less than 33% m/m protein derived from legumes and have >= 100 mg calcium per 100 ml,
            - milk and dairy beverage alternatives derived from cereals, nuts, seeds, or a combination of those ingredients that contain no less than 0.3% m/m protein derived from cereals, nuts, seeds, 
            or combination of those ingredients, and have >= 100 mg calcium per 100 ml, 
            - milk, dairy beverages, and milk and dairy beverage alternatives, must contain >= 75% dairy or permitted dairy-alternative ingredients. 
                    
            **Category 2-food** includes all food other than those included in category 1-beverage, 1D-dairy-beverage, 2D-dairy-food, 3-fat or 3D-cheese
                    
            **Category 2D-dairy-food** includes:  
            - yoghurt, fermented milk products, cream, dairy desserts and other chilled (but not frozen) dairy products,
            - cheeses with calcium content <= 320 mg/100g (e.g. ricotta, cottage cheese, cream cheese), 
            - cheese alternatives derived from legumes that contain > 15% m/m protein derived from legumes and have a calcium level of <= 320 mg/100 g,
            - yoghurt dairy dessert alternatives derived from legumes that contain > 3.1% m/m protein derived from legumes, 
            - spoonable dairy foods with <= 25% other non dairy ingredients, 
            - dairy foods other than those included in category 1D-dairy-food or 3D-cheese. 
            This category **DOES NOT** include ice cream or alternatives derived from cereals, nuts or seed. These products fall in category 2-food. 

            **Category 3-fat** includes oils and spreads. 

            **Category 3D-cheese** includes: 
            - cheese (including surface ripened cheeses) and processed cheese with a calcium content > 320 mg/100g. Must consist of >= 75% dairy ingredients,
            - cheese alternative derived from legumes that contain no less than 15% m/m protein derived from legumes and have a calcium content > 320 mg/100 g and contain >= 75% permitted dairy-alternative ingredients. 
        """
EXPLAINER_HSR = (
    "The Health Star Rating System is a front-of-pack labelling system that rates overall nutritional profile of packaged foods on a scale of ½ to 5 stars. "
    "**The more stars, the healthier the choice.** \n\n"
    "It is computed from *negative factors* (energy, saturated fat, sugar, sodium) minus *postive factors* (protein, fibre, % content of fruits, vegetables, nuts). "
    "The final score is then mapped to a star rating depending on the product category."    
)

st.set_page_config(page_title="Health Star Rating Calculator", page_icon="💫", layout="centered")
st.title("💫 Health Star Rating Calculator")
st.caption("Powered by the ATNi Nutri API")

with st.expander("What is Health Star Rating?"):
    st.markdown(EXPLAINER_HSR)
    st.link_button("Official HSR page", "https://www.healthstarrating.gov.au")

tab_single, tab_bulk = st.tabs(["Single Product", "Bulk CSV"])

# ── Single product ─────────────────────────────────────────────────────────────
with tab_single:
    st.subheader("Calculate rating for one product")

    is_water = False
    is_unsweeten = False
    disable_inputs = False

    category = st.selectbox(
        "Category",
        CATEGORIES,
        index=None,
        placeholder="Select the HSR category for your product",
        format_func=lambda c: f"{c} — not fully supported yet" if c in UNSUPPORTED_CATEGORIES else c,
    )

    with st.expander("How to categorise the product"):
        st.markdown(EXPLAINER_CATEGORISE)
        st.link_button("For more information", HSR_PAGE_URL)

    if category in UNSUPPORTED_CATEGORIES:
        st.warning("This category is not supported yet. Please select other categories.")

    if category == "1-beverage":
        water_type = st.radio(
            "Beverage type",
            options=["Neither", "Water", "Unsweetened but flavored water"],
            index=0,
            help=EXPLAINER_UNSWEETEN,
        )
        is_water = water_type == "Water"
        is_unsweeten = water_type == "Unsweetened but flavored water"
        disable_inputs = is_water or is_unsweeten

    with st.form("single_product_form"):
        st.caption("The values have to be per 100 g. The default values are zero.")
        col1, col2 = st.columns(2)

        with col1:
            energy_kj = st.number_input("Energy (kJ)", min_value=0.0, value=0.0, step=1.0, disabled=disable_inputs)
            sugar_g = st.number_input("Sugars (g)", min_value=0.0, value=0.0, step=0.1, disabled=disable_inputs)
            satfat_g = st.number_input("Saturated fat (g)", min_value=0.0, value=0.0, step=0.1, disabled=disable_inputs)
            sodium_mg = st.number_input("Sodium (mg)", min_value=0.0, value=0.0, step=0.1, disabled=disable_inputs)

        with col2:
            fibre_g = st.number_input("Fibre (g)", min_value=0.0, value=0.0, step=0.1, disabled=disable_inputs)
            protein_g = st.number_input("Protein (g)", min_value=0.0, value=0.0, step=0.1, disabled=disable_inputs)
            fvnl_percent = st.number_input(
                "Fruits, vegetables, nuts and legumes (%)", min_value=0.0, max_value=100.0, value=0.0, step=1.0, disabled=disable_inputs
            )
            is_concentrated = st.checkbox(
                "Is the fruit and vegetables content concentrated?", disabled=(disable_inputs or category == "1-beverage"), help=EXPLAINER_CONCENC
            )

        submitted = st.form_submit_button(
            "Calculate health star rating",
            width="stretch",
            disabled=category is None or category in UNSUPPORTED_CATEGORIES,
        )

    if submitted and category is not None and category not in UNSUPPORTED_CATEGORIES:
        payload = {
            "energy_kj": energy_kj,
            "sugar_g": sugar_g,
            "satfat_g": satfat_g,
            "sodium_mg": sodium_mg,
            "fvnl_percent": fvnl_percent,
            "fibre_g": fibre_g,
            "protein_g": protein_g,
            "is_concentrated": is_concentrated,
            "is_water": is_water,
            "is_unsweeten": is_unsweeten,
            "category": category,
        }
        try:
            response = requests.post(f"{API_BASE_URL}/hsr", json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            star_rating = data["star_rating"]
            score = data["final_score"]

            st.markdown("---")
            stars_html = get_stars(star_rating)

            col_rating, col_healthy = st.columns([1, 2])

            with col_rating:
                st.markdown(
                    f"""
                    <div style="
                        text-align:center;
                        border-radius:18px;
                        padding:1.1rem 1rem;
                        background-color:#f9f9f9; 
                        border: 1px solid #ddd;
                    ">{stars_html}
                        <div style="
                            font-size:1.2rem;
                            font-weight:bold; 
                            color: #1b75ba;
                            ">{star_rating} / 5.0 stars
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with col_healthy:
                if star_rating >= HEALTHY_THRESHOLD:
                    healthy_stat = "Considered healthy"
                else:
                    healthy_stat = "Considered less healthy"
                st.metric("Healthiness assessment", healthy_stat)
                st.caption("Healthier threshold >= 3.5 stars")

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
    st.subheader("Calculate rating for multiple products")

    st.download_button(
        label="Download template",
        data=TEMPLATE_CSV,
        file_name="hsr_template.csv",
        mime="text/csv",
        width="stretch",
    )
    
    with st.expander("Expected input for each column"):
        st.markdown(
            "| Column | Type | Input | Default |\n"
            "|--------|------|-------|---------|\n"            
            "| `category` | string | `1-beverage`, `1D-dairy-beverage`, `2-food`, `2D-dairy-food`, `3-fat`, `3D-cheese` | *required* |\n"
            "| `energy_kj` | float | 0 – 3700 | *required* |\n"
            "| `sugar_g` | float | 0 – 100 | *required* |\n"
            "| `satfat_g` | float | 0 – 100 | *required except for `1-beverage`* |\n"
            "| `sodium_mg` | float | 0 – 5000 | *required except for `1-beverage`*  |\n"
            "| `protein_g` | float | 0 – 100 | 0 |\n"
            "| `fibre_g` | float | 0 – 100 | 0 |\n"
            "| `fvnl_percent` | float | 0 – 100 | 0 |\n"          
            "| `is_concentrated` | bool | true / false | false |\n"
            "| `is_water` | bool | true / false | false |\n"
            "| `is_unsweeten` | bool | true / false | false |\n"
        )

    st.info(
        "Upload a csv with the following columns: \n\n"
        "`category`, `energy_kj`, `sugar_g`, `satfat_g`, `sodium_mg`, `protein_g`, `fibre_g`, `fvnl_percent`, `is_concentrated`, `is_water`, `is_unsweeten`."
    )

    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"], max_upload_size=5)

    if uploaded_file is not None:
        try:
            preview_df = pd.read_csv(uploaded_file)
            st.write(f"**{len(preview_df)} products loaded** - preview: ")
            st.dataframe(preview_df.head(5), width="stretch")
            uploaded_file.seek(0)
        except Exception as e:
            st.error(f"Could not read file: {e}")
            st.stop()

        if st.button("Calculate health star ratings", width="stretch"):
            with st.spinner("Sending to API..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/hsrs",
                        files={"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")},
                        timeout=30,
                    )
                    response.raise_for_status()

                    results = response.json()

                    n_errors = sum(1 for r in results if r.get("star_rating") is None)
                    if n_errors:
                        st.warning(
                            f"**{n_errors} row(s)** could not be scored (invalid data) — they appear with `final_score=-100` and no star rating."
                        )

                    if results:
                        results_df = pd.DataFrame(results)
                        combined_df = pd.concat(
                            [preview_df.reset_index(drop=True), results_df.reset_index(drop=True)],
                            axis=1,
                        )

                        combined_df["healthy/less healthy"] = np.where(
                            combined_df["star_rating"].isna(), "N/A", np.where(combined_df["star_rating"] >= 3.5, "Healthy", "Less healthy")
                        )
                        to_write_df = combined_df.copy()
                        combined_df["star_rating"] = combined_df["star_rating"].apply(lambda r: get_stars(r, html=False) if pd.notna(r) else "N/A")

                        st.success(f"Processed **{len(results)}** products.")
                        st.dataframe(combined_df.head(5), width="stretch")

                        csv_bytes = to_write_df.to_csv(index=False).encode()
                        st.download_button(
                            "Download results as CSV",
                            data=csv_bytes,
                            file_name="hsr_results.csv",
                            mime="text/csv",
                            width="stretch",
                        )

                except requests.exceptions.ConnectionError:
                    st.error("Cannot reach the API. Make sure the server is running on " + API_BASE_URL)
                except requests.exceptions.HTTPError as e:
                    detail = e.response.json().get("detail", str(e))
                    st.error(f"API error: {detail}")
