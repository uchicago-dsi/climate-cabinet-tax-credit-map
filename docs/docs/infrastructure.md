# Infrastructure & Deployment

The application architecture is implemented differently across development environments:

|  | DEV | PROD |
|---|---|---|
| File Storage | Local File System | Google Cloud Storage |
| Databases | Local Docker Containers | Google Cloud SQL for PostgreSQL |
| Pipeline | Local Docker Container | Google Cloud Run Job |
| Web App | Local Docker Container | Netlify |
| Tileset Server | Mapbox Studio | Mapbox Studio |

## Development

![A diagram of Docker Compose infrastructure](assets/local_infrastructure.svg)

To "deploy" the app locally, a staff member manually builds and runs a Docker Compose application with the pipeline/Django project, PostgreSQL database, and web app as networked services. To ease the development process, pgAdmin is also provided as a sevice to quickly run commands against the database and view records in a GUI. All data files are read from and written to the local file system, which is mounted as a volume in the pipeline container. For more information on running the application in development mode, please consult the **[Getting Started page](/getting-started)**.

## Production

![A diagram of production infrastructure](assets/prod_infrastructure.svg)

To deploy the app in production, a staff member ensures that the `main` branch on GitHub is up-to-date by merging in the latest code. A GitHub Action triggered by the push builds and tags a new Docker image of the project's `pipeline` and then pushes that image to the Google Cloud Project's Artifact Registry.

The staff member then manually triggers a pre-configured Google Cloud Run job. The job pulls the latest tagged Docker image from the registry and runs a container from that image; the default container commands are overriden in order to run all the steps of the pipeline as described above. Read and write requests are made to Cloud SQL, Cloud Storage, and Mapbox Studio in the course of processing.

The push to `main` also triggers a new build of the Next.js app on Netlify simultaneously. A staff member can manually promote this new build to production once the pipeline has finished running. The live instance will query a Cloud SQL database and fetch Mapbox tilesets in response to user search queries.

### Cloud Resources

#### Artifact Registry

`cc-widget-prod-pipeline-repo`. Repository for holding Docker images of the pipeline.

#### Cloud Run

`cc-widget-prod-pipeline`. Cloud Run job that builds and runs the latest image from the `cc-widget-prod-pipeline-repo` as a container, overriding its commands to run all stages of the pipeline. The job instance is configured to use 8GB of memory and 2vCPUs and time out after 24 hours have passed. The job typically completes within one to two hours, however. It authenticates with other Google Cloud services using the `cc-widget-prod-pipeline-service-account` defined below.

#### Cloud SQL

`cc-widget-prod-large-sql`. Cloud SQL instance on Enterprise Edition using PostgreSQL 15. Dedicated core. 2vCPUs. 8GB RAM. 250GB SSD Storage. Stopped and destroyed manually after the pipeline has finished running.

`cc-widget-prod-small-sql`. Cloud SQL instance on Enterprise Edition using PostgreSQL 15. Shared core (db-f1-micro). 1vCPU. 0.6GB RAM. 10GB SSD Storage. Stores data used by the website.

#### Cloud Storage

`cc-widget-product-storage`. Cloud Storage Bucket created with default settings. Holds raw and clean datasets used during pipeline processing.

#### IAM

`cc-widget-prod-pipeline-service-account`. Service account with Cloud Run Admin, Cloud SQL Admin, and Storage Object User permissions.

#### Secret Manager

`DJANGO_SECRET_KEY`. Secret key used by the Django pipeline for common hashing operations.

`MAPBOX_API_TOKEN`. Secret token used by the Django pipeline to create and/or update Mapbox tilesets.

`POSTGRES_PASSWORD`. Password to the "large" PostgreSQL database in Cloud SQL.

`RESIZED_POSTGRES_PASSWORD`. Password to the "small" PostgreSQL database in Cloud SQL.

