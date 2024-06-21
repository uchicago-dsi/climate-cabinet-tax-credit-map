"""Base settings used throughout the Django project.
"""

# Standard library imports
import os
from pathlib import Path

# Third-party imports
from configurations import Configuration
from distutils.util import strtobool


class BaseConfig(Configuration):
    """Defines configuration settings common across environments."""

    # Define file paths
    BASE_DIR = Path(__file__).parents[3]
    PROJECT_DIR = BASE_DIR / "pipeline"
    TEST_DIR = PROJECT_DIR / "tests"
    STATIC_ROOT = os.path.join(PROJECT_DIR, "staticfiles")
    STATIC_URL = "/static/"

    # Define default model fields
    DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

    # Define default settings for batching and bulk operations
    PQ_CHUNK_SIZE = 1_000
    DB_REPLICATION_CHUNK_SIZE = 10_000
    EXPONENTIAL_SMOOTHING_FACTOR = 0.1
    TARGET_SECONDS_PER_BATCH = 5
    SLOW_LOAD_THRESHOLD_IN_MINUTES = 1

    # Define settings to generate population-weighted centroid datasets
    POPULATION_SERVICE = {
        "island_blk_housing_fpath": "raw/census/blocks/us_island_area_block_housing_2020.csv",
        "island_blk_shapefile_fpath": "raw/census/blocks/tl_2020_**_tabblock20.zip",
        "island_blk_shapefile_crs": "EPSG:4269",
        "island_blk_grp_pop_fpath": "raw/census/block_groups/us_block_group_population_2020.csv",
        "island_blk_grp_shapefile_fpath": "raw/census/block_groups/tl_2020_[6,7][0,6,8,9]_bg.zip",
        "island_blk_grp_shapefile_crs": "EPSG:4269",
        "us_blk_grp_centroids_fpath": "raw/census/block_groups/CenPop2020_Mean_BG.txt",
        "us_blk_grp_centroids_crs": "EPSG:4269",
        "output_centroids_fpath": "raw/census/block_groups/us_block_group_pop_centers_2020.geoparquet",
        "output_centroids_crs": "EPSG:4269",
        "zcta_populations_fpath": "raw/census/zip_codes/us_zcta_population_2020.csv",
        "place_populations_fpath": "raw/census/places/us_place_population_2020.csv",
        "county_subdivision_populations_fpath": "raw/census/county_subdivisions/us_county_subdivision_population_2020.csv",
    }

    # Define settings to process raw datasets
    BUFFER_DEG = -10e-20
    GEOJSONL_DIRECTORY = "clean/geojsonl"
    GEOPARQUET_DIRECTORY = "clean/geoparquet"
    RAW_DATASETS = [
        {
            "name": "counties",
            "as_of": "2020-01-01",
            "geography_type": "county",
            "epsg": 4269,
            "published_on": "2021-02-02",
            "source": "2020 TIGER/Line Shapefiles, U.S. Census Bureau",
            "files": {
                "counties": "raw/census/counties/tl_2020_us_county.zip",
                "state_fips": "raw/census/states/fips_states.csv",
            },
        },
        {
            "name": "distressed communities",
            "as_of": "2022-01-01",
            "geography_type": "distressed",
            "epsg": 4269,
            "published_on": None,
            "source": "Distressed Communities Index (DCI), Economic Innovation Group",
            "files": {
                "distress_scores": "raw/bonus/distressed/DCI-2016-2020-Academic-Non-profit-Government-Scores-Only.xlsx",
                "zctas": "raw/census/zip_codes/tl_2020_us_zcta520.zip",
            },
        },
        {
            "name": "energy communities - coal",
            "as_of": "2023-01-01",
            "geography_type": "energy",
            "epsg": 4269,
            "published_on": "2023-06-15",
            "source": "Interagency Working Group on Coal & Power Plant Communities & Economic Revitalization, National Energy Technology Lab, Department of Energy",
            "files": {
                "coal_communities": "raw/bonus/energy/ira_coal_closure_energy_comm_2023v2.zip",
            },
        },
        {
            "name": "energy communities - fossil fuels",
            "as_of": "2023-01-01",
            "geography_type": "energy",
            "epsg": 4269,
            "published_on": "2023-06-15",
            "source": "Interagency Working Group on Coal & Power Plant Communities & Economic Revitalization, National Energy Technology Lab, Department of Energy",
            "files": {
                "fossil_fuel_communities": "raw/bonus/energy/msa_nmsa_fee_ec_status_2023v2.zip"
            },
        },
        {
            "name": "justice40 communities",
            "as_of": "2019-01-01",
            "geography_type": "justice40",
            "epsg": 4326,
            "published_on": "2022-11-22",
            "source": "Climate and Economic Justice Screening Tool v.1.0, Council on Environmental Quality, Executive Office of the President",
            "files": {"justice40_communities": "raw/bonus/justice40/usa.zip"},
        },
        {
            "name": "low-income communities",
            "as_of": "2020-01-01",
            "geography_type": "low-income",
            "epsg": 4269,
            "published_on": "2023-09-01",
            "source": "NMTC Program, Department of the Treasury",
            "files": {
                "county_fips": "raw/census/counties/fips_counties.csv",
                "low_income_territories": "raw/bonus/low_income/NMTC_LIC_Territory_2020_December_2023.xlsx",
                "low_income_states": "raw/bonus/low_income/NMTC_2016-2020_ACS_LIC_Sept1_2023.xlsb",
                "state_fips": "raw/census/states/fips_states.csv",
                "tracts_2020": "raw/census/tracts/tl_2020_**_tract.zip",
            },
        },
        {
            "name": "municipalities - states",
            "as_of": "2020-01-01",
            "geography_type": "municipality",
            "epsg": 4269,
            "published_on": "2021-02-02",
            "source": "2020 TIGER/Line Shapefiles, U.S. Census Bureau",
            "files": {
                "corrections": "raw/census/government_units/gov_unit_corrections.json",
                "county_fips": "raw/census/counties/fips_counties.csv",
                "county_subdivisions": "raw/census/county_subdivisions/tl_2020_**_cousub.zip",
                "government_units": "raw/census/government_units/Govt_Units_2021_Final.xlsx",
                "places": "raw/census/places/tl_2020_**_place.zip",
                "state_fips": "raw/census/states/fips_states.csv",
            },
        },
        {
            "name": "municipalities - territories",
            "as_of": "2020-01-01",
            "geography_type": "municipality",
            "epsg": 4269,
            "published_on": "2021-02-02",
            "source": "2020 TIGER/Line Shapefiles, U.S. Census Bureau",
            "files": {
                "county_fips": "raw/census/counties/fips_counties.csv",
                "county_subdivisions": "raw/census/county_subdivisions/tl_2020_**_cousub.zip",
                "places": "raw/census/places/tl_2020_**_place.zip",
                "state_fips": "raw/census/states/fips_states.csv",
            },
        },
        {
            "name": "municipal utilities",
            "as_of": "2022-12-09",
            "geography_type": "municipal utility",
            "epsg": 4326,
            "published_on": None,
            "source": "Geospatial Management Office, U.S. Department of Homeland Security",
            "files": {
                "corrected_names": "raw/retail/municipal_utility_name_matches.csv",
                "hinton_iowa": "raw/retail/hinton_municipal_iowa.zip",
                "utilities": "raw/retail/Electric_Retail_Service_Territories.zip",
            },
        },
        {
            "name": "rural cooperatives",
            "as_of": "2022-12-09",
            "geography_type": "rural cooperative",
            "epsg": 4326,
            "published_on": None,
            "source": "Geospatial Management Office, U.S. Department of Homeland Security",
            "files": {
                "utilities": "raw/retail/Electric_Retail_Service_Territories.zip",
            },
        },
        {
            "name": "states",
            "as_of": "2020-01-01",
            "geography_type": "state",
            "epsg": 4269,
            "published_on": "2021-02-02",
            "source": "2020 TIGER/Line Shapefiles, U.S. Census Bureau",
            "files": {
                "states": "raw/census/states/tl_2020_us_state.zip",
            },
        },
    ]

    # Define settings to load geographies and associations into database
    INTERSECTION_AREA_THRESHOLD_DEG = 0.02
    CLEAN_DATASETS = [
        {"name": "counties", "file": "clean/geoparquet/counties.geoparquet"},
        {
            "name": "distressed communities",
            "file": "clean/geoparquet/distressed_communities.geoparquet",
        },
        {
            "name": "energy communities - coal",
            "file": "clean/geoparquet/energy_communities___coal.geoparquet",
        },
        {
            "name": "energy communities - fossil fuels",
            "file": "clean/geoparquet/energy_communities___fossil_fuels.geoparquet",
        },
        {
            "name": "justice40 communities",
            "file": "clean/geoparquet/justice40_communities.geoparquet",
        },
        {
            "name": "low-income communities",
            "file": "clean/geoparquet/low_income_communities.geoparquet",
        },
        {
            "name": "municipalities - states",
            "file": "clean/geoparquet/municipalities___states.geoparquet",
        },
        {
            "name": "municipalities - territories",
            "file": "clean/geoparquet/municipalities___territories.geoparquet",
        },
        {
            "name": "municipal utilities",
            "file": "clean/geoparquet/municipal_utilities.geoparquet",
        },
        {
            "name": "rural cooperatives",
            "file": "clean/geoparquet/rural_cooperatives.geoparquet",
        },
        {"name": "states", "file": "clean/geoparquet/states.geoparquet"},
    ]

    # Define settings to sync cleaned data files with remote Mapbox tilesets
    MAPBOX_TILEJSON_METADATA_FILE = "clean/mapbox/mapbox_tilesets.json"
    MAPBOX_TILESET_PUBLISH_SECONDS_WAIT = 10
    MAPBOX_TILESET_SOURCE_BATCH_SIZE = 10000
    MAPBOX_TILESETS = [
        {
            "formal_name": "cc_counties",
            "display_name": "counties",
            "min_zoom": 3,
            "max_zoom": 10,
            "files": ["clean/geojsonl/counties.geojsonl"],
        },
        {
            "formal_name": "cc_distressed",
            "display_name": "distressed communities",
            "min_zoom": 1,
            "max_zoom": 10,
            "files": ["clean/geojsonl/distressed_communities.geojsonl"],
        },
        {
            "formal_name": "cc_energy",
            "display_name": "energy communities",
            "min_zoom": 1,
            "max_zoom": 10,
            "files": [
                "clean/geojsonl/energy_communities___coal.geojsonl",
                "clean/geojsonl/energy_communities___fossil_fuels.geojsonl",
            ],
        },
        {
            "formal_name": "cc_justice40",
            "display_name": "justice40 communities",
            "min_zoom": 1,
            "max_zoom": 10,
            "files": ["clean/geojsonl/justice40_communities.geojsonl"],
        },
        {
            "formal_name": "cc_low_income",
            "display_name": "low-income communities",
            "min_zoom": 1,
            "max_zoom": 10,
            "files": ["clean/geojsonl/low_income_communities.geojsonl"],
        },
        {
            "formal_name": "cc_municipalities",
            "display_name": "municipalities",
            "min_zoom": 1,
            "max_zoom": 10,
            "files": [
                "clean/geojsonl/municipalities___states.geojsonl",
                "clean/geojsonl/municipalities___territories.geojsonl",
            ],
        },
        {
            "formal_name": "cc_municipal_utils",
            "display_name": "municipal utilities",
            "min_zoom": 1,
            "max_zoom": 10,
            "files": ["clean/geojsonl/municipal_utilities.geojsonl"],
        },
        {
            "formal_name": "cc_rural_cooperatives",
            "display_name": "rural cooperatives",
            "min_zoom": 1,
            "max_zoom": 5,
            "files": ["clean/geojsonl/rural_cooperatives.geojsonl"],
        },
        {
            "formal_name": "cc_states",
            "display_name": "states",
            "min_zoom": 1,
            "max_zoom": 5,
            "files": ["clean/geojsonl/states.geojsonl"],
        },
    ]

    # Installed apps
    INSTALLED_APPS = (
        # Default
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        # Third party apps
        "corsheaders",
        # Your apps
        "mapbox",
        "tax_credit",
        "tests",
    )

    # https://docs.djangoproject.com/en/2.0/topics/http/middleware/
    MIDDLEWARE = (
        "corsheaders.middleware.CorsMiddleware",
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    )

    # Email
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

    # General
    ADMINS = (("Author", ""),)
    LANGUAGE_CODE = "en-us"
    TIME_ZONE = "UTC"

    # If you set this to False, Django will make some optimizations so as not
    # to load the internationalization machinery.
    USE_I18N = False
    USE_L10N = True
    USE_TZ = True

    # URLs
    APPEND_SLASH = False
    ROOT_URLCONF = "config.urls"
    LOGIN_REDIRECT_URL = "/"

    # Set DEBUG to False as a default for safety
    # https://docs.djangoproject.com/en/dev/ref/settings/#debug
    DEBUG = strtobool(os.getenv("DJANGO_DEBUG", "no"))

    # Secret Key (Warning - Do not use in production!)
    SECRET_KEY = "w^8y-35j5&yn99*80j6f@6dys-2a_jfh2-+lo4-2ohu(ov7ios"

    # Password Validation
    # https://docs.djangoproject.com/en/2.0/topics/auth/passwords/#module-django.contrib.auth.password_validation
    AUTH_PASSWORD_VALIDATORS = [
        {
            "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
        },
    ]

    # Templates
    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
            },
        },
    ]

    # Database
    # https://docs.djangoproject.com/en/3.2/ref/settings/#databases
    DATABASES = {
        "default": {
            "ENGINE": "django.contrib.gis.db.backends.postgis",
            "NAME": os.getenv("POSTGRES_DB", "postgres"),
            "USER": os.getenv("POSTGRES_USER", "postgres"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", ""),
            "HOST": os.getenv("POSTGRES_HOST", "postgres"),
            "PORT": int(os.getenv("POSTGRES_PORT", 5433)),
            "CONN_MAX_AGE": int(os.getenv("POSTGRES_CONN_MAX_AGE", 0)),
            "DISABLE_SERVER_SIDE_CURSORS": False,
            "OPTIONS": {"sslmode": "prefer"},
        }
    }

    if strtobool(os.getenv("RESIZE_DB", "no")):
        DATABASES["resized"] = {
            "ENGINE": "django.contrib.gis.db.backends.postgis",
            "NAME": os.getenv("RESIZED_POSTGRES_DB", "postgres"),
            "USER": os.getenv("RESIZED_POSTGRES_USER", "postgres"),
            "PASSWORD": os.getenv("RESIZED_POSTGRES_PASSWORD", ""),
            "HOST": os.getenv("RESIZED_POSTGRES_HOST", "postgres"),
            "PORT": int(os.getenv("RESIZED_POSTGRES_PORT", 5432)),
            "CONN_MAX_AGE": int(os.getenv("RESIZED_POSTGRES_CONN_MAX_AGE", 0)),
            "DISABLE_SERVER_SIDE_CURSORS": False,
            "OPTIONS": {"sslmode": "prefer"},
        }

    # Logging
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "django.server": {
                "()": "django.utils.log.ServerFormatter",
                "format": "[%(server_time)s] %(message)s",
            },
            "verbose": {
                "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s"
            },
            "simple": {"format": "%(levelname)s %(message)s"},
        },
        "filters": {
            "require_debug_true": {
                "()": "django.utils.log.RequireDebugTrue",
            },
        },
        "handlers": {
            "django.server": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "formatter": "django.server",
            },
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "simple",
            },
            "mail_admins": {
                "level": "ERROR",
                "class": "django.utils.log.AdminEmailHandler",
            },
        },
        "loggers": {
            "django": {
                "handlers": ["console"],
                "propagate": True,
            },
            "django.server": {
                "handlers": ["django.server"],
                "level": "INFO",
                "propagate": False,
            },
            "django.request": {
                "handlers": ["mail_admins", "console"],
                "level": "ERROR",
                "propagate": False,
            },
            "django.db.backends": {"handlers": ["console"], "level": "INFO"},
        },
    }
