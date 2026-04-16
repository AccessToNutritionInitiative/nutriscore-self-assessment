#!/bin/sh
set -e

DB_PATH="${DB_PATH:-/app/data/nutri.db}"
MIGRATIONS_DIR="${MIGRATIONS_DIR:-/app/migrations}"

mkdir -p "$(dirname "$DB_PATH")"

for migration in "$MIGRATIONS_DIR"/*.sql; do
    [ -e "$migration" ] || continue
    echo "Applying migration: $migration"
    sqlite3 "$DB_PATH" < "$migration"
done

exec "$@"
