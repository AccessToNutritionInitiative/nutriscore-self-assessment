# Nutri-Score Self-Assessment

A self-assessment tool for computing the [Nutri-Score](https://www.santepubliquefrance.fr/determinants-de-sante/nutrition-et-activite-physique/articles/nutri-score) of food and beverage products.

It exposes a **FastAPI** backend for score calculation and a **Streamlit** UI for manual entry or bulk CSV processing.

> **Note:** Only the `beverage` category is currently supported.

## Getting started

**Prerequisites:** [uv](https://docs.astral.sh/uv/) and [just](https://just.systems/)

```bash
just init       # install dependencies
just dev        # start the API server  (http://localhost:8000)
just ui         # start the Streamlit UI (http://localhost:8501)
```

### Bulk CSV format

To score multiple products at once, upload a CSV with the following columns:

```
energy_kj, sugar_g, sat_fat_g, salt_g, fruit_veg_pct, fibre_g, protein_g, has_sweeteners, is_water, category
```

See [`tests/data/beverages.csv`](tests/data/beverages.csv) for an example.

## Other commands

```bash
just test        # run tests
just format      # format & lint with ruff
just type-check  # type-check with ty
```
