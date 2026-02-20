app := "src/nutri/interface/api/main.py"

default:
    @just --choose
    
init:
    uv sync

dev:
    uv run fastapi dev {{app}}

test:
    uv run pytest -vv

ui:
    uv run streamlit run ui/app.py

format:
    uvx ruff format .
    uvx ruff check --fix .

type-check:
    uvx ty check

pre-commit: format type-check