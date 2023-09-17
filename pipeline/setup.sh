#!/bin/bash

# Configure script to exit when any command fails
set -e

echo "Starting setup script."

# Monitor last executed command
trap 'last_command=$current_command; current_command=$BASH_COMMAND' DEBUG

# Log error message upon script exit
trap '[ $? -eq 1 ] && echo "Pipeline failed."' EXIT

# Parse command line arguments
migrate=false
load_geos=false
load_geos_test=false
load_programs=false
load_geo_metrics=false
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --migrate) migrate=true; shift ;;
        --load-geos) load_geos=true; shift ;;
        --load-geos-test) load_geos_test=true; shift ;;
        --load-programs) load_programs=true; shift ;;
        --load-geo-metrics) load_geo_metrics=true; shift ;;
        *) echo "Unknown command line parameter received: $1"; exit 1 ;;
    esac
done

# Wait for database server to accept connections
python wait_for_postgres.py

# Perform model migrations if indicated 
# (WARNING: Defaults to "yes" for all questions)
if $migrate ; then
    echo "Creating database migrations from Django models."
    yes | ./manage.py makemigrations

    echo "Applying migrations to database."
    yes | ./manage.py migrate
fi

# Load geographies if indicated
if $load_geos ; then
    echo "Loading geographies into database."
    ./manage.py load_geos
fi

# Load geographies in testing mode if indicated
if $load_geos_test ; then
    echo "Loading geographies into database."
    ./manage.py load_geos --smoke-test --load-all
fi

# Load tax credit programs if indicated
if $load_programs ; then
    echo "Loading tax credit programs into database."
    ./manage.py load_programs
 
    echo "Loading geography metrics into database."
    ./manage.py load_geo_metrics

    echo "All datasets loaded successfully."
fi

# Load geography metrics if indicated
if $load_geo_metrics ; then
    echo "Loading geography metrics into database."
    ./manage.py load_geo_metrics
fi

# Log successful end of setup
echo "Database setup completed successfully."
