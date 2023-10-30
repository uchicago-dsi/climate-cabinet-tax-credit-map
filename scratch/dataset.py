"""
"""


import geopandas as gpd
import glob
import numpy as np
import pandas as pd
import json
import yaml
from abc import ABC, abstractmethod
from constants import (
    GEOJSONL_DIR,
    GEOPARQUET_DIR,
    RAW_DATA_DIR, 
    STATE_ABBREVIATIONS
)
from dataclasses import dataclass
from logger import logging, LoggerFactory
from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry.polygon import Polygon
from typing import Optional


@dataclass
class GeoDataset(ABC):
    """Publication information for the dataset. 
    """

    name: str
    """Informal name for the dataset.
    """

    as_of: str
    """The date on which the data became current.
    """

    geography_type: str
    """The geography type (e.g., state, county)
    represented by the dataset.
    """

    epsg: int
    """The coordinate reference system (CRS) of the dataset
    in terms of the standard EPSG code.
    """
    
    published_on: str
    """The date on which the data was published/released.
    """

    source: str
    """The organization publishing the data.
    """

    logger: logging.Logger
    """A standard logger instance.
    """

    data: Optional[gpd.GeoDataFrame] = None
    """The data records.
    """

    @property
    def is_empty(self) -> bool:
        """A boolean indicating whether the dataset has any records.
        """
        return self.data is None

    @abstractmethod
    def _load_and_aggregate(self, **kwargs) -> gpd.GeoDataFrame:
        """Loads and aggregates one or more input data files
        to build a `GeoDataFrame`. Then updates the data to 
        reference that `GeoDataFrame`.

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        raise NotImplementedError
    
    @abstractmethod
    def _build_name(self) -> gpd.GeoDataFrame:
        """Updates the data with a formatted name column.

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        raise NotImplementedError
    
    @abstractmethod
    def _build_fips(self) -> gpd.GeoDataFrame:
        """Updates the data with one or more columns storing
        geography FIPS Codes.

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        raise NotImplementedError

    def _build_population(self) -> gpd.GeoDataFrame:
        """Updates the data with one or more columns storing
        population estimates.

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        if self.is_empty:
            raise RuntimeError("Dataset is empty. Cannot count populations.")
        return self.data.copy()
    
    def _correct_geometry(self) -> gpd.GeoDataFrame:
        """Updates the geometry column of the dataset by transforming
        Polygons to MultiPolygons (at the time of writing, necessary for
        database load) and projecting to EPSG:4326.

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        if self.is_empty:
            raise RuntimeError("Dataset is empty. Cannot correct geometry.")     
        try:
            trans = lambda b: MultiPolygon([b]) if isinstance(b, Polygon) else b
            self.data["geometry"] = self.data["geometry"].apply(trans)
            self.data = self.data #.to_crs(epsg=4326)
            return self.data.copy()
        except Exception as e:
            raise Exception(f"Failed to correct geometry column. {e}") from None

    def _filter_records(self) -> gpd.GeoDataFrame:
        """Filters the dataset to contain only relevant entries.
        By default, does not perform any filtering and must
        be overridden by subclasses.

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        if self.is_empty:
            raise RuntimeError("Dataset is empty. Cannot filter records.")
        return self.data.copy()

    def _reshape_data(self) -> gpd.GeoDataFrame:
        """Adds metadata as new columns, subsets columns, and sorts
        columns and rows of the dataset.

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        if self.is_empty:
            raise RuntimeError("Dataset is empty. Cannot reshape.")
        
        self.data["geography_type"] = self.geography_type
        self.data["as_of"] = self.as_of
        self.data["published_on"] = self.published_on
        self.data["source"] = self.source
        self.data = self.data[[
            "name", 
            "fips", 
            "geography_type", 
            "as_of", 
            "published_on", 
            "source", 
            "geometry"
        ]]
        self.data = self.data.sort_values(by="name")
        return self.data.copy()
    
    def process(self, **kwargs) -> gpd.GeoDataFrame:
        """Loads and cleans a dataset.

        Args:
            dataset (`GeoDataset`): The dataset instance to process.

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        # Load files
        self.logger.info(f"Loading input files.")
        self._load_and_aggregate(**kwargs)
        self.logger.info(f"{len(self.data):,} record(s) found.")

        # Filter records
        self.logger.info("Filtering dataset to include only relevant records.")
        self._filter_records()
        self.logger.info(f"{len(self.data):,} record(s) remaining.")

        # Create name column
        self.logger.info("Building name column.")
        self._build_name()

        # Create FIPS Code columns
        self.logger.info("Building FIPS Code columns.")
        self._build_fips()

        # Correct geometry column
        self.logger.info("Correcting geometries and reprojecting CRS.")
        self._correct_geometry()

        # Reshape GeoDataFrame
        self.logger.info("Reshaping data.")
        self._reshape_data()

        return self.data.copy()

    def to_geoparquet(self, index: bool=False) -> None:
        """Writes the dataset to a geoparquet file.

        Args:
            index (`bool`): A boolean indicating whether the
                index should be included in the output file.
                Defaults to `False`.

        Returns:
            None
        """
        if self.is_empty:
            raise RuntimeError("Dataset is empty. Cannot write file.")
        fname = "_".join(self.name.replace("-", "_").split(" ")) + ".geoparquet"
        self.data.to_parquet(GEOPARQUET_DIR / fname, index=index)

    def to_geojson_lines(self) -> None:
        """Writes the dataset to a newline-delimited GeoJSON file.

        References:
        - https://stevage.github.io/ndgeojson/
        - https://datatracker.ietf.org/doc/html/rfc8142

        Args:
            None

        Returns:
            None
        """
        if self.is_empty:
            raise RuntimeError("Dataset is empty. Cannot write file.")
        counter = 0
        num_features = len(self.data)
        fname = "_".join(self.name.replace("-", "_").split(" ")) + ".geojsonl"
        with open(GEOJSONL_DIR / fname, "w") as f:
            for row in self.data.iterfeatures(drop_id=True):
                f.write(json.dumps(row))
                counter += 1
                if counter != num_features:
                    f.write("\n")


class StateDataset(GeoDataset):
    """Represents a dataset of states parsed from 
    U.S. Census Bureau TIGER/Line Shapefiles.
    """

    def _load_and_aggregate(self, **kwargs) -> gpd.GeoDataFrame:
        """Loads and aggregates one or more input data files
        to build a `GeoDataFrame`. Then updates the data to 
        reference that `GeoDataFrame`.

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        # Parse input file path
        try:
            states_fpath = kwargs["states"]
        except KeyError as e:
            raise RuntimeError("Missing file path to states shapefile. "
                               f"Expected to find key \"{e}\" under "
                               "\"files\" in configuration settings.") from None
        
        # Load shapefile of state boundaries and metadata
        try:
            self.data: gpd.GeoDataFrame = gpd.read_file(
                filename=RAW_DATA_DIR / states_fpath)
        except Exception as e:
            raise RuntimeError(f"Failed to load file. {e}") from None
        
        # Return a copy of the data for auditing purposes
        return self.data.copy()

    def _build_name(self) -> gpd.GeoDataFrame:
        """Updates the data with a formatted name column.

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        self.data["name"] = self.data["NAME"].str.upper()
        return self.data.copy()

    def _build_fips(self) -> gpd.GeoDataFrame:
        """Updates the data with one or more columns storing
        geography FIPS Codes.

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        self.data["fips"] = self.data["STATEFP"]
        return self.data.copy()


class CountyDataset(GeoDataset):
    """Represents a dataset of counties parsed from
    U.S. Census Bureau TIGER/Line Shapefiles.
    """

    def _load_and_aggregate(self, **kwargs) -> gpd.GeoDataFrame:
        """Loads and aggregates one or more input data files
        to build a `GeoDataFrame`. Then updates the data to 
        reference that `GeoDataFrame`.

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        # Parse input file paths
        try:
            counties_fpath = kwargs["counties"]
            county_fips_fpath = kwargs["county_fips"]
        except KeyError as e:
            raise RuntimeError("Missing file path. Expected to find key "
                               f"\"{e}\" under \"files\" in configuration "
                               "settings.") from None
        
        # Load shapefile of U.S. counties
        counties: gpd.GeoDataFrame = gpd.read_file(
            filename=RAW_DATA_DIR / counties_fpath)
        
        # Load CSV file of U.S. county FIPS codes
        fips: pd.DataFrame = pd.read_csv(
            filepath_or_buffer=RAW_DATA_DIR / county_fips_fpath,
            delimiter="|", 
            dtype=str)
        
        # Merge counties and fip codes
        self.data = counties.merge(
            right=fips[["STATE", "STATE_NAME"]],
            how="left",
            left_on="STATEFP",
            right_on="STATE")
        
        return self.data.copy()

    def _build_name(self) -> gpd.GeoDataFrame:
        """Updates the data with a formatted name column.

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        self.data["name"] = self.data["NAMELSAD"].str.upper() + \
                        ", " + self.data["STATE_NAME"].str.upper()
        return self.data.copy()

    def _build_fips(self) -> gpd.GeoDataFrame:
        """Updates the data with one or more columns storing
        geography FIPS Codes.

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        self.data["fips"] = self.data["STATEFP"] + self.data["COUNTYFP"]
        return self.data.copy()

    
class DistressedDataset(GeoDataset):
    """Represents a dataset of distressed zip codes
    parsed from U.S. Census Bureau Tiger/Line Shapefiles
    merged with the Distressed Community Index (DCI)
    scores published by the Economic Innovation Group.
    """

    def _load_and_aggregate(self, **kwargs) -> gpd.GeoDataFrame:
        """Loads and aggregates one or more input data files
        to build a `GeoDataFrame`. Then updates the data to 
        reference that `GeoDataFrame`.

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        # Parse input file path
        try:
            distress_scores_fpath = kwargs["distress_scores"]
            zctas_fpath = kwargs["zctas"]
        except KeyError as e:
            raise RuntimeError("Missing file path. Expected to find key "
                               f"\"{e}\" under \"files\" in configuration "
                               "settings.") from None
        
        # Load zip code tabulation area shapefile
        zctas: gpd.GeoDataFrame = gpd.read_file(
            filename=RAW_DATA_DIR / zctas_fpath)
        
        # Load Excel file of distress scores
        scores: pd.DataFrame = pd.read_excel(
            io=RAW_DATA_DIR / distress_scores_fpath,
            sheet_name="Zip code",
            dtype=str)
        
        # Merge datasets
        self.data = zctas.merge(
            right=scores[["Zipcode", "Quintile (5=Distressed)"]],
            how="left",
            left_on="ZCTA5CE20",
            right_on="Zipcode")
        
        return self.data.copy()

    def _build_name(self) -> gpd.GeoDataFrame:
        """Updates the data with a formatted name column.

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        if self.is_empty:
            raise RuntimeError("Dataset is empty. Cannot construct name.")
        self.data["name"] = "DISTRESSED ZCTA " + \
                            self.data["Zipcode"].str.upper()
        return self.data.copy()

    def _build_fips(self) -> gpd.GeoDataFrame:
        """Updates the data with one or more columns storing
        geography FIPS Codes.

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        if self.is_empty:
            raise RuntimeError("Dataset is empty. Cannot construct FIPS Codes.")
        self.data["fips"] = None
        return self.data.copy()
    
    def _filter_records(self) -> gpd.GeoDataFrame:
        """Filters the dataset to contain only relevant entries
        (i.e., zip code tabulation areas marked as distressed).

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        if self.is_empty:
            raise RuntimeError("Dataset is empty. Cannot filter records.")
        self.data = self.data.query("`Quintile (5=Distressed)` == '5'")
        return self.data.copy()


class LowIncomeDataset(GeoDataset):
    """Represents a dataset of low-income census tracts
    parsed from U.S. Census Bureau Tiger/Line Shapefiles,
    filtered by low-income status reported by the Department
    of the Treasury's New Markets Tax Credit (NMTC) Program.
    """

    def _find_qualifying_tracts(
        self,
        county_fips: pd.DataFrame,
        state_fips: pd.DataFrame,
        nmtc_fpath: str,
        nmtc_pov_id_col: str,
        nmtc_pov_sheet_name: str,
        nmtc_migr_id_col: str,
        nmtc_migr_sheet_name: str,
        nmtc_indic_col: str,
        tracts_fpath_rgx: str) -> gpd.GeoDataFrame:
        """
        """
        # Read first Excel sheet of dataset for low-income status
        # (Examining qualification based on income or poverty criteria)
        has_pov_df = pd.read_excel(
            io=nmtc_fpath,
            sheet_name=nmtc_pov_sheet_name,
            dtype=str)
                
        # Subset to include only qualifying low-income tracts
        has_pov_df = has_pov_df[has_pov_df[nmtc_indic_col] == "YES"]

        # Read second Excel sheet of dataset for low-income status
        # (Examining qualification based on high migration rates)
        migr_df = pd.read_excel(
            io=nmtc_fpath,
            sheet_name=nmtc_migr_sheet_name,
            skiprows=1,
            dtype=str)
        
        # Derive list of qualifying tract ids
        ids = has_pov_df[nmtc_pov_id_col].tolist() + \
            migr_df[nmtc_migr_id_col].tolist()
        lic_ids = sorted(list(set(ids)))

        # Build GeoDataFrame of low-income census tracts
        gdf = None
        for pth in glob.glob(tracts_fpath_rgx):

            # Load tracts for state/state-equivalent
            tract_gdf = gpd.read_file(pth, dtype=str)

            # Standardize columns (necessary to handle different census years)
            new_cols = [c.replace("10", "") for c in tract_gdf.columns.tolist()]
            tract_gdf.columns = new_cols

            # Filter to include only relevant tracts
            tract_gdf = tract_gdf.query("GEOID in @lic_ids")

            # Add county name metadata
            tract_gdf = tract_gdf.merge(
                how="left",
                right=county_fips[["STATEFP", "COUNTYFP", "COUNTYNAME"]],
                on=["STATEFP", "COUNTYFP"])
            
            # Add state name metadata
            tract_gdf = tract_gdf.merge(
                how="left",
                right=state_fips[["STATE", "STATE_NAME"]],
                left_on="STATEFP",
                right_on="STATE")

            # Concatenate states to larger GeoDataFrame
            gdf = tract_gdf if gdf is None else pd.concat([gdf, tract_gdf])

        return gdf

    def _load_and_aggregate(self, **kwargs) -> gpd.GeoDataFrame:
        """Loads and aggregates one or more input data files
        to build a `GeoDataFrame`. Then updates the data to 
        reference that `GeoDataFrame`. NOTE: It is necessary to 
        load both 2020 and 2010 census data because data from
        the U.S. territories (apart from Puerto Rico), has not
        yet been released.

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        # Parse input file paths
        try:
            county_fips_fpath = kwargs["county_fips"]
            income_2016_fpath = kwargs["low_income_2011_2015"]
            income_2020_fpath = kwargs["low_income_2016_2020"]
            state_fips_fpath = kwargs["state_fips"]
            tracts_2010_fpath = kwargs["tracts_2010"]
            tracts_2020_fpath = kwargs["tracts_2020"]
        except KeyError as e:
            raise RuntimeError("Missing file path. Expected to find key "
                               f"\"{e}\" under \"files\" in configuration "
                               "settings.") from None
    
        # Load county metadata
        county_fips = pd.read_csv(
            filepath_or_buffer=RAW_DATA_DIR / county_fips_fpath,
            delimiter="|",
            dtype=str)
        
        # Load state metadata
        state_fips = pd.read_csv(
            filepath_or_buffer=RAW_DATA_DIR / state_fips_fpath,
            delimiter="|",
            dtype=str)

        # Load data for 2020 Census
        gdf2020 = self._find_qualifying_tracts(
            county_fips,
            state_fips,
            nmtc_fpath=RAW_DATA_DIR / income_2020_fpath,
            nmtc_pov_id_col="2020 Census Tract Number FIPS code. GEOID",
            nmtc_pov_sheet_name="2016-2020",
            nmtc_migr_id_col="2020 Census Tract Number FIPS code. GEOID",
            nmtc_migr_sheet_name="High migration tracts",
            nmtc_indic_col="Does Census Tract Qualify For NMTC Low-Income Community (LIC) on Poverty or Income Criteria?",
            tracts_fpath_rgx=RAW_DATA_DIR / tracts_2020_fpath)
        
        # Load data for 2010 Census
        gdf2010 = self._find_qualifying_tracts(
            county_fips,
            state_fips,
            nmtc_fpath=RAW_DATA_DIR / income_2016_fpath,
            nmtc_pov_id_col="2010 Census Tract Number FIPS code. GEOID",
            nmtc_pov_sheet_name="NMTC LICs 2011-2015 ACS",
            nmtc_migr_id_col="2010 Census Tract Number FIPS code GEOID",
            nmtc_migr_sheet_name="High migration tracts",
            nmtc_indic_col="Does Census Tract Qualify For NMTC Low-Income Community (LIC) on Poverty or Income Criteria?",
            tracts_fpath_rgx=RAW_DATA_DIR / tracts_2010_fpath)
        
        # Concatenate GeoDataFrames
        self.data = pd.concat([gdf2020, gdf2010])

        return self.data.copy()

    def _build_name(self) -> gpd.GeoDataFrame:
        """Updates the data with a formatted name column.

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        if self.is_empty:
            raise RuntimeError("Dataset is empty. Cannot construct name.")
        self.data["name"] = "LOW-INCOME " + \
            self.data["NAMELSAD"].str.upper() + ", " + \
            self.data["COUNTYNAME"].str.upper() + ", " + \
            self.data["STATE_NAME"].str.upper()
        
        return self.data.copy()

    def _build_fips(self) -> gpd.GeoDataFrame:
        """Updates the data with one or more columns storing
        geography FIPS Codes.

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        if self.is_empty:
            raise RuntimeError("Dataset is empty. Cannot construct FIPS Codes.")
        self.data["fips"] = self.data["GEOID"]
        return self.data.copy()


class Justice40Dataset(GeoDataset):
    """Represents a dataset of Justice40 communities parsed
    from the Climate and Economic Justice Screening Tool.
    """

    def _load_and_aggregate(self, **kwargs) -> gpd.GeoDataFrame:
        """Loads and aggregates one or more input data files
        to build a `GeoDataFrame`. Then updates the data to 
        reference that `GeoDataFrame`.

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        # Parse input file paths
        try:
            justice40_fpath = kwargs["justice40_communities"]
        except KeyError as e:
            raise RuntimeError("Missing file path. Expected to find key "
                               f"\"{e}\" under \"files\" in configuration "
                               "settings.") from None
        
        # Load dataset
        self.data: gpd.GeoDataFrame = gpd.read_file(
            filename=RAW_DATA_DIR / justice40_fpath)
        
        # Replace NaN values
        self.data = self.data.replace({np.nan: None})
        return self.data.copy()
    
    def _build_name(self) -> gpd.GeoDataFrame:
        """Updates the data with a formatted name column.

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        # Define local function
        def parse_row(row: pd.Series) -> str:
            """Builds a geography name using other fields.

            Args:
                row (`pd.Series`): The DataFrame row.

            Returns:
                (str): The name.
            """
            # Format tract id
            tract_id = row["GEOID10"]
            tract_num = tract_id[-6:-2].lstrip("0")
            block_grp = tract_id[-2:]
            fmd_tract = tract_num if block_grp == "00" else f"{tract_num}.{block_grp}"
            tract = f"CENSUS TRACT {fmd_tract}, "

            # Format county
            county = f"{row['CF'].upper()}, " if row["CF"] else ""

            # Format state
            state = f"{row['SF'].upper()}"

            # Compose name
            return f"JUSTICE40 {tract}{county}{state}"
        
        # Apply function to generate name column.
        self.data["name"] = self.data.apply(parse_row, axis=1)

        return self.data.copy()

    def _build_fips(self) -> gpd.GeoDataFrame:
        """Updates the data with one or more columns storing
        geography FIPS Codes.

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        self.data["fips"] = self.data["GEOID10"]
        return self.data.copy()

    def _filter_records(self) -> gpd.GeoDataFrame:
        """Filters the dataset to contain only relevant entries.
        By default, does not perform any filtering and must
        be overridden by subclasses.

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        if self.is_empty:
            raise RuntimeError("Dataset is empty. Cannot filter records.")
        self.data = self.data.query("SN_C == 1")
        return self.data.copy()


class CoalDataset(GeoDataset):
    """Represents a dataset of 2020 U.S. census tracts
    affected by coal plant closures and thereafter
    designated as energy communities.
    """

    def _load_and_aggregate(self, **kwargs) -> gpd.GeoDataFrame:
        """Loads and aggregates one or more input data files
        to build a `GeoDataFrame`. Then updates the data to 
        reference that `GeoDataFrame`.

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        # Parse input file paths
        try:
            coal_fpath = kwargs["coal_communities"]
        except KeyError as e:
            raise RuntimeError("Missing file path. Expected to find key "
                               f"\"{e}\" under \"files\" in configuration "
                               "settings.") from None
        
        # Load file
        self.data: gpd.GeoDataFrame = gpd.read_file(
            filename=RAW_DATA_DIR / coal_fpath)
        
        return self.data.copy()

    def _build_name(self) -> gpd.GeoDataFrame:
        """Updates the data with a formatted name column.

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        self.data["name"] = self.data["CensusTrac"].str.upper() + ", " + \
                            self.data["County_Nam"].str.upper() + ", " + \
                            self.data["State_Name"].str.upper()
        return self.data.copy()

    def _build_fips(self) -> gpd.GeoDataFrame:
        """Updates the data with one or more columns storing
        geography FIPS Codes.

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        self.data["fips"] = self.data["geoid_trac"]
        return self.data.copy()


class FossilFuelDataset(GeoDataset):
    """Represents a dataset of 2010 U.S. MSAs and non-MSAs
    affected by fossil fuel industry unemployment and 
    thereafter designated as energy communities.
    """

    def _load_and_aggregate(self, **kwargs) -> gpd.GeoDataFrame:
        """Loads and aggregates one or more input data files
        to build a `GeoDataFrame`. Then updates the data to 
        reference that `GeoDataFrame`.

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        # Parse input file paths
        try:
            fossil_fuel_fpath = kwargs["fossil_fuel_communities"]
        except KeyError as e:
            raise RuntimeError("Missing file path. Expected to find key "
                               f"\"{e}\" under \"files\" in configuration "
                               "settings.") from None
        
        # Load data
        gdf: gpd.GeoDataFrame = gpd.read_file(
            filename=RAW_DATA_DIR / fossil_fuel_fpath)
        
        # Subset data to include only column relevant to
        # metropolitan statistical areas (MSAs, the unit of analysis)
        gdf = gdf[["EC_qual_st", "msa_qual", "MSA_area_n", "geometry"]]
        
        # Group rows (counties) by MSA name
        self.data = gdf.groupby(by="MSA_area_n").first().reset_index()

        return self.data.copy()

    def _build_name(self) -> gpd.GeoDataFrame:
        """Updates the data with a formatted name column.

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        # Define local function
        def parse_row(row: pd.Series) -> str:
            """Builds a geography name using other fields.

            Args:
                row (`pd.Series`): The DataFrame row.

            Returns:
                (str): The name.
            """
            if row["msa_qual"] == "Non_MSA":
                prefix = "Non-Metropolitan Area"
                locale_name_end = row["MSA_area_n"].index("nonmetropolitan") - 1
                locale_name = row["MSA_area_n"][:locale_name_end]
                return f"{prefix} {locale_name}".upper()
            else:
                prefix = "Metropolitan Statistical Area"
                locale_name, state_abbrev = row["MSA_area_n"].split(", ")
                state_names = '-'.join(
                    STATE_ABBREVIATIONS[a] 
                    for a in 
                    state_abbrev.split("-")
                )
                return f"{prefix} {locale_name}, {state_names}".upper()
            
        # Apply function to generate name columns
        self.data["name"] = self.data.apply(parse_row, axis=1)

        return self.data.copy()

    def _build_fips(self) -> gpd.GeoDataFrame:
        """Updates the data with one or more columns storing
        geography FIPS Codes.

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        self.data["fips"] = None
        return self.data.copy()

    def _filter_records(self) -> gpd.GeoDataFrame:
        """Filters the dataset to contain only relevant entries.
        By default, does not perform any filtering and must
        be overridden by subclasses.

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        self.data = self.data.query("EC_qual_st == 'Yes'")
        return self.data.copy()


class RuralCoopDataset(GeoDataset):
    """Represents a dataset of rural electric cooperatives.
    """

    def _load_and_aggregate(self, **kwargs) -> gpd.GeoDataFrame:
        """Loads and aggregates one or more input data files
        to build a `GeoDataFrame`. Then updates the data to 
        reference that `GeoDataFrame`.

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        # Parse input file paths
        try:
            utilities_fpath = kwargs["utilities"]
        except KeyError as e:
            raise RuntimeError("Missing file path. Expected to find key "
                               f"\"{e}\" under \"files\" in configuration "
                               "settings.") from None
        
        # Load data
        self.data: gpd.GeoDataFrame = gpd.read_file(
            filename=RAW_DATA_DIR / utilities_fpath,
            dtype=str)
        
        return self.data.copy()

    def _build_name(self) -> gpd.GeoDataFrame:
        """Updates the data with a formatted name column.

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        map_state = lambda s: STATE_ABBREVIATIONS[s]
        self.data["name"] = "RURAL COOPERATIVE " + \
            self.data["NAME"].str.upper() + ", " +\
            self.data["STATE"].apply(map_state).str.upper()
        return self.data.copy()

    def _build_fips(self) -> gpd.GeoDataFrame:
        """Updates the data with one or more columns storing
        geography FIPS Codes.

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        self.data["fips"] = None
        return self.data.copy()
    
    def _filter_records(self) -> gpd.GeoDataFrame:
        """Filters the dataset to contain only relevant entries
        (i.e., rural cooperatives only).

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        if self.is_empty:
            raise RuntimeError("Dataset is empty. Cannot filter records.")
        self.data = self.data.query("TYPE == 'COOPERATIVE'")
        return self.data.copy()


class MunicipalityDataset(GeoDataset):
    """Represents a dataset county subdivisions
    parsed from U.S. Census Bureau TIGER/Line Shapefiles.
    """

    def _load_and_aggregate(self, **kwargs) -> gpd.GeoDataFrame:
        """Loads and aggregates one or more input data files
        to build a `GeoDataFrame`. Then updates the data to 
        reference that `GeoDataFrame`.

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        # Parse input file names
        try:
            county_fips_fpath = kwargs["county_fips"]
            county_subdivisions_fpath = kwargs["county_subdivisions"]
            state_fips_fpath = kwargs["state_fips"]
        except KeyError as e:
            raise RuntimeError("Missing file path. Expected to find key "
                               f"\"{e}\" under \"files\" in configuration "
                               "settings.") from None

        # Load county subdivision files
        fpaths = glob.glob(RAW_DATA_DIR / county_subdivisions_fpath)
        gdf = None
        for pth in fpaths:
            loaded_gdf = gpd.read_file(pth)
            gdf = loaded_gdf if gdf is None else pd.concat([gdf, loaded_gdf])

        # Load state metadata
        state_fips = pd.read_csv(
            filepath_or_buffer=RAW_DATA_DIR / state_fips_fpath,
            delimiter="|",
            dtype=str)

        # Load county metadata
        county_fips = pd.read_csv(
            filepath_or_buffer=RAW_DATA_DIR / county_fips_fpath,
            delimiter="|",
            dtype=str)
        
        # Merge county subdivisions with state names 
        gdf = gdf.merge(
            how="left",
            right=state_fips[["STATE", "STATE_NAME"]],
            left_on="STATEFP",
            right_on="STATE")

        # Merge county subdivisions with county names 
        self.data = gdf.merge(
            how="left",
            right=county_fips[["STATEFP", "COUNTYFP", "COUNTYNAME"]],
            on=["STATEFP", "COUNTYFP"])

        return self.data.copy()

    def _build_name(self) -> gpd.GeoDataFrame:
        """Updates the data with a formatted name column.

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        # Define local function
        def parse_row(row: pd.Series) -> str:
            """Builds a geography name using other fields.

            Args:
                row (`pd.Series`): The DataFrame row.

            Returns:
                (str): The name.
            """
            state = row["STATE_NAME"].upper()
            county = row["COUNTYNAME"].upper()
            subdivision = row["NAME"].upper()
            gov_lvl = row["NAMELSAD"].split()[-1].upper()

            try:
                int(subdivision)
                gov_lvl_is_num = True
            except ValueError:
                gov_lvl_is_num = False
            
            if gov_lvl_is_num:
                subdivision_full = row["NAMELSAD"].upper()
            elif gov_lvl in ("CITY", "VILLAGE"):
                subdivision_full = f"{gov_lvl} OF {subdivision}"
            else:
                subdivision_full = f"{subdivision} {gov_lvl}"

            return f"{subdivision_full}, {county}, {state}"
        
        # Apply function to generate name column
        self.data["name"] = self.data.apply(parse_row, axis=1)

        return self.data.copy()

    def _build_fips(self) -> gpd.GeoDataFrame:
        """Updates the data with one or more columns storing
        geography FIPS Codes.

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        self.data["fips"] = self.data["GEOID"]
        return self.data.copy()

    def _filter_records(self) -> gpd.GeoDataFrame:
        """Filters the dataset to contain only relevant entries
        (i.e., relevant geography type classes).

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        if self.is_empty:
            raise RuntimeError("Dataset is empty. Cannot filter records.")
        valid_classes = ["C2", "C5", "T1", "T5", "Z2", "Z3", "Z5", "Z7"]
        self.data = self.data.query("CLASSFP in @valid_classes")
        return self.data.copy()


class MunicipalUtilityDataset(GeoDataset):
    """Represents a dataset of municipal utilities.
    """
   
    def _load_and_aggregate(self, **kwargs) -> gpd.GeoDataFrame:
        """Loads and aggregates one or more input data files
        to build a `GeoDataFrame`. Then updates the data to 
        reference that `GeoDataFrame`.

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        # Parse input file paths
        try:
            corrected_names_fpath = kwargs["corrected_names"]
            utilities_fpath = kwargs["utilities"]
        except KeyError as e:
            raise RuntimeError("Missing file path. Expected to find key "
                               f"\"{e}\" under \"files\" in configuration "
                               "settings.") from None
        
        # Load utilities shapefile
        self.data: gpd.GeoDataFrame = gpd.read_file(
            filename=RAW_DATA_DIR / utilities_fpath)
        
        # Load corrected names
        corrected_names = pd.read_csv(
            filepath_or_buffer=RAW_DATA_DIR / corrected_names_fpath,
            dtype={"OBJECTID": int})

        # Merge corrected names
        self.data = self.data.merge(
            right=corrected_names,
            how="left",
            on="OBJECTID",
            suffixes=["_DHS", "_CC"])
        
        return self.data.copy()

    def _build_name(self) -> gpd.GeoDataFrame:
        """Updates the data with a formatted name column.

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        self.data["name"] = self.data["NAME_CC"] + ", " + \
            self.data["STATE"].apply(lambda s: STATE_ABBREVIATIONS[s])
        return self.data.copy()

    def _build_fips(self) -> gpd.GeoDataFrame:
        """Updates the data with one or more columns storing
        geography FIPS Codes.

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        self.data["fips"] = None
        return self.data.copy()
    
    def _filter_records(self) -> gpd.GeoDataFrame:
        """Filters the dataset to contain only relevant entries
        (i.e., municipalities within the 50 U.S. states, the 
        District of Columbia, and U.S. territories).

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        if self.is_empty:
            raise RuntimeError("Dataset is empty. Cannot filter records.")
        municipal_types = ['MUNICIPAL', 'MUNICIPAL MKTG AUTHORITY']
        excluded_states = ["AB", "BC"]
        self.data = self.data.query("TYPE in @municipal_types & "
                                    "STATE not in @excluded_states")
        return self.data.copy()



if __name__ == "__main__":
    with open("./config/datasets.yaml") as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    registry = {
        "counties": CountyDataset,
        "distressed communities": DistressedDataset,
        "energy communities - coal": CoalDataset,
        "energy communities - fossil fuels": FossilFuelDataset,
        "justice40 communities": Justice40Dataset,
        "low-income communities": LowIncomeDataset,
        "municipalities": MunicipalityDataset,
        "municipal utilities": MunicipalUtilityDataset,
        "rural cooperatives": RuralCoopDataset,
        "states": StateDataset
    }

    logger = LoggerFactory.get("DATASET-CLEAN")

    for c in config:
        if c["name"].startswith("state"):
            logger.info(f"Received request to process dataset \"{c['name']}\".")
            try:
                dataset_type = registry[c["name"]]
            except KeyError:
                raise RuntimeError("Dataset not found in registry. "
                                   "Terminating process.")
            
            logger.info("Initializing dataset.")
            fpaths = c.pop("files")
            dataset: GeoDataset = dataset_type(**{**c, "logger": logger})
            
            logger.info("Beginning processing job.")
            dataset.process(**fpaths)

            logger.info("Writing processed data to geoparquet file.")
            dataset.to_geoparquet()

            logger.info("Writing processed data to new line delimited GeoJSON.")
            dataset.to_geojson_lines()

    