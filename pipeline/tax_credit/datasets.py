"""Representations of datasets used to populate the database tables.
"""

# Standard library imports
import logging
import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

# Third-party imports
import geopandas as gpd
import numpy as np
import pandas as pd
from django.conf import settings
from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry.polygon import Polygon

# Application imports
from common.storage import DataLoader, DataWriter
from tax_credit.constants import STATE_ABBREVIATIONS
from tax_credit.models import Geography


@dataclass
class GeoDataset(ABC):
    """Abstract representation of a dataset with metadata."""

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

    reader: DataLoader
    """Client for reading input files from a local or cloud data store.
    """

    writer: DataWriter
    """Client for writing data to local or cloud store.
    """

    data: Optional[gpd.GeoDataFrame] = None
    """The data records.
    """

    @property
    def is_null(self) -> bool:
        """A boolean indicating whether the dataset is currently null."""
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

    def _correct_geometry(self) -> gpd.GeoDataFrame:
        """Updates the geometry column of the dataset by transforming
        Polygons to MultiPolygons (at the time of writing, necessary
        for database load) and setting the CRS to EPSG:4326.

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        try:
            # Convert geometries into Shapely MultiPolygons
            trans = lambda b: MultiPolygon([b]) if isinstance(b, Polygon) else b
            self.data["geometry"] = self.data["geometry"].apply(trans)

            # Change CRS to EPSG:4326 (geographic)
            self.data = self.data.set_crs(epsg=int(self.epsg))
            self.data = self.data.to_crs(epsg=4326)

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
        return self.data.copy()

    def _reshape_data(self) -> gpd.GeoDataFrame:
        """Adds metadata as new columns, subsets columns, and sorts
        columns and rows of the dataset.

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        self.data["geography_type"] = self.geography_type
        self.data["as_of"] = self.as_of
        self.data["published_on"] = self.published_on
        self.data["source"] = self.source
        self.data = self.data[
            [
                "name",
                "fips",
                "fips_pattern",
                "geography_type",
                "as_of",
                "published_on",
                "source",
                "geometry",
            ]
        ]
        self.data = self.data.sort_values(by="name")
        return self.data.copy()

    def process(self, **kwargs) -> gpd.GeoDataFrame:
        """Loads and cleans a dataset.

        References:
        - ["pandas | User Guide | Copy-on-Write (CoW)"](https://pandas.pydata.org/pandas-docs/stable/user_guide/copy_on_write.html#copy-on-write-enabling)

        Args:
            dataset (`GeoDataset`): The dataset instance to process.

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        # Enable Copy-on-Write (CoW) to avoid indexing side effects
        pd.set_option("mode.copy_on_write", True)

        # Load files
        self.logger.info(f"Loading input files.")
        self._load_and_aggregate(**kwargs)
        pre_num_records = len(self.data)
        self.logger.info(f"{pre_num_records:,} record(s) found.")

        # Filter records
        self.logger.info("Filtering the dataset to include only relevant records.")
        self._filter_records()
        post_num_records = len(self.data)
        if pre_num_records != post_num_records:
            self.logger.info(
                f"{post_num_records:,} record(s) remaining after filtering."
            )

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

    def to_geoparquet(self, index: bool = False) -> None:
        """Writes the dataset to a geoparquet file after
        buffering the geometry to remove overlaps. NOTE:
        Because the buffer has already been converted to
        degrees, user warnings about applying buffers
        to geographic projections are suppressed.

        Documentation:
        - ["geopandas.GeoSeries.buffer"](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoSeries.buffer.html)

        Args:
            index (`bool`): A boolean indicating whether the
                index should be included in the output file.
                Defaults to `False`.

        Returns:
            None
        """
        # Confirm dataset is not null
        if self.is_null:
            raise RuntimeError("Dataset is empty. Cannot write file.")

        # Make copy of DataFrame to avoid changing internal data state
        copy = self.data.copy()

        # Buffer geometry to remove slight overlaps
        with warnings.catch_warnings():
            warnings.simplefilter(action="ignore", category=UserWarning)
            copy.geometry = copy.geometry.buffer(settings.BUFFER_DEG)

        # Convert geometries back into Shapely MultiPolygons
        trans = lambda b: MultiPolygon([b]) if isinstance(b, Polygon) else b
        copy.geometry = copy.geometry.apply(trans)

        # Write to file
        fname = "_".join(self.name.replace("-", "_").split(" ")) + ".geoparquet"
        self.writer.write_geoparquet(fname, copy, index=index)

    def to_geojson_lines(self, index: bool = False) -> None:
        """Writes the dataset to a newline-delimited GeoJSON file.

        References:
        - https://stevage.github.io/ndgeojson/
        - https://datatracker.ietf.org/doc/html/rfc8142

        Args:
            index (`bool`): A boolean indicating whether the
                index should be included in the output file.
                Defaults to `False`.

        Returns:
            `None`
        """
        # Confirm dataset is not null
        if self.is_null:
            raise RuntimeError("Dataset is empty. Cannot write file.")

        # Write to file
        fname = "_".join(self.name.replace("-", "_").split(" ")) + ".geojsonl"
        self.writer.write_geojsonl(fname, self.data, index=index)


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
            `None`

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        # Parse input file paths
        try:
            coal_fpath = kwargs["coal_communities"]
        except KeyError as e:
            raise RuntimeError(
                "Missing file path. Expected to find key "
                f'"{e}" under "files" in configuration '
                "settings."
            ) from None

        # Load file
        zip_file_path = "IRA_Coal_Closure_Energy_Comm_2023v2/Coal_Closure_Energy_Communities_SHP_2023v2"
        self.data = self.reader.read_shapefile(coal_fpath, zip_file_path)

        return self.data.copy()

    def _build_name(self) -> gpd.GeoDataFrame:
        """Updates the data with a formatted name column.

        Args:
            `None`

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        if self.is_null:
            raise RuntimeError("Dataset is empty. Cannot construct name.")
        self.data["name"] = (
            self.data["CensusTrac"].str.upper()
            + ", "
            + self.data["County_Nam"].str.upper()
            + ", "
            + self.data["State_Name"].str.upper()
        )
        return self.data.copy()

    def _build_fips(self) -> gpd.GeoDataFrame:
        """Updates the data with one or more columns storing
        geography FIPS Codes.

        Args:
            `None`

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        if self.is_null:
            raise RuntimeError("Dataset is empty. Cannot construct FIPS Codes.")
        self.data["fips"] = self.data["geoid_trac"]
        self.data["fips_pattern"] = Geography.FipsPattern.STATE_COUNTY_TRACT
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
            `None`

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        # Parse input file paths
        try:
            counties_fpath = kwargs["counties"]
            state_fips_fpath = kwargs["state_fips"]
        except KeyError as e:
            raise RuntimeError(
                "Missing file path. Expected to find key "
                f'"{e}" under "files" in configuration '
                "settings."
            ) from None

        # Load shapefile of U.S. counties
        counties = self.reader.read_shapefile(counties_fpath)

        # Load CSV file of U.S. county FIPS codes
        fips = self.reader.read_csv(state_fips_fpath, delimiter="|", dtype=str)

        # Merge counties and fip codes
        self.data = counties.merge(
            right=fips[["STATE", "STATE_NAME"]],
            how="left",
            left_on="STATEFP",
            right_on="STATE",
        )

        return self.data.copy()

    def _build_name(self) -> gpd.GeoDataFrame:
        """Updates the data with a formatted name column.

        Args:
            `None`

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        if self.is_null:
            raise RuntimeError("Dataset is empty. Cannot construct name.")
        self.data["name"] = (
            self.data["NAMELSAD"].str.upper()
            + ", "
            + self.data["STATE_NAME"].str.upper()
        )
        return self.data.copy()

    def _build_fips(self) -> gpd.GeoDataFrame:
        """Updates the data with one or more columns storing
        geography FIPS Codes.

        Args:
            `None`

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        if self.is_null:
            raise RuntimeError("Dataset is empty. Cannot construct FIPS Codes.")
        self.data["fips"] = self.data["STATEFP"] + self.data["COUNTYFP"]
        self.data["fips_pattern"] = Geography.FipsPattern.STATE_COUNTY
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
            `None`

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        # Parse input file path
        try:
            distress_scores_fpath = kwargs["distress_scores"]
            zctas_fpath = kwargs["zctas"]
        except KeyError as e:
            raise RuntimeError(
                "Missing file path. Expected to find key "
                f'"{e}" under "files" in configuration '
                "settings."
            ) from None

        # Load zip code tabulation area shapefile
        zctas = self.reader.read_shapefile(zctas_fpath)

        # Load Excel file of distress scores
        scores = self.reader.read_excel(
            file_name=distress_scores_fpath, sheet_name="Zip code", dtype=str
        )

        # Merge datasets
        self.data = zctas.merge(
            right=scores[["Zipcode", "Quintile (5=Distressed)"]],
            how="left",
            left_on="ZCTA5CE20",
            right_on="Zipcode",
        )

        return self.data.copy()

    def _build_name(self) -> gpd.GeoDataFrame:
        """Updates the data with a formatted name column.

        Args:
            `None`

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        if self.is_null:
            raise RuntimeError("Dataset is empty. Cannot construct name.")
        self.data["name"] = "DISTRESSED ZCTA " + self.data["Zipcode"].str.upper()
        return self.data.copy()

    def _build_fips(self) -> gpd.GeoDataFrame:
        """Updates the data with one or more columns storing
        geography FIPS Codes.

        Args:
            `None`

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        if self.is_null:
            raise RuntimeError("Dataset is empty. Cannot construct FIPS Codes.")
        self.data["fips"] = self.data["fips_pattern"] = None
        return self.data.copy()

    def _filter_records(self) -> gpd.GeoDataFrame:
        """Filters the dataset to contain only relevant entries
        (i.e., zip code tabulation areas marked as distressed).

        Args:
            `None`

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        if self.is_null:
            raise RuntimeError("Dataset is empty. Cannot filter records.")
        self.data = self.data.query("`Quintile (5=Distressed)` == '5'")
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
            `None`

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        # Parse input file paths
        try:
            fossil_fuel_fpath = kwargs["fossil_fuel_communities"]
        except KeyError as e:
            raise RuntimeError(
                "Missing file path. Expected to find key "
                f'"{e}" under "files" in configuration '
                "settings."
            ) from None

        # Load data
        zip_file_path = (
            "MSA_NMSA_FEE_EC_Status_2023v2/MSA_NMSA_FEE_EC_Status_SHP_2023v2"
        )
        gdf = self.reader.read_shapefile(fossil_fuel_fpath, zip_file_path)

        # Subset data to include only column relevant to
        # metropolitan statistical areas (MSAs, the unit of analysis)
        gdf = gdf[["EC_qual_st", "msa_qual", "MSA_area_n", "geometry"]]

        # Group rows (counties) by MSA name
        self.data = gdf.groupby(by="MSA_area_n").first().reset_index()

        return self.data.copy()

    def _build_name(self) -> gpd.GeoDataFrame:
        """Updates the data with a formatted name column.

        Args:
            `None`

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        if self.is_null:
            raise RuntimeError("Dataset is empty. Cannot construct name.")

        def parse_row(row: pd.Series) -> str:
            """Builds a geography name using other fields.

            Args:
                row (`pd.Series`): The DataFrame row.

            Returns:
                (`str`): The name.
            """
            if row["msa_qual"] == "Non_MSA":
                prefix = "Non-Metropolitan Area"
                locale_name_end = row["MSA_area_n"].index("nonmetropolitan") - 1
                locale_name = row["MSA_area_n"][:locale_name_end]
                return f"{prefix} {locale_name}".upper()
            else:
                prefix = "Metropolitan Statistical Area"
                locale_name, state_abbrev = row["MSA_area_n"].split(", ")
                state_names = "-".join(
                    STATE_ABBREVIATIONS[a] for a in state_abbrev.split("-")
                )
                return f"{prefix} {locale_name}, {state_names}".upper()

        self.data["name"] = self.data.apply(parse_row, axis=1)

        return self.data.copy()

    def _build_fips(self) -> gpd.GeoDataFrame:
        """Updates the data with one or more columns storing
        geography FIPS Codes.

        Args:
            `None`

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        if self.is_null:
            raise RuntimeError("Dataset is empty. Cannot construct FIPS Codes.")
        self.data["fips"] = self.data["fips_pattern"] = None
        return self.data.copy()

    def _filter_records(self) -> gpd.GeoDataFrame:
        """Filters the dataset to contain only relevant entries.
        By default, does not perform any filtering and must
        be overridden by subclasses.

        Args:
            `None`

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        if self.is_null:
            raise RuntimeError("Dataset is empty. Cannot filter records.")
        self.data = self.data.query("EC_qual_st == 'Yes'")
        return self.data.copy()


class Justice40Dataset(GeoDataset):
    """Represents a dataset of Justice40 census tracts parsed
    from the Climate and Economic Justice Screening Tool.
    """

    def _load_and_aggregate(self, **kwargs) -> gpd.GeoDataFrame:
        """Loads and aggregates one or more input data files
        to build a `GeoDataFrame`. Then updates the data to
        reference that `GeoDataFrame`.

        Args:
            `None`

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        # Parse input file paths
        try:
            justice40_fpath = kwargs["justice40_communities"]
        except KeyError as e:
            raise RuntimeError(
                "Missing file path. Expected to find key "
                f'"{e}" under "files" in configuration '
                "settings."
            ) from None

        # Load dataset
        self.data = self.reader.read_shapefile(justice40_fpath)

        # Replace NaN values
        self.data = self.data.replace({np.nan: None})
        return self.data.copy()

    def _build_name(self) -> gpd.GeoDataFrame:
        """Updates the data with a formatted name column.

        Args:
            `None`

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        if self.is_null:
            raise RuntimeError("Dataset is empty. Cannot construct name.")

        def parse_row(row: pd.Series) -> str:
            """Builds a geography name using other fields.

            Args:
                row (`pd.Series`): The DataFrame row.

            Returns:
                (`str`): The name.
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

        self.data["name"] = self.data.apply(parse_row, axis=1)

        return self.data.copy()

    def _build_fips(self) -> gpd.GeoDataFrame:
        """Updates the data with one or more columns storing
        geography FIPS Codes.

        Args:
            `None`

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        if self.is_null:
            raise RuntimeError("Dataset is empty. Cannot construct FIPS Codes.")
        self.data["fips"] = self.data["GEOID10"]
        self.data["fips_pattern"] = Geography.FipsPattern.STATE_COUNTY_TRACT
        return self.data.copy()

    def _filter_records(self) -> gpd.GeoDataFrame:
        """Filters the dataset to contain only relevant entries.
        Here, only disadvantaged census tracts with geometries
        are retained. (Some census tracts are water bodies and
        therefore have a population size of zero.)

        Args:
            `None`

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        if self.is_null:
            raise RuntimeError("Dataset is empty. Cannot filter records.")
        has_geom = ~self.data.geometry.isna()
        is_disadv = self.data.SN_C == 1
        self.data = self.data[has_geom & is_disadv]
        return self.data.copy()


class LowIncomeDataset(GeoDataset):
    """Represents a dataset of low-income census tracts
    parsed from U.S. Census Bureau Tiger/Line Shapefiles,
    filtered by low-income status reported by the Department
    of the Treasury's New Markets Tax Credit (NMTC) Program.
    """

    def _load_and_aggregate(self, **kwargs) -> gpd.GeoDataFrame:
        """Loads and aggregates one or more input data files
        to build a `GeoDataFrame`. Then updates the data to
        reference that `GeoDataFrame`. NOTE: It is necessary to
        load both 2020 and 2010 census data because data from
        the U.S. territories (apart from Puerto Rico), has not
        yet been released.

        Args:
            `None`

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        # Parse input file paths
        try:
            county_fips_fpath = kwargs["county_fips"]
            income_territories_fpath = kwargs["low_income_territories"]
            income_states_fpath = kwargs["low_income_states"]
            state_fips_fpath = kwargs["state_fips"]
            tracts_2020_fpath = kwargs["tracts_2020"]
        except KeyError as e:
            raise RuntimeError(
                "Missing file path. Expected to find key "
                f'"{e}" under "files" in configuration '
                "settings."
            ) from None

        # Load state metadata
        state_fips = self.reader.read_csv(
            file_name=state_fips_fpath, delimiter="|", dtype=str
        )

        # Load county metadata
        county_fips = self.reader.read_csv(
            file_name=county_fips_fpath, delimiter="|", dtype=str
        )

        # Load NMTC poverty indicators for census tracts within U.S. states
        nmtc_state_pov = self.reader.read_excel(
            file_name=income_states_fpath, sheet_name="2016-2020", dtype=str
        )

        # Load NMTC high migration indicators for census tracts within U.S. states
        nmtc_state_mig = self.reader.read_excel(
            file_name=income_states_fpath,
            sheet_name="High migration tracts",
            skiprows=1,
            dtype=str,
        )

        # Load NMTC poverty indicators for census tracts within U.S. island territories
        nmtc_islands_pov = self.reader.read_excel(
            file_name=income_territories_fpath, sheet_name="NMTC LIC 2020", dtype=str
        )

        # Subset poverty datasets to relevant columns and concatenate
        nmtc_id_col = "2020 Census Tract Number FIPS code. GEOID"
        nmtc_pov_flag_col = "Does Census Tract Qualify For NMTC Low-Income Community (LIC) on Poverty or Income Criteria?"
        nmtc_cols = [nmtc_id_col, nmtc_pov_flag_col]
        nmtc_pov = pd.concat([nmtc_state_pov[nmtc_cols], nmtc_islands_pov[nmtc_cols]])

        # Filter poverty dataset to include only qualifying low-income census tracts
        nmtc_pov = nmtc_pov[nmtc_pov[nmtc_pov_flag_col] == "YES"]

        # Derive list of qualifying tract ids across all indicator datasets
        ids = nmtc_pov[nmtc_id_col].tolist() + nmtc_state_mig[nmtc_id_col].tolist()
        lic_ids = sorted(list(set(ids)))

        # Build GeoDataFrame of low-income census tracts
        gdf = None

        for pth in self.reader.list_directory_contents(tracts_2020_fpath):
            # Load tracts for state/state-equivalent
            tract_gdf = self.reader.read_shapefile(pth)

            # Filter to include only relevant tracts
            tract_gdf = tract_gdf.query("GEOID in @lic_ids")

            # Add county name metadata
            tract_gdf = tract_gdf.merge(
                how="left",
                right=county_fips[["STATEFP", "COUNTYFP", "COUNTYNAME"]],
                on=["STATEFP", "COUNTYFP"],
            )

            # Add state name metadata
            tract_gdf = tract_gdf.merge(
                how="left",
                right=state_fips[["STATE", "STATE_NAME"]],
                left_on="STATEFP",
                right_on="STATE",
            )

            # Concatenate tracts to larger GeoDataFrame
            gdf = tract_gdf if gdf is None else pd.concat([gdf, tract_gdf])

        # Store reference
        self.data = gdf

        return self.data.copy()

    def _build_name(self) -> gpd.GeoDataFrame:
        """Updates the data with a formatted name column.

        Args:
            `None`

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        if self.is_null:
            raise RuntimeError("Dataset is empty. Cannot construct name.")
        self.data["name"] = (
            "LOW-INCOME "
            + self.data["NAMELSAD"].str.upper()
            + ", "
            + self.data["COUNTYNAME"].str.upper()
            + ", "
            + self.data["STATE_NAME"].str.upper()
        )

        return self.data.copy()

    def _build_fips(self) -> gpd.GeoDataFrame:
        """Updates the data with one or more columns storing
        geography FIPS Codes.

        Args:
            `None`

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        if self.is_null:
            raise RuntimeError("Dataset is empty. Cannot construct FIPS Codes.")
        self.data["fips"] = self.data["GEOID"]
        self.data["fips_pattern"] = Geography.FipsPattern.STATE_COUNTY_TRACT
        return self.data.copy()


class MunicipalUtilityDataset(GeoDataset):
    """Represents a dataset of municipal utilities."""

    def _load_and_aggregate(self, **kwargs) -> gpd.GeoDataFrame:
        """Loads and aggregates one or more input data files
        to build a `GeoDataFrame`. Then updates the data to
        reference that `GeoDataFrame`.

        Args:
            `None`

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        # Parse input file paths
        try:
            corrected_names_fpath = kwargs["corrected_names"]
            utilities_fpath = kwargs["utilities"]
            hinton_iowa_fpath = kwargs["hinton_iowa"]
        except KeyError as e:
            raise RuntimeError(
                "Missing file path. Expected to find key "
                f'"{e}" under "files" in configuration '
                "settings."
            ) from None

        # Load utilities shapefile
        self.data = self.reader.read_shapefile(utilities_fpath)

        # Load corrected names
        corrected_names = self.reader.read_csv(
            file_name=corrected_names_fpath, dtype={"OBJECTID": int}
        )

        # Merge corrected names
        self.data = self.data.merge(
            right=corrected_names, how="left", on="OBJECTID", suffixes=["_DHS", "_CC"]
        )

        # Fix erroneous boundary for Hinton, IA
        # NOTE: The original dataset used the boundaries for Hinton, WV
        hinton = self.reader.read_shapefile(file_name=hinton_iowa_fpath)
        bad_data_idx = self.data.query(
            "NAME_DHS == 'CITY OF HINTON' & STATE == 'IA'"
        ).index.values[0]
        self.data.at[bad_data_idx, "geometry"] = hinton.iloc[0]["geometry"]

        return self.data.copy()

    def _build_name(self) -> gpd.GeoDataFrame:
        """Updates the data with a formatted name column.

        Args:
            `None`

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        if self.is_null:
            raise RuntimeError("Dataset is empty. Cannot construct names.")
        self.data["name"] = (
            self.data["NAME_CC"]
            + ", "
            + self.data["STATE"].apply(lambda s: STATE_ABBREVIATIONS[s])
        )
        self.data["name"] = self.data["name"].str.upper()
        return self.data.copy()

    def _build_fips(self) -> gpd.GeoDataFrame:
        """Updates the data with one or more columns storing
        geography FIPS Codes.

        Args:
            `None`

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        if self.is_null:
            raise RuntimeError("Dataset is empty. Cannot construct FIPS Codes.")
        self.data["fips"] = self.data["fips_pattern"] = None
        return self.data.copy()

    def _filter_records(self) -> gpd.GeoDataFrame:
        """Filters the dataset to contain only relevant entries
        (i.e., municipalities within the 50 U.S. states, the
        District of Columbia, and U.S. territories).

        Args:
            `None`

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        if self.is_null:
            raise RuntimeError("Dataset is empty. Cannot filter records.")
        municipal_types = ["MUNICIPAL", "MUNICIPAL MKTG AUTHORITY"]
        excluded_states = ["AB", "BC"]
        self.data = self.data.query(
            "TYPE in @municipal_types & " "STATE not in @excluded_states"
        )
        return self.data.copy()


class MunicipalityWithinStateDataset(GeoDataset):
    """Represents a dataset of all 35,731 municipalities (e.g., cities,
    towns, villages, townships, and boroughs) recognized by the U.S.
    Census Bureau within the 50 U.S. states and the District of Columbia.
    Aggregated from the U.S. Census Bureau's master address file for
    governments and 2020 TIGER/Line Shapefiles. A cross-walk between FIPS
    codes in the master address file and 2020 U.S. census was applied to
    ensure correct joins.

    NOTE: The Census Bureau distinguishes between municipalities and
    townships, but here we collapse the definitions together in accordance
    with [the definition](https://www.whitehouse.gov/about-the-white-house/our-government/state-local-government/)
    offered by the White House.
    """

    def _load_and_aggregate(self, **kwargs) -> gpd.GeoDataFrame:
        """Loads and aggregates one or more input data files
        to build a `GeoDataFrame`. Then updates the data to
        reference that `GeoDataFrame`.

        Args:
            `None`

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        # Parse input file names
        try:
            corrections_fpath = kwargs["corrections"]
            county_fips_fpath = kwargs["county_fips"]
            state_fips_fpath = kwargs["state_fips"]
            gov_units_fpath = kwargs["government_units"]
            places_fpath = kwargs["places"]
            county_subs_fpath = kwargs["county_subdivisions"]
        except KeyError as e:
            raise RuntimeError(
                "Missing file path. Expected to find key "
                f'"{e}" under "files" in configuration '
                "settings."
            ) from None

        # Load government unit file and corrections
        gov_units = self.reader.read_excel(file_name=gov_units_fpath, dtype=str)
        corrections = self.reader.read_json(file_name=corrections_fpath)

        # Filter units to remove counties
        gov_units = gov_units.query("UNIT_TYPE != '1 - COUNTY'")

        # Drop units that are no longer incorporated
        units_to_drop = corrections["census_id_gid"]["to_drop"]
        gov_units = gov_units.query("CENSUS_ID_GIDID not in @units_to_drop")

        # Correct place FIPS codes to match codes in 2020 Census
        fips_map = corrections["census_id_gid"]["to_corrected_fips"]
        correct_func = lambda r: fips_map.get(r["CENSUS_ID_GIDID"], r["FIPS_PLACE"])
        gov_units["FIPS_PLACE"] = gov_units.apply(correct_func, axis=1)

        # Consolidate FIPS columns to create GEOIDs for places and county subdivisions
        gov_units["FIPS_PLACE"] = gov_units["FIPS_PLACE"].replace({np.nan: ""})
        gov_units["GEOID_PLACE"] = gov_units["FIPS_STATE"] + gov_units["FIPS_PLACE"]
        gov_units["GEOID_SUBDIV"] = (
            gov_units["FIPS_STATE"] + gov_units["FIPS_COUNTY"] + gov_units["FIPS_PLACE"]
        )

        # Load place files
        places = None
        for pth in self.reader.list_directory_contents(places_fpath):
            loaded_gdf = self.reader.read_shapefile(pth)
            places = loaded_gdf if places is None else pd.concat([places, loaded_gdf])

        # Merge units and places
        gov_places = gov_units.merge(
            right=places, how="inner", left_on="GEOID_PLACE", right_on="GEOID"
        )

        # Load county subdivision files
        county_subs = None
        for pth in self.reader.list_directory_contents(county_subs_fpath):
            loaded_gdf = self.reader.read_shapefile(pth)
            county_subs = (
                loaded_gdf
                if county_subs is None
                else pd.concat([county_subs, loaded_gdf])
            )

        # Merge units and county subdivisions
        gov_county_subs = gov_units.merge(
            right=county_subs, how="inner", left_on="GEOID_SUBDIV", right_on="GEOID"
        )

        # Document origin dataset with new columns
        gov_places["DATASET"] = "places"
        gov_county_subs["DATASET"] = "county subdivisions"

        # Merge government places and county subdivisions into single GeoDataFrame
        cols = [
            "CENSUS_ID_GIDID",
            "GEOID_PLACE",
            "GEOID_SUBDIV",
            "FIPS_STATE",
            "FIPS_COUNTY",
            "UNIT_TYPE",
            "UNIT_NAME",
            "NAME",
            "NAMELSAD",
            "DATASET",
            "geometry",
        ]
        gdf = gpd.GeoDataFrame(pd.concat([gov_county_subs[cols], gov_places[cols]]))

        # Load state metadata
        state_fips = self.reader.read_csv(
            file_name=state_fips_fpath, delimiter="|", dtype=str
        )

        # Load county metadata
        county_fips = self.reader.read_csv(
            file_name=county_fips_fpath, delimiter="|", dtype=str
        )

        # Merge GeoDataFrame with state names
        gdf = gdf.merge(
            right=state_fips[["STATE_NAME", "STATE"]],
            how="left",
            left_on="FIPS_STATE",
            right_on="STATE",
        )

        # Merge GeoDataFrame with county names
        gdf = gdf.merge(
            right=county_fips[["STATEFP", "COUNTYFP", "COUNTYNAME"]],
            how="left",
            left_on=["FIPS_STATE", "FIPS_COUNTY"],
            right_on=["STATEFP", "COUNTYFP"],
        )

        # Apply name corrections
        name_replacement = corrections["unit_name"]["to_corrected_name"]
        gdf["UNIT_NAME"] = gdf["UNIT_NAME"].apply(lambda n: name_replacement.get(n, n))

        # Store reference to GeoDataFrame
        self.data = gdf

        return self.data.copy()

    def _build_name(self) -> gpd.GeoDataFrame:
        """Updates the data with a formatted name column
        while ensuring that each name is unique.

        Args:
            `None`

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        # Confirm that data has been loaded
        if self.is_null:
            raise RuntimeError("Dataset is empty. Cannot construct name.")

        # Define local function to standardize name
        def standardize_name(row: pd.Series, is_multiple: bool):
            """Standardizes the municipality name. When the same
            name appears multiple times in the same state, as given
            by the `is_multiple` flag, the county name is included
            to prevent confusion. Otherwise, the county name is
            omitted for improved readability.

            Args:
                row (`pd.Series`): The DataFrame row representing
                    the municipality.

                is_multiple (`bool`): A boolean indicating whether
                    the municipality's name appears more than once
                    within its U.S. state.

            Returns:
                (`str`): The corrected name.
            """
            entity = row["entity"]
            unit_name = row["UNIT_NAME"]
            legal_name = row["NAMELSAD"]
            short_name = row["NAME"]
            state_name = row["STATE_NAME"]
            county_name = row["COUNTYNAME"]

            if entity == "township" or entity.isdigit():
                return f"{legal_name}, {county_name}, {state_name}".upper()
            elif is_multiple:
                return f"{unit_name}, {county_name}, {state_name}".upper()
            else:
                return f"{short_name}, {state_name}".upper()

        # Add legal entity type column to dataset
        self.data["entity"] = self.data["NAMELSAD"].apply(lambda n: n.split()[-1])

        # Group municipal short names by state
        name_grps = self.data.groupby(by=["NAME", "FIPS_STATE"])

        # Apply standardization function to each unique
        # combination of municipality name and state
        stnd_gdf = None
        for name in name_grps.groups.keys():
            gdf = name_grps.get_group(name)
            is_multiple = len(gdf) > 1
            gdf["name"] = gdf.apply(lambda r: standardize_name(r, is_multiple), axis=1)
            stnd_gdf = gdf if stnd_gdf is None else pd.concat([stnd_gdf, gdf])

        # Update dataset with reference to DataFrame of standardized names
        self.data = stnd_gdf

        return self.data.copy()

    def _build_fips(self) -> gpd.GeoDataFrame:
        """Updates the data with one or more columns storing
        geography FIPS Codes.

        Args:
            `None`

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        # Confirm that data has been loaded
        if self.is_null:
            raise RuntimeError("Dataset is empty. Cannot construct FIPS Codes.")

        # Define local function to map FIPS code and pattern based on dataset type
        def map(row: pd.Series):
            if row["DATASET"] == "places":
                return row["GEOID_PLACE"], Geography.FipsPattern.STATE_PLACE
            else:
                return (
                    row["GEOID_SUBDIV"],
                    Geography.FipsPattern.STATE_COUNTY_COUNTY_SUBDIVISION,
                )

        # Apply function
        self.data[["fips", "fips_pattern"]] = self.data.apply(
            map, axis=1, result_type="expand"
        )

        return self.data.copy()

    def _filter_records(self) -> gpd.GeoDataFrame:
        """Filters the dataset to contain only relevant entries.
        This is accomplished by identifying duplicate government
        units that appear as both a place and county subdivision
        and then returning only the place, which better aligns
        with the municipality boundary.

        Args:
            `None`

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        # Confirm that data has been loaded
        if self.is_null:
            raise RuntimeError("Dataset is empty. Cannot filter records.")

        # Group data by common keys
        grp_cols = [
            "CENSUS_ID_GIDID",
            "GEOID_PLACE",
            "GEOID_SUBDIV",
            "UNIT_TYPE",
            "UNIT_NAME",
            "NAME",
            "NAMELSAD",
        ]
        grpd_df = self.data.groupby(by=grp_cols)

        # Remove duplicate records
        deduped_gdf = None
        for name in grpd_df.groups.keys():
            df = grpd_df.get_group(name)
            if len(df) > 1:
                df = df.query("DATASET == 'places'")
            deduped_gdf = df if deduped_gdf is None else pd.concat([deduped_gdf, df])

        # Update dataset with reference to de-duped DataFrame
        self.data = deduped_gdf

        return self.data.copy()


class MunicipalityWithinTerritoryDataset(GeoDataset):
    """Represents a dataset of municipalities within U.S. territories.

    NOTE: Here, only American Samoan villages and counties (the latter
    classifed as "minor civil divisions") and Guamanian municipalities
    are considered municipal equivalents because they have elected
    officials. For the Commonwealth of the Northern Mariana Islands
    and Puerto Rico, municipalities are considered county-equivalents
    and therefore processed through the `CountyDataset` instead. The
    U.S. Virgin Islands has no municipalities; the only government is
    for the territory as a whole.
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
            state_fips_fpath = kwargs["state_fips"]
            places_fpath = kwargs["places"]
            county_subs_fpath = kwargs["county_subdivisions"]
        except KeyError as e:
            raise RuntimeError(
                "Missing file path. Expected to find key "
                f'"{e}" under "files" in configuration '
                "settings."
            ) from None

        # Load county subdivision files
        county_subs = None
        for pth in self.reader.list_directory_contents(county_subs_fpath):
            loaded_gdf = self.reader.read_shapefile(pth)
            county_subs = (
                loaded_gdf
                if county_subs is None
                else pd.concat([county_subs, loaded_gdf])
            )

        # Load place files
        places = None
        for pth in self.reader.list_directory_contents(places_fpath):
            loaded_gdf = self.reader.read_shapefile(pth)
            places = loaded_gdf if places is None else pd.concat([places, loaded_gdf])

        # Load state metadata
        state_fips = self.reader.read_csv(
            file_name=state_fips_fpath, delimiter="|", dtype=str
        )

        # Load county metadata
        county_fips = self.reader.read_csv(
            file_name=county_fips_fpath, delimiter="|", dtype=str
        )

        # Merge county subdivisions with county metadata
        county_subs = county_subs.merge(
            right=county_fips[["STATEFP", "COUNTYFP", "COUNTYNAME"]],
            how="left",
            on=["STATEFP", "COUNTYFP"],
        )

        # Document origin dataset with new column
        places["DATASET"] = "places"
        county_subs["DATASET"] = "county subdivisions"

        # Concatenate county subdivisions and places into single GeoDataFrame
        places["COUNTYFP"] = places["COUSUBFP"] = None
        cols = [
            "NAME",
            "GEOID",
            "STATEFP",
            "COUNTYFP",
            "COUSUBFP",
            "DATASET",
            "geometry",
        ]
        gdf = gpd.GeoDataFrame(pd.concat([county_subs[cols], places[cols]]))

        # Merge resulting dataset with state metadata
        gdf = gdf.merge(
            right=state_fips[["STATE_NAME", "STATE"]],
            how="left",
            left_on="STATEFP",
            right_on="STATE",
        )

        # Store reference to DataFrame
        self.data = gdf

        return self.data.copy()

    def _build_name(self) -> gpd.GeoDataFrame:
        """Updates the data with a formatted name column.

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        # Confirm that data has been loaded
        if self.is_null:
            raise RuntimeError("Dataset is empty. Cannot construct name.")

        # Standardize name
        self.data["name"] = (
            self.data["NAME"].str.upper() + ", " + self.data["STATE_NAME"].str.upper()
        )

        return self.data.copy()

    def _build_fips(self) -> gpd.GeoDataFrame:
        """Updates the data with one or more columns storing
        geography FIPS Codes.

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        # Confirm that data has been loaded
        if self.is_null:
            raise RuntimeError("Dataset is empty. Cannot construct FIPS Codes.")

        # Set FIPS column
        self.data["fips"] = self.data["GEOID"]

        # Define local function to map FIPS code pattern based on dataset type
        map_func = lambda r: (
            Geography.FipsPattern.STATE_PLACE
            if r["DATASET"] == "places"
            else Geography.FipsPattern.STATE_COUNTY_COUNTY_SUBDIVISION
        )

        # Apply function
        self.data["fips_pattern"] = self.data.apply(map_func, axis=1)

        return self.data.copy()

    def _filter_records(self) -> gpd.GeoDataFrame:
        """Filters the dataset to contain only relevant entries
        (i.e., villages and counties in American Samoa and
        municipalities in Guam). Also removes an undefined
        county subdivision with the FIPS code "00000".

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        # Confirm that data has been loaded
        if self.is_null:
            raise RuntimeError("Dataset is empty. Cannot filter records.")

        # Define filters
        valid_place = (self.data["STATEFP"] == "60") & (
            self.data["DATASET"] == "places"
        )
        valid_county_sub = (
            (self.data["STATEFP"].isin(("60", "66")))
            & (self.data["COUSUBFP"] != "00000")
            & (self.data["DATASET"] == "county subdivisions")
        )

        # Apply filters
        self.data = self.data[(valid_place) | (valid_county_sub)]

        return self.data.copy()


class RuralCoopDataset(GeoDataset):
    """Represents a dataset of rural electric cooperatives."""

    def _load_and_aggregate(self, **kwargs) -> gpd.GeoDataFrame:
        """Loads and aggregates one or more input data files
        to build a `GeoDataFrame`. Then updates the data to
        reference that `GeoDataFrame`.

        Args:
            `None`

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        # Parse input file paths
        try:
            utilities_fpath = kwargs["utilities"]
        except KeyError as e:
            raise RuntimeError(
                "Missing file path. Expected to find key "
                f'"{e}" under "files" in configuration '
                "settings."
            ) from None

        # Load data
        self.data = self.reader.read_shapefile(utilities_fpath)
        return self.data.copy()

    def _build_name(self) -> gpd.GeoDataFrame:
        """Updates the data with a formatted name column.

        Args:
            `None`

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        if self.is_null:
            raise RuntimeError("Dataset is empty. Cannot construct names.")
        map_state = lambda s: STATE_ABBREVIATIONS[s]
        self.data["name"] = (
            "RURAL COOPERATIVE "
            + self.data["NAME"].str.upper()
            + ", "
            + self.data["STATE"].apply(map_state).str.upper()
        )
        return self.data.copy()

    def _build_fips(self) -> gpd.GeoDataFrame:
        """Updates the data with one or more columns storing
        geography FIPS Codes.

        Args:
            `None`

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        if self.is_null:
            raise RuntimeError("Dataset is empty. Cannot construct FIPS Codes.")
        self.data["fips"] = self.data["fips_pattern"] = None
        return self.data.copy()

    def _filter_records(self) -> gpd.GeoDataFrame:
        """Filters the dataset to contain only relevant entries
        (i.e., rural cooperatives only).

        Args:
            `None`

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        if self.is_null:
            raise RuntimeError("Dataset is empty. Cannot filter records.")
        self.data = self.data.query("TYPE == 'COOPERATIVE'")
        return self.data.copy()


class StateDataset(GeoDataset):
    """Represents a dataset of states parsed from
    U.S. Census Bureau TIGER/Line Shapefiles.
    """

    def _load_and_aggregate(self, **kwargs) -> gpd.GeoDataFrame:
        """Loads and aggregates one or more input data files
        to build a `GeoDataFrame`. Then updates the data to
        reference that `GeoDataFrame`.

        Args:
            `None`

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        # Parse input file path
        try:
            states_fpath = kwargs["states"]
        except KeyError as e:
            raise RuntimeError(
                "Missing file path to states shapefile. "
                f'Expected to find key "{e}" under '
                '"files" in configuration settings.'
            ) from None

        # Load shapefile of state boundaries and metadata
        try:
            self.data = self.reader.read_shapefile(states_fpath)
        except Exception as e:
            raise RuntimeError(f"Failed to load file. {e}") from None

        # Return a copy of the data for auditing purposes
        return self.data.copy()

    def _build_name(self) -> gpd.GeoDataFrame:
        """Updates the data with a formatted name column.

        Args:
            `None`

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        if self.is_null:
            raise RuntimeError("Dataset is empty. Cannot construct name.")
        self.data["name"] = self.data["NAME"].str.upper()
        return self.data.copy()

    def _build_fips(self) -> gpd.GeoDataFrame:
        """Updates the data with one or more columns storing
        geography FIPS Codes.

        Args:
            `None`

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
        if self.is_null:
            raise RuntimeError("Dataset is empty. Cannot construct FIPS Codes.")
        self.data["fips"] = self.data["STATEFP"]
        self.data["fips_pattern"] = Geography.FipsPattern.STATE
        return self.data.copy()


class DatasetFactory:
    """Factory for selecting datasets by name."""

    _REGISTRY = {
        "counties": CountyDataset,
        "distressed communities": DistressedDataset,
        "energy communities - coal": CoalDataset,
        "energy communities - fossil fuels": FossilFuelDataset,
        "justice40 communities": Justice40Dataset,
        "municipalities - states": MunicipalityWithinStateDataset,
        "municipalities - territories": MunicipalityWithinTerritoryDataset,
        "municipal utilities": MunicipalUtilityDataset,
        "low-income communities": LowIncomeDataset,
        "rural cooperatives": RuralCoopDataset,
        "states": StateDataset,
    }

    @staticmethod
    def create(
        name: str,
        as_of: str,
        geography_type: str,
        epsg: int,
        published_on: str,
        source: str,
        logger: logging.Logger,
        reader: DataLoader,
        writer: DataWriter,
    ) -> GeoDataset:
        """Static method for creating a `GeoDataset` subclass.

        Args:
            name (`str`): The informal name for the dataset.

            as_of (`str`): The date on which the data became current.

            geography_type (`str`): The geography type (e.g.,
                state, county) represented by the dataset.

            epsg (`int`): The coordinate reference system (CRS)
                of the dataset in terms of the standard EPSG code.

            published_on (`str`): The date on which the
                data was published/released.

            source (`str`): The organization publishing the data.

            logger (`logging.Logger`): A standard logger instance.

            reader (`common.storage.DataFrameReader`): Client for
                reading input files from a local or cloud data store.

            writer (`common.storage.DataFrameWriter`): Client for
                writing data to a local or cloud store.

        Returns:
            (`GeoDataset`): The initialized dataset.
        """
        try:
            dataset_type = DatasetFactory._REGISTRY[name]
        except KeyError:
            raise RuntimeError(
                f'Dataset "{name}" not found in ' "registry. Terminating process."
            )
        return dataset_type(
            name,
            as_of,
            geography_type,
            epsg,
            published_on,
            source,
            logger,
            reader,
            writer,
        )
