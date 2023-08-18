#!/bin/bash

# Configure script to exit when any command fails
set -e

# Monitor last executed command
trap 'last_command=$current_command; current_command=$BASH_COMMAND' DEBUG

# Log error message upon script exit
trap '[ $? -eq 1 ] && echo "Pipeline failed."' EXIT

# Parse command line arguments
migrate=false
load_datasets=false
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --migrate) migrate=true; shift ;;
        --load) load_datasets=true; shift ;;
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

# Load data if indicated
if $load_datasets ; then
    echo "Loading geographies into database."
    ./manage.py load_geos

    echo "Loading tax credit programs into database."
    ./manage.py load_programs

    echo "Loading geography metrics into database."
    ./manage.py load_geo_metrics

    echo "All datasets loaded successfully."
fi
