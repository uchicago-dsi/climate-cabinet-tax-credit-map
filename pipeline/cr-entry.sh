#! /bin/bash
set -e

rm -rf tax_credit/migrations/0*.py

# TODO: should maybe have a systematic way of running the server or not
./setup.sh --migrate --load-geos --load-programs --load-geo-metrics && python manage.py runserver
# ./setup.sh --migrate --load-geos --load-programs --load-geo-metrics