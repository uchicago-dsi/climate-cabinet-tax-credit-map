# Architecture

The application has five main components:

## File Storage

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

## Database

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

## Pipeline

The pipeline is a Django application that consists of several standard and custom **[Django management commands](https://docs.djangoproject.com/en/5.0/howto/custom-management-commands/)**. When triggered, a bash script in the pipeline—

1. **Connects to the PostgreSQL Database.** The pipeline attempts to connect to the database. If it fails, it retries on an interval until a maximum number of seconds has elapsed—at which point it throws an error.

2. **Creates New Migrations.**  The pipeline runs `manage.py makemigrations` to detect any changes in the Django ORM models. If a model class has changed, a new migration file is written under the `pipeline/tax_credit/migrations` folder to later move to the updated schema.

3. **Migrates Schemas.** The pipeline runs `manage.py migrate` to apply any newly-detected migration file(s) to the database. The first time the application runs, this operation creates the `tax_credit_geography` and `tax_credit_bonus_target_overlap` tables as well as a custom tsvector index on the `tax_credit_geography.name` column, and installs of the trigram extension. 

4. **Loads and Cleans Input Data Files.** After the tables and indices have been created, the pipeline runs `manage.py clean_data`. This custom command reads raw input files from the configured data store, cleans and standardizes the data to conform to the `tax_credit_geography` table schema described above, and then writes the resulting output geographies to the data store as geoparquet and geojsonl files.

5. **Loads Geographies.** The pipeline then runs `manage.py load_geos`. This custom command reads each cleaned geoparquet file from the data store one by one and bulk inserts its records into the `tax_credit_geography` database table, _ignoring unique constraint violations when they occur_.

6. **Load Associations.** Once the geographies are loaded, the pipeline runs `manage.py load_associations`. This custom command computes spatial intersections between all combinations of target and bonus geography types and estimates the number of persons living in those intersections. The population estimation is achieved by matching geographies on a common state or county FIPS code when possible, or by summing the populations of census block group population-weighted centroids that fall into the intersections. Finally, the association records are mapped to the schema for the `tax_credit_target_bonus_overlap` table outlined above and bulk inserted into the database.

7. **Sync Tilesets.** Finally, the pipeline runs `manage.py sync_tilesets`, which syncs the remote Mapbox tilesets with the tilesets defined by the cleaned geojsonl files and configuration settings. Steps include deleting all pre-existing tileset sources for the given Mapbox account, uploading the geojsonl files as new sources, publishing the sources as new tilesets, and awaiting the completion of the publishing job.

## Web App

A JavaScript-based, **[Next.js](https://nextjs.org/)** web application that reads directly from the database to (a) conduct user geography searches and (b) return reports of available tax credit programs, intersecting bonus communities, and population counts for those geographies. **[Prisma](https://www.prisma.io/)** is used as an ORM and **[Tailwind](https://tailwindcss.com/)** as a CSS framework. Once a geography is selected, the web app requests those geographies' tiles from an external tileset server and displays those tiles on a **[React Map GL](https://visgl.github.io/react-map-gl/)** component with styling.

## Tileset Server

Requesting hundreds of large and complex geometries at once from the database and serializing the result as GeoJSON to be displayed on a map quickly proved to be infeasible. The network transfer time was slow enough to harm the user experience and large states like California required too much memory for the browser. To mitigate these issues, the application renders geographies using tilesets. **[Mapbox](https://docs.mapbox.com/api/overview/)** was selected as the server based on its community support, generous free tier, and integration with popular React component libraries like `react-map-gl`.
