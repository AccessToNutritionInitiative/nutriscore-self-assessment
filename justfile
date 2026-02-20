app := "src/nutri/interface/api/main.py"

dev:
    uv run fastapi dev {{app}}

test:
    uv run pytest -vv

ui:
    uv run streamlit run ui/app.py