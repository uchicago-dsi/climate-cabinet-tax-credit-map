"""Constants used across the notebooks directory.
"""

# Standard library imports
from pathlib import Path


# Define coordinate reference systems
ALBERS = 9822
NAD83 = 4269

# Define top-level project directory
PROJECT_DIR = Path(__file__).parents[2]

# Define data subdirectory and relevant children directories
DATA_DIR = PROJECT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
CENSUS_DATA_DIR = RAW_DATA_DIR / "census"
BLOCK_GROUPS_DATA_DIR = CENSUS_DATA_DIR / "block_groups"
TRACTS_DATA_DIR = CENSUS_DATA_DIR / "tracts"
CLEAN_DATA_DIR = DATA_DIR / "clean"
CLEAN_ANALYSIS_DIR = CLEAN_DATA_DIR / "analysis"
CLEAN_GEOPARQUET_DIR = CLEAN_DATA_DIR / "geoparquet"

# Define paths to files referencing origin geographies and their populations
BLOCK_GROUPS_FPATH = BLOCK_GROUPS_DATA_DIR / "tl_2020_*_bg.zip"
BLOCK_GROUP_POP_AREA_FPATH = (
    BLOCK_GROUPS_DATA_DIR / "us_block_group_population_2020.csv"
)
BLOCK_GROUP_POP_CENTROIDS_FPATH = (
    BLOCK_GROUPS_DATA_DIR / "CenPop2020_Mean_BG.txt"
)
TRACT_POP_AREA_FPATH = TRACTS_DATA_DIR / "us_census_tract_population_2020.csv"
TRACT_POP_CENTROIDS_FPATH = TRACTS_DATA_DIR / "CenPop2020_Mean_TR.txt"
TRACTS_FPATH = TRACTS_DATA_DIR / "tl_2020_*_tract.zip"

# Define names of files referencing target geographies
COUNTIES_FNAME = "counties.geoparquet"
DISTRESSED_ZCTAS_FNAME = "distressed_communities.geoparquet"
MUNICIPAL_UTILS_FNAME = "municipal_utilities.geoparquet"
MUNICIPALITIES_FNAME = "municipalities___states.geoparquet"
RURAL_COOPS_FNAME = "rural_cooperatives.geoparquet"
