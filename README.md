# Climate Cabinet - Tax Credit Bonus Map Widget

A full-stack web application allowing local officials to search for tax credit bonuses newly-available under the Inflation Reduction Act (2020) within their state, county, municipality, municipal utility, or rural cooperative. At the time of writing, featured tax credit programs include the Alternative Fuel Refueling Property Credit, Direct Pay Clean Energy Investment Tax Credit, Direct Pay Clean Energy Production Tax Credit, Neighborhood Access and Equity Grant, and Solar for All. Program eligibilty is determined by the presence of a low-income, distressed, energy, and/or Justice 40 community within the jurisdiction, and tax credits can stack if a jurisdiction contains more than one of these "bonus" communities.

The application is not intended to be a standalone website, but a "widget" embedded as an iframe in Climate Cabinet Education's main WordPress site. Decoupling the widget from the site had the benefit of safer and more flexible development. Because the widget's logic and configuration could be updated independently, software engineers external to Climate Cabinet never required elevated permissions or access to core code bases. In addition, engineers were able to take advantage of popular, tried-and-tested JavaScript libraries when designing the front-end rather than work within the system of WordPress plugins.

## Features

Users can:

- Search for a geography by name by typing into an autocomplete box. After a configured debounce period, they will see a dropdown of search results or "No Results Found" based on their search phrase.

- Click on a search result and wait for the web app to process their request. Upon completion, the map zooms to the boundaries of the selected geography and shows the current geography and all of its bonus communities as Mapbox tileset layers. In addition, a summary of the geography, its bonus communities, and eligible programs, along with population counts, are displayed in the sidebar.

- Hover over geographies on the map to view their names.

- Select which tileset layer(s) to view at once by toggling checkboxes in the map control panel.

- Switch between political and satellite base maps using radio buttons in the map control panel.

- Open a full-screen view of the map by clicking on the expand button in the map's upper lefthand corner.


## Application Design

The application has five main components:

### (1) File Storage

A file system used to store raw, cleaned, and test datasets; tileset metadata; etc. It uses the following directory structure:

```
├── clean/
│   ├── geojsonl/
│   ├── geoparquet/
│   └── mapbox/
├── raw/
│   ├── bonus/
│   │   ├── distressed/
│   │   ├── energy/
│   │   ├── justice40/
│   │   └── low_income/
│   ├── census/
│   │   ├── block_groups/
│   │   ├── blocks/
│   │   ├── counties/
│   │   ├── county_subdivisions/
│   │   ├── government_units/
│   │   ├── places/
│   │   ├── states/
│   │   ├── tracts/
│   │   └── zip_codes/
│   └── retail/
└── test/
```

Detailed descriptions of each directory's contents can be found in the documentation.

### (2) Database

A PostgreSQL database. PostgreSQL was chosen as the database engine because it is free and open source with a large and active community of contributors. In addition, it is easy to run both locally as a Docker container and as a service on a cloud platform. The application installs PostgreSQL's PostGIS extension to store multipolygon geometries and run spatial queries and its trigram extension to calculate the relevance of search results.

Two tables are defined:

**`public.tax_credit_geography`**

A table storing geographies available for user search and/or reporting. A unique constraint exists on the combination of the `name`, `fips`, and `geography type` fields.

| Name | Type | Description | Ever Blank or Null? | Example |
|---|---|---|---|---|
| id | bigint | The primary key. | NO | 1760 |
| name | character varying | The geography name. | NO | "LORAIN COUNTY, OHIO" |
| fips | character varying | The FIPS code assigned to the geography, if applicable. | YES, BLANK | 39093 |
| fips_pattern | character varying | Explains how to interpret the FIPS code. | YES, BLANK | "STATE(2) + COUNTY(3)" |
| geography_type | character varying | The type of geography, from a limited set of choices. | NO | "county" |
| population | integer | The estimated population for the geography. | YES, NULL | 312964 |
| population_strategy | character varying | The method used to derive the population estimate. | YES, BLANK | "FIPS Code Match" |
| as_of | date | The date on which the geography's data source became current. | NO | 2020-01-01 |
| published_on | date | The publication date of the geography's data source. | YES, NULL | 2021-02-02 |
| source | text | A citation for the geography's data source. | NO | "2020 TIGER/Line Shapefiles, U.S. Census Bureau" |
| programs | jsonb | A generated field consisting of the tax credit programs the geography qualifies for based on type. Only relevant for bonus geographies. | NO | [] |
| geometry | geometry | The geography boundary as a hex string.  | NO | 01060000206.... |
| name_vector | tsvector | A sorted list of lexemes parsed from the name field. Used to optimize text search. | NO | 'counti':2 'lorain':1 'ohio':3 |

**`public.tax_credit_target_bonus_overlap`**

An association table relating "target" geographies—again, states, counties, municipalities, municipal utilities, and rural cooperatives—with the bonus territories—i.e., distressed, low-income, energy, and Justice40 communities—that spatially intersect with them. Additional metadata includes an estimate of the number of people living in the intersection.

| Name | Field | Description | Ever Blank or Null? | Example |
|---|---|---|---|---|
| id | integer | The primary key. | NO | 4013 |
| target_id | bigint | Foreign key reference to a "target" geography. | NO | 1760 |
| bonus_id | bigint | Foreign key reference to a "bonus" geography (e.g., distressed, low-income, Justice 40, energy communities, etc.). | NO | 5727 |
| population | integer | The number of people estimated to live in the intersection between the target and bonus geographies. | NO | 61390 |
| population_strategy | character varying | The method used to derive the population estimate. | NO | "Population-Weighted Block Group Centroid Spatial Join" |

### (3) Pipeline

The pipeline is a Django application that consists of several standard and custom **[Django management commands](https://docs.djangoproject.com/en/5.0/howto/custom-management-commands/)**. When triggered, a bash script in the pipeline—

1. **Connects to the PostgreSQL Database.** The pipeline attempts to connect to the database. If it fails, it retries on an interval until a maximum number of seconds has elapsed—at which point it throws an error.

2. **Creates New Migrations.**  The pipeline runs `manage.py makemigrations` to detect any changes in the Django ORM models. If a model class has changed, a new migration file is written under the `pipeline/tax_credit/migrations` folder to later move to the updated schema.

3. **Migrates Schemas.** The pipeline runs `manage.py migrate` to apply any newly-detected migration file(s) to the database. The first time the application runs, this operation creates the `tax_credit_geography` and `tax_credit_bonus_target_overlap` tables as well as a custom tsvector index on the `tax_credit_geography.name` column, and installs of the trigram extension. 

4. **Loads and Cleans Input Data Files.** After the tables and indices have been created, the pipeline runs `manage.py clean_data`. This custom command reads raw input files from the configured data store, cleans and standardizes the data to conform to the `tax_credit_geography` table schema described above, and then writes the resulting output geographies to the data store as geoparquet and geojsonl files.

5. **Loads Geographies.** The pipeline then runs `manage.py load_geos`. This custom command reads each cleaned geoparquet file from the data store one by one and bulk inserts its records into the `tax_credit_geography` database table, _ignoring unique constraint violations when they occur_.

6. **Load Associations.** Once the geographies are loaded, the pipeline runs `manage.py load_associations`. This custom command computes spatial intersections between all combinations of target and bonus geography types and estimates the number of persons living in those intersections. The population estimation is achieved by matching geographies on a common state or county FIPS code when possible, or by summing the populations of census block group population-weighted centroids that fall into the intersections. Finally, the association records are mapped to the schema for the `tax_credit_target_bonus_overlap` table outlined above and bulk inserted into the database.

7. **Sync Tilesets.** Finally, the pipeline runs `manage.py sync_tilesets`, which syncs the remote Mapbox tilesets with the tilesets defined by the cleaned geojsonl files and configuration settings. Steps include deleting all pre-existing tileset sources for the given Mapbox account, uploading the geojsonl files as new sources, publishing the sources as new tilesets, and awaiting the completion of the publishing job.

### (4) Web App

A JavaScript-based, **[Next.js](https://nextjs.org/)** web application that reads directly from the database to (a) conduct user geography searches and (b) return reports of available tax credit programs, intersecting bonus communities, and population counts for those geographies. **[Prisma](https://www.prisma.io/)** is used as an ORM and **[Tailwind](https://tailwindcss.com/)** as a CSS framework. Once a geography is selected, the web app requests those geographies' tiles from an external tileset server and displays those tiles on a **[React Map GL](https://visgl.github.io/react-map-gl/)** component with styling.

### (5) Tileset Server

Requesting hundreds of large and complex geometries at once from the database and serializing the result as GeoJSON to be displayed on a map quickly proved to be infeasible. The network transfer time was slow enough to harm the user experience and large states like California required too much memory for the browser. To mitigate these issues, the application renders geographies using tilesets. **[Mapbox](https://docs.mapbox.com/api/overview/)** was selected as the server based on its community support, generous free tier, and integration with popular React component libraries like `react-map-gl`.

## Infrastructure & Deployment

The application design is implemented differently across development environments:

|  | DEV | PROD |
|---|---|---|
| File Storage | Local File System | Google Cloud Storage |
| Database | Local Docker Container | Google Cloud SQL for PostgreSQL |
| Pipeline | Local Docker Container | Google Cloud Run Job |
| Web App | Local Docker Container | Netlify |
| Tileset Server | Mapbox Studio | Mapbox Studio |

### Development

![A diagram of Docker Compose infrastructure](/assets/local_infrastructure.svg)

To "deploy" the app locally, a staff member manually builds and runs a Docker Compose application with the pipeline/Django project, PostgreSQL database, and web app as networked services. To ease the development process, pgAdmin is also provided as a sevice to quickly run commands against the database and view records in a GUI. All data files are read from and written to the local file system, which is mounted as a volume in the pipeline container.

### Production

![A diagram of production infrastructure](/assets/prod_infrastructure.svg)

To deploy the app in production, a staff member ensures that the `main` branch on GitHub is up-to-date by merging in the latest code. A GitHub Action triggered by the push builds and tags a new Docker image of the project's `pipeline` and then pushes that image to the Google Cloud Project's Artifact Registry.

The staff member then manually triggers a pre-configured Google Cloud Run job. The job pulls the latest tagged Docker image from the registry and runs a container from that image; the default container commands are overriden in order to run all the steps of the pipeline as described above. Read and write requests are made to Cloud SQL, Cloud Storage, and Mapbox Studio in the course of processing.

The push to `main` also triggers a new build of the Next.js app on Netlify simultaneously. A staff member can manually promote this new build to production once the pipeline has finished running. The live instance will query the Cloud SQL database and fetches Mapbox tilesets in response to user search queries.


## Local Development

### Dependencies

- Make
- Docker Desktop
- Mapbox

### Setup

1. **Download Environment Files.** Download the `.env.dev` and `.env.test` files from the configured **[Google Cloud Storage bucket location]("")** and then save them under the project's `pipeline` directory. Similarly, download the `.env` file from Cloud Storage and save it under the `dashboard` directory. These files are ignored by Git by default.

2. **Download Data Files.** Download the zipped data file from the same bucket and save it under the root of the project. Unzip the file to create a new `data` directory containing `raw`, `clean`, and `test` subfolders and delete any remaining zip artifacts. The entire `data` directory is also ignored by Git.

3. **Get Test Mapbox API Tokens.**  Create a separate, non-production Mapbox account if you don't already have one (e.g., a personal account).  Log into your account through a web browser and then generate a new secret token with the scopes "tilesets:read", "tilesets:write", and "tilesets:list". Copy your username and token into `.env.dev` and `.env.test` as `MAPBOX_USERNAME="username"` and `MAPBOX_API_TOKEN="secret token"`. Then copy your username and public token value (as listed on your user account page) and save them in your dashboard's `.env` file as `NEXT_PUBLIC_MAPBOX_USERNAME="username"` and `NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN="public token"`, respectively.

4. **Install Make.** Install **[make](https://sites.ualberta.ca/dept/chemeng/AIX-43/share/man/info/C/a_doc_lib/aixprggd/genprogc/make.htm)** for your operating system. On macOS and Windows Subsystem for Linux, which runs on Ubuntu, `make` should be installed by default, which you can verify with `make --version`. If the package is not found, install `build-essential` (e.g., `sudo apt-get install build-essential`) and then reattempt to verify. If you are working on a Windows PC outside of WSL, follow the instructions **[here](https://gist.github.com/evanwill/0207876c3243bbb6863e65ec5dc3f058#make)**.

5. **Install Docker Desktop.**  Follow the instructions **[here](https://docs.docker.com/engine/install/)** to install the latest version of Docker Desktop for your operating system. (The project uses Docker Compose V2.) Then, confirm that Docker has been installed correctly by running `docker --version` in a terminal. Be careful to enable the appropriate distros in Docker Desktop if working in WSL.



### Entrypoints

The project's Makefile provides simple entrypoints for running the application locally as a Docker Compose application. A few simple pointers:

- All of the commands listed below **must be run under the root of the project**.

- Services can be shut down at any point by entering `CTRL-C`.

- The PostgreSQL database's data is persisted as a Docker volume called "pgdata", which is saved as a folder under the project root and ignored by Git. Because the project's Docker containers are run as the root user, you will need to assign yourself ownership of the directory if you'd like to delete or modify it (`sudo chown -R <username> pgdata`).

- For all commands, pgAdmin is provided as a GUI for the PostgreSQL database. To use pgAdmin, navigate to `localhost:443` in a web browser, select `servers` in the dropdown in the lefthand sidebar, and log in with the password `postgres` when prompted. **[Browse tables and query the loaded data](https://www.pgadmin.org/docs/pgadmin4/latest/user_interface.html#user-interface)** using raw SQL statements.

#### Run Full-Stack Application

To run the web app locally for the first time, execute the following two commands in sequence:

```
make run-pipeline-execution
make run-dashboard
```

The first statement executes the Django pipeline while the second starts a Next.js development server and initializes a new Prisma ORM client with the existing database schema to enable direct queries against the database. After the ORM has been set up, you can navigate to `http://localhost:3000` in your browser to begin using the web app.

Subsequent invocations of `make run-pipeline-execution` are unnecessary after the database has been initialized the first time. To run the full-stack application later in the future, simply execute:

```
make run-dashboard
```

#### Run Database

```
make run-database
```

This command builds and runs the PostGIS database and pgAdmin GUI. It is helpful for examining the database and running queries without the overhead of additional Compose services.

#### Develop Pipeline

```
make run-pipeline-interactive
```

This command builds and runs the PostGIS database, pgAdmin GUI, and Django pipeline. The pipeline is run as a live development server in the background, with an attached interactive terminal. Using the terminal, you can run commands and scripts as part of the development process. 

#### Test Pipeline

```
make test-pipeline
```

## Credits

This project is a collaborative effort between **[Climate Cabinet Education](https://climatecabineteducation.org/)** and the **[University of Chicago Data Science Institute](https://11thhourproject.org/)**, with generous support from the **[11th Hour Project](https://11thhourproject.org/)**.