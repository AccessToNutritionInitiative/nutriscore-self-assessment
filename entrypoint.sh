#!/bin/sh
set -e

DB_PATH="${DB_PATH:-/app/data/nutri.db}"
MIGRATIONS_DIR="${MIGRATIONS_DIR:-/app/migrations}"

mkdir -p "$(dirname "$DB_PATH")"

sqlite3 "$DB_PATH" "CREATE TABLE IF NOT EXISTS _migrations (name TEXT PRIMARY KEY);"

for migration in "$MIGRATIONS_DIR"/*.sql; do
    [ -e "$migration" ] || continue
    name=$(basename "$migration")
    already_applied=$(sqlite3 "$DB_PATH" "SELECT 1 FROM _migrations WHERE name='$name';")
    if [ -n "$already_applied" ]; then
        continue
    fi
    echo "Applying migration: $name"
    sqlite3 "$DB_PATH" < "$migration"
    sqlite3 "$DB_PATH" "INSERT INTO _migrations (name) VALUES ('$name');"
done

exec "$@"
