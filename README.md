# Climate Cabinet Tax Credit Map

This project loads a PostGIS database with geographic features regarding tax credit programs.

# Structure

The pipeline is a Django project with specified management commands that load the data. 
It can be run in Docker compose using the docker-compose.yaml file in the `pipeline` folder.
Running `docker compose up` will start a `PostGIS database` container, a `pgadmin` container at localhost:443, and a `Django` app container.
The Django project runs an entrypoint script which runs the management commands which use `Geopandas` to load Geoparquets and store them in PostGIS.

The data is all relatively small, so entire files are loaded in a single sweep.
Batching could be used if it were needed for larger files.

# Quick start

