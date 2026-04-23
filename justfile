app := "src/nutri/interface/api/main.py"
db_path := env_var_or_default("DB_PATH", "data/nutri.db")

default:
    @just --choose

# Sync your local environment with the project
init:
    uv sync

# Apply SQLite migrations in order
migrate:
    mkdir -p "$(dirname {{db_path}})"
    for f in migrations/*.sql; do echo "Applying $f"; sqlite3 {{db_path}} < "$f"; done

# Start server locally
dev:
    uv run fastapi dev {{app}}

# Run tests
test:
    uv run pytest -vv

# Start UI
ui:
    uv run streamlit run ui/app.py --server.runOnSave true

# Format the codebase
format:
    uvx ruff format .
    uvx ruff check --fix .

# Check Python typing
type-check:
    uvx ty check

# Run before commiting
pre-commit: format type-check test

prod-up:
  docker compose -f compose.yml -f compose.prod.yml --env-file .env.prod up -d

prod-logs:
  docker compose -f compose.yml -f compose.prod.yml --env-file .env.prod logs api -f

prod-stop:
  docker compose -f compose.yml -f compose.prod.yml --env-file .env.prod down
