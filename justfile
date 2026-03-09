app := "src/nutri/interface/api/main.py"

default:
    @just --choose

# Sync your local environment with the project
init:
    uv sync

# Start server locally
dev:
    uv run fastapi dev {{app}}

# Run tests
test:
    uv run pytest -vv

# Start UI
ui:
    uv run streamlit run ui/app.py

# Format the codebase
format:
    uvx ruff format .
    uvx ruff check --fix .

# Check Python typing
type-check:
    uvx ty check

# Run before commiting
pre-commit: format type-check
