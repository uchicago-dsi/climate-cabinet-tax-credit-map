# Climate Cabinet Tax Credit Map

This project loads a PostGIS database with geographic features regarding tax credit programs.

# Structure

The pipeline is a Django project with specified management commands that load the data. 
It can be run in Docker compose using the docker-compose.yaml file in the `pipeline` folder.
Running `docker compose up` will start a `PostGIS database` container, a `pgadmin` container at localhost:443, and a `Django` app container.
The Django project runs an entrypoint script which runs the management commands which use `PyArrow` to load Geoparquets and store them in PostGIS.
The files are large enough that they must be batched using Arrow to avoid substantial memory overhead.

# Quick start - local

Download the data from `https://drive.google.com/drive/folders/1mZkpZ8t6a3VdtKyhO7xZSC6A233zPesN` and save it in a directory titled `data` in the root of the project. 
From the project root, run docker with `docker compose up`.
Navigating to `localhost:443`, selecting `servers`, and logging in with the password `postgres` will allow you to access and query the loaded data.
