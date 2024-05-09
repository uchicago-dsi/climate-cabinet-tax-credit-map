"""Representations of fieldsets used for Mapbox API requests. 
"""

# Standard library imports
from typing_extensions import Self

# Third-party imports
from pydantic import BaseModel, model_validator

# Application imports
from .fields import (
    ResultSetLimit,
    ResultSetStart,
    ResultSetTimestampSortBy,
    TilesetDisplayName,
    TilesetFormalName,
    TilesetJobId,
    TilesetJobStage,
    TilesetLayerName,
    TilesetSourceFile,
    TilesetSourceId,
    TilesetType,
    TilesetVisibility,
    TilesetZoom,
    Token,
    Username,
)


class BaseFieldset(BaseModel):
    """Common fields used for HTTP requests to the Mapbox API."""

    token: Token
    username: Username


class TilesetCreateFieldset(BaseFieldset):
    """Fields used to request the creation of a new Mapbox tileset."""

    display_name: TilesetDisplayName
    formal_name: TilesetFormalName
    layer_name: TilesetLayerName
    max_zoom: TilesetZoom
    min_zoom: TilesetZoom
    source_id: TilesetSourceId

    @model_validator(mode="after")
    def validate_zoom_range(self) -> Self:
        """Confirms that the minimum zoom level is less
        than or equal to the maximum zoom level.

        Args:
            `None`

        Returns:
            (`TilesetCreateFieldset`): The instance.
        """
        if self.min_zoom.value > self.max_zoom.value:
            raise ValueError(
                f"The minimum value of the zoom range, "
                f"{self.min_zoom.value} is greater than "
                f"the maximum, {self.max_zoom}."
            )
        return self


class TilesetDeleteFieldset(BaseFieldset):
    """Fields used to delete a tileset."""

    tileset_formal_name: TilesetFormalName


class TilesetListFieldset(BaseFieldset):
    """Fields used to query for tilesets."""

    type: TilesetType
    visibility: TilesetVisibility
    sort_by: ResultSetTimestampSortBy
    limit: ResultSetLimit
    start: ResultSetStart


class TilesetJobCreateFieldset(BaseFieldset):
    """Fields used to create a new tileset publishing job."""

    tileset_formal_name: TilesetFormalName


class TilesetJobGetFieldset(BaseFieldset):
    """Fields used to fetch a tileset processing job."""

    tileset_formal_name: TilesetFormalName
    job_id: TilesetJobId


class TilesetJobListFieldset(BaseFieldset):
    """Fields used to query for tileset processing jobs."""

    tileset_formal_name: TilesetFormalName
    stage: TilesetJobStage
    limit: ResultSetLimit
    start: ResultSetStart


class TilesetMetadataGetFieldset(BaseFieldset):
    """Fields used to fetch TileJSON metadata for a tileset."""

    tileset_formal_name: TilesetFormalName


class TilesetRecipeUpdateFieldset(BaseFieldset):
    """Fields used to update a tileset recipe."""

    tileset_formal_name: TilesetFormalName
    source_id: TilesetSourceId
    layer_name: TilesetLayerName
    max_zoom: TilesetZoom
    min_zoom: TilesetZoom


class TilesetSourceCreateFieldset(BaseFieldset):
    """Fields used to create or append a new tileset source."""

    source_id: TilesetSourceId
    file: TilesetSourceFile


class TilesetSourceDeleteFieldset(BaseFieldset):
    """Fields used to delete a tileset source."""

    source_id: TilesetSourceId


class TilesetSourceListFieldset(BaseFieldset):
    """Fields used to query for tileset sources."""

    sort_by: ResultSetTimestampSortBy
    limit: ResultSetLimit
    start: ResultSetStart
