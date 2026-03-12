import requests
import streamlit as st

API_BASE_URL = "http://localhost:8000"
CATEGORIES = ["1-beverage", "1D-dairy-beverage", "2-food", "2D-dairy-food", "3-fat", "3D-cheese"]
UNSUPPORTED_CATEGORIES = {}
HEALTHY_THRESHOLD = 3.5

def render_stars(rating: float) -> str: 
    full_stars = int(rating)
    half_star = 1 if (rating % 1) == 0.5 else 0
    empty_stars = 5 - full_stars - half_star

    return(
        '<span style = "color: #1b75ba; font-size:2rem;">'
        + "★" * full_stars
        + ("⯪" if half_star else "")
        + '<span style="color: #1b75ba;">☆</span>' * empty_stars
        + "</span>"
    )

st.set_page_config(page_title="Health Star Rating Calculator", page_icon="💫", layout="centered")
st.title("💫 HSR Calculator")
st.caption("Powered by the ATNi HSR API")

tab_single, tab_bulk = st.tabs(["Single Product", "Bulk CSV"])

# ── Single product ─────────────────────────────────────────────────────────────
with tab_single:
    st.subheader("Calculate score for one product")
    st.caption("The values have to be per 100 g")

    is_water = False
    is_unsweeten = False
    disable_inputs = False

    category = st.selectbox(
            "Category",
            CATEGORIES,
            format_func=lambda c: f"{c} — not fully supported yet" if c in UNSUPPORTED_CATEGORIES else c,
        )
    
    with st.expander("How to categorise the products"): 
        st.markdown("""
            Category 1-beverage includes
                    
            Category 1D-beverage includes
                    
            Category 2-food includes all food other than those included in category 1-beverage, 1D-dairy-beverage, 2D-dairy-food, 3-fat or 3D-cheese
                    
            Category 2D-dairy-food includes: 
                * Yoghurts, 
                * Cheeses with calcium content <= 320 mg/100g, 
                * Spoonable dairy foods with <= 25% other non dairy ingredients
                * Dairy foods other than those included in category 1D-dairy-food or 3D-cheese. 
        """)
    
    if category in UNSUPPORTED_CATEGORIES:
        st.warning("This category is not supported yet. Please select other categories.")
    
    if category == "1-beverage": 
        
        water_type = st.radio(
            "Beverage type", 
            options=["Neither", "Water", "Unsweetened but flavored water"],
            index=0,
            help="Selected 'Unsweetened but flavored water' for packaged beverages similar in nutritional profile to water that may contain only, \
                carbon dioxide (added or naturally occurring), \
                permitted flavouring substances (as defined by Standard 1.1.2-2 of the Code), \
                mineral salts at Good Manufacturing Practice (GMP) (Schedule 16 of the Code), \
                additives that provide a specific safety or stability function at GMP (Schedule 16 of the Code).  \
                It **MUST NOT** contain added sugars, sweeteners, colours, sodium, caffeine, quinine, or any other ingredient \
                that contains energy and is not expressly permitted above (e.g. protein)."
        )
        is_water = water_type == "Water"
        is_unsweeten = water_type == "Unsweetened but flavored water"
        disable_inputs = is_water or is_unsweeten
        
    with st.form("single_product_form"):       
        col1, col2 = st.columns(2)
        
        with col1:
            energy_kj = st.number_input("Energy (kJ)", min_value=0.0, value=0.0, step=1.0, disabled=disable_inputs)
            sugar_g = st.number_input("Sugars (g)", min_value=0.0, value=0.0, step=0.1, disabled=disable_inputs)
            satfat_g = st.number_input("Saturated fat (g)", min_value=0.0, value=0.0, step=0.1, disabled=disable_inputs)
            sodium_mg = st.number_input("Sodium (mg)", min_value=0.0, value=0.0, step=0.1, disabled=disable_inputs)
            
        with col2:
            fibre_g = st.number_input("Fibre (g)", min_value=0.0, value=0.0, step=0.1, disabled=disable_inputs)
            protein_g = st.number_input("Protein (g)", min_value=0.0, value=0.0, step=0.1, disabled=disable_inputs)
            fvnl_percent = st.number_input("Fruits, vegetables, nuts and legumes (%)", min_value=0.0, max_value=100.0, value=0.0, step=1.0, disabled=disable_inputs)
            is_concentrated = st.checkbox(
                "Is the fruit and vegetables content concentrated?", 
                disabled=disable_inputs,
                help="Only applies if a product contains solely concentrated fruits or vegetables (including dried), for example dried fruit or tomato paste. \
                Nuts and legumes are specifically excluded from the definition of fruit and vegetables.")

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
            stars_html = render_stars(star_rating)
            
            col_rating, col_healthy = st.columns([1, 2])

            with col_rating: 
                st.markdown(
                    f"""
                    <div style="
                        text-align:center;
                        border-radius:18px;
                        padding:0.4rem 1rem;
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
                if star_rating >= 3.5: 
                    healthy_stat = "Consider healthy"
                else: 
                    healthy_stat = "Considered less healthy"
                st.metric("Healthiness assessment", healthy_stat)
            
                
        except requests.exceptions.ConnectionError:
            st.error("Cannot reach the API. Make sure the server is running on " + API_BASE_URL)
        except requests.exceptions.HTTPError as exc:
            detail = exc.response.json().get("detail", str(exc))
            st.error(f"API error: {detail}")
