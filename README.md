# Nutri-Score Self-Assessment

A self-assessment tool for computing the [Nutri-Score](https://www.santepubliquefrance.fr/determinants-de-sante/nutrition-et-activite-physique/articles/nutri-score) and [Health Star Rating](https://www.healthstarrating.gov.au/) of food and beverage products.

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

## Production

The application runs on a VPS, hosted on Hostinger, behind [Traefik](https://traefik.io/) with automatic HTTPS via Let's Encrypt. [Watchtower](https://containrrr.dev/watchtower/) watches for new container images in this Github repository (ghcr.io) and updates the production (ui & api) automatically.

### Accessing the VPS

```bash
ssh atni@<host>
cd projects/nutriscore-self-assessment
```

### Managing production

A `.env.prod` must exist in the project repository in the VPS. Copy the .env.template and fill it with your own credentials.

The following `just` commands are available **on the VPS** only:

```bash
just prod-up     # start (or recreate) all production containers in detached mode
just prod-logs   # tail the production logs
just prod-stop   # stop and remove all production containers
```
