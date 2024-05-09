"""Representations of fields used in Mapbox API requests. 
"""

# Standard library imports
import io
from abc import abstractmethod
from typing import Optional

# Third-party imports
from pydantic import (
    BaseModel,
    ConfigDict,
    StrictInt,
    Field,
    computed_field,
)


class Username(BaseModel):
    """The username associated with the Mapbox API account."""

    value: str


class TilesetDisplayName(BaseModel):
    """The descriptive name of the tileset, used for
    public display. Limited to 64 characters.
    """

    value: str = Field(min_length=1, max_length=64)


class TilesetFormalName(BaseModel):
    """The formal name of the tileset, used internally within Mapbox.
    Must be unique for each user account. Limited to 32
    characters. Only allows `-` and `_` as special characters.
    """

    value: str = Field(min_length=1, max_length=32, pattern=r"^[a-zA-Z0-9\_\-]*$")


class TilesetJobId(BaseModel):
    """The id of a tileset procesing job."""

    value: str


class TilesetLayerName(BaseModel):
    """The name of the tileset layer. Must be a string
    with only underscores and alphanumeric characters.
    """

    value: str = Field(min_length=1, pattern=r"^[a-zA-Z0-9\_]*$")


class TilesetZoom(BaseModel):
    """A zoom level. Must be between 0 and 16, inclusive."""

    value: StrictInt = Field(ge=0, le=16)


class TilesetSourceId(BaseModel):
    """A unique identifier for a tileset source.
    Limited to 32 characters. Only allows "-" and
    "_" as special characters.
    """

    value: str = Field(min_length=1, max_length=32, pattern=r"^[a-zA-Z0-9\_\-]*$")


class TilesetSourceFile(BaseModel):
    """A data file for a tileset source (i.e., raw
    geographic data formatted as line-delimited GeoJSON).
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    value: io.IOBase


class QueryParameter(BaseModel):
    """An abstract representation of a query parameter."""

    @computed_field
    @property
    @abstractmethod
    def name(self) -> str:
        """The parameter name."""
        raise NotImplementedError


class Token(QueryParameter):
    """The Mapbox API token used to authenticate."""

    @computed_field
    @property
    def name(self) -> str:
        """The parameter name."""
        return "access_token"

    value: str


class TilesetJobStage(QueryParameter):
    """Filters results by processing stage. Valid choices include:
    "processing", "queued", "success", "failed", or "superseded".
    """

    @computed_field
    @property
    def name(self) -> str:
        """The name of the query parameter."""
        return "stage"

    value: Optional[str] = Field(
        default=None,
        pattern=(r"^(processing)$|^(queued)$|^(success)$|^(failed)$|^(superseded)$"),
    )


class ResultSetLimit(QueryParameter):
    """An integer representing the pagination result size."""

    @computed_field
    @property
    def name(self) -> str:
        """The name of the query parameter."""
        return "limit"

    value: Optional[StrictInt] = Field(default=None, ge=1, le=500)


class ResultSetStart(QueryParameter):
    """A pagination start link."""

    @computed_field
    @property
    def name(self) -> str:
        """The name of the query parameter."""
        return "start"

    value: Optional[str] = None


class ResultSetTimestampSortBy(QueryParameter):
    """The name of a timestamp field used to sort pagination results."""

    @computed_field
    @property
    def name(self) -> str:
        """The name of the query parameter."""
        return "sortby"

    value: Optional[str] = Field(default=None, pattern=(r"^(created)$|^(modified)$"))


class TilesetType(QueryParameter):
    """The tileset type (i.e., "raster" or "vector")."""

    @computed_field
    @property
    def name(self) -> str:
        """The name of the query parameter."""
        return "type"

    value: Optional[str] = Field(default=None, pattern=(r"^(raster)$|^(vector)$"))


class TilesetVisibility(QueryParameter):
    """The tileset accessibility/visibility (i.e., `private` or `public`)."""

    @computed_field
    @property
    def name(self) -> str:
        """The name of the query parameter."""
        return "visibility"

    value: Optional[str] = Field(default=None, pattern=(r"^(private)$|^(public)$"))
