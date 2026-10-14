#!/usr/bin/env bash
# exit on error
set -o errexit

export PYTHONIOENCODING=utf-8
export PYTHONUTF8=1
export LANG=C.UTF-8
export LC_ALL=C.UTF-8

pip install --no-cache-dir -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate --no-input
python auto_migrate_review_columns.py || true
