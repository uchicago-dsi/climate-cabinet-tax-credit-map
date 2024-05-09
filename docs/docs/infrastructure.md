# Infrastructure & Deployment

The application design is implemented differently across development environments:

|  | DEV | PROD |
|---|---|---|
| File Storage | Local File System | Google Cloud Storage |
| Database | Local Docker Container | Google Cloud SQL for PostgreSQL |
| Pipeline | Local Docker Container | Google Cloud Run Job |
| Web App | Local Docker Container | Netlify |
| Tileset Server | Mapbox Studio | Mapbox Studio |

## Development

![A diagram of Docker Compose infrastructure](assets/local_infrastructure.svg)

To "deploy" the app locally, a staff member manually builds and runs a Docker Compose application with the pipeline/Django project, PostgreSQL database, and web app as networked services. To ease the development process, pgAdmin is also provided as a sevice to quickly run commands against the database and view records in a GUI. All data files are read from and written to the local file system, which is mounted as a volume in the pipeline container.

## Production

![A diagram of production infrastructure](assets/prod_infrastructure.svg)

To deploy the app in production, a staff member ensures that the `main` branch on GitHub is up-to-date by merging in the latest code. A GitHub Action triggered by the push builds and tags a new Docker image of the project's `pipeline` and then pushes that image to the Google Cloud Project's Artifact Registry.

The staff member then manually triggers a pre-configured Google Cloud Run job. The job pulls the latest tagged Docker image from the registry and runs a container from that image; the default container commands are overriden in order to run all the steps of the pipeline as described above. Read and write requests are made to Cloud SQL, Cloud Storage, and Mapbox Studio in the course of processing.

The push to `main` also triggers a new build of the Next.js app on Netlify simultaneously. A staff member can manually promote this new build to production once the pipeline has finished running. The live instance will query the Cloud SQL database and fetches Mapbox tilesets in response to user search queries.