"""Representations of datasets used to populate the database tables.
"""

import geopandas as gpd
import glob
import logging
import numpy as np
import pandas as pd
import json
from abc import ABC, abstractmethod
from constants import (
    GEOJSONL_DIR,
    GEOPARQUET_DIR,
    RAW_DATA_DIR, 
    STATE_ABBREVIATIONS
)
from dataclasses import dataclass
from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry.polygon import Polygon
from typing import Optional


@dataclass
class GeoDataset(ABC):
    """Abstract representation of a dataset with metadata. 
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
    
    def _correct_geometry(self) -> gpd.GeoDataFrame:
        """Updates the geometry column of the dataset by transforming
        Polygons to MultiPolygons (at the time of writing, necessary for
        database load) and projecting to EPSG:4326.

        Args:
            None

        Returns:
            (`GeoDataFrame`): A snapshot of the current data.
        """
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
