#!/bin/bash

# Log script start
echo "Starting setup script."

# Configure script to exit when any command fails
set -e

# Monitor last executed command
trap 'last_command=$current_command; current_command=$BASH_COMMAND' DEBUG

# Log error message upon script exit
trap '[ $? -eq 1 ] && echo "Pipeline failed."' EXIT

# Parse command line arguments
migrate=false
clean_data=false
load_geos=false
load_associations=false
sync_mapbox=false
run_server=false
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --migrate) migrate=true; shift ;;
        --clean-data) clean_data=true; shift ;;
        --load-geos) load_base_tables=true; shift ;;
        --load-associations) load_associations=true; shift ;;
        --sync-mapbox) sync_mapbox=true; shift ;;
        --run-server) run_server=true; shift ;;
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

# Generate cleaned datasets if indicated
if $clean_data ; then
    echo "Generating geography datasets from raw data files."
    ./manage.py clean_data
fi

# Load cleaned geographies into database if indicated
if $load_geos ; then
    echo "Loading geographies into database."
    ./manage.py load_geos
fi

# Compute and load associations between target and bonus geographies if indicated
if $load_associations ; then
    echo "Loading association table into database."
    ./manage.py load_associations
fi

# Log successful end of database setup
echo "Database setup completed successfully."

# Update Mapbox tilesets to match cleaned geographies if indicated
if $sync_mapbox ; then
    echo "Syncing remote Mapbox tilesets with lastest cleaned geographies."
    ./manage.py sync_tilesets
fi

# Run development server if indicated.
if $run_server ; then
    echo "Running default development server."
    ./manage.py runserver 0.0.0.0:8080
fi
