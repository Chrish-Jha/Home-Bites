#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput
python manage.py setup_admin

# Free tier has no Shell — seed data on first deploy if database is empty
python manage.py shell -c "
from food.models import Food
import sys
sys.exit(0 if Food.objects.exists() else 1)
" && echo "Database already has data, skipping loaddata." || python manage.py loaddata data/fixtures/food_data.json
