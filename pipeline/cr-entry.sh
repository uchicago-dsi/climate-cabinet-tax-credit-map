#! /bin/bash
set -e

rm -rf tax_credit/migrations/0*.py

# TODO: should maybe have a systematic way of running the server or not
# testing or not, etc.
./setup.sh --migrate --load-geos-test --load-programs --load-geo-metrics && python manage.py runserver

# TODO: this is the actual command
# ./setup.sh --migrate --load-geos --load-programs --load-geo-metrics