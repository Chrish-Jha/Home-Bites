#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -f venv/bin/activate ]]; then
  # shellcheck disable=SC1091
  source venv/bin/activate
fi

unset DATABASE_URL

python manage.py dumpdata food --indent 2 -o data/fixtures/food_data.json

echo "Exported SQLite data to data/fixtures/food_data.json"
