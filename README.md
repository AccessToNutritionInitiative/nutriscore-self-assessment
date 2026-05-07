# Nutrition Self-Assessment

A web application built for the [Access to Nutrition Initiative (ATNi)](https://accesstonutrition.org/) to help food and beverage SMEs assess and improve their nutrition practices.

The project bundles three tools behind a single FastAPI backend and a Streamlit UI:

- **Nutrition Self-Assessment.** A multi-topic questionnaire (Management & Products, Marketing, Workforce, Labeling, Engagement) that scores company practices. The entire questionnaire — questions, scoring rules, and recommendations — is data-driven from `survey.json`. See [SURVEY.md](SURVEY.md) to learn how to customize it.
- **Nutri-Score Calculator.** Computes the [Nutri-Score](https://www.santepubliquefrance.fr/determinants-de-sante/nutrition-et-activite-physique/articles/nutri-score) of a product from its nutrient composition. Single-product entry and bulk CSV upload are both supported.
- **Health Star Rating Calculator.** Same idea, for the [Health Star Rating](https://www.healthstarrating.gov.au/) system.

## Getting started

**Prerequisites:** [uv](https://docs.astral.sh/uv/) and [just](https://just.systems/)

```bash
just init       # install dependencies
just dev        # start the API (http://localhost:8000)
just ui         # start the UI  (http://localhost:8501)
```


Run `just` with no arguments to see the full list of recipes (tests, formatting, type-check, production deploy).

Alternatively, the project also ships as a Docker stack. Copy `.env.template` to `.env` and set `DOMAIN=localhost`, then:

```bash
docker compose up --build
```

The UI is served at http://nutricheck.localhost and the API at http://nutriapi.localhost.

## Production

The application runs on a Hostinger VPS behind [Traefik](https://traefik.io/) (automatic HTTPS via Let's Encrypt), with [Watchtower](https://containrrr.dev/watchtower/) auto-updating containers from this repo's `ghcr.io` images. See the deployment write-up [here](https://theembedding1.substack.com/p/deploy-production-applications-on) for details.
