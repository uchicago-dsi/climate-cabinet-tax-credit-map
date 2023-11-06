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
load_base_tables=false
load_dependent_tables=false
load_assoc_table=false
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --migrate) migrate=true; shift ;;
        --load-base-tables) load_base_tables=true; shift ;;
        --load-dependent-tables) load_dependent_tables=true; shift ;;
        --load-assoc-table) load_assoc_table=true; shift ;;
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

if $load_base_tables ; then
    echo "Loading base tables into database."
    ./manage.py load_base_tables
fi

if $load_dependent_tables ; then
    echo "Loading dependent tables into database."
    ./manage.py load_dependent_tables
fi

if $load_assoc_table ; then
    echo "Loading association table into database."
    ./manage.py load_assoc_table
fi

# Log successful end of setup
echo "Database setup completed successfully."
