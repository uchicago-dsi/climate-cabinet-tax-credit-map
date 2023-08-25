#! /bin/bash
set -e

rm -rf tax_credit/migrations/0*.py

./setup.sh --migrate --load-geos --load-programs --load-geo-metrics