#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <postgresql-database-url>"
  echo "Example: $0 postgresql://user:pass@host:5432/dbname"
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -f venv/bin/activate ]]; then
  # shellcheck disable=SC1091
  source venv/bin/activate
fi

export DATABASE_URL="$1"

python manage.py migrate --noinput
python manage.py loaddata data/fixtures/food_data.json

echo "PostgreSQL database migrated and seeded from data/fixtures/food_data.json"
