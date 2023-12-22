"""Clients for operations against the Mapbox API service.
"""

import io
import json
import os
import requests
import tempfile
import time
from types import TracebackType
from typing import Dict, List, Optional
from typing_extensions import Self, Type

from common.logger import logging
from common.storage import FileSystemHelperFactory
from django.conf import settings
from mapbox.fieldsets import *


class MapboxTilingApiClient:
    """Wrapper for API requests against the Mapbox Tiling Service (MTS).
    """

    def __init__(self) -> None:
        """Initializes a new instance of a `MapboxTilesetClient`.

        Args:
            `None`

        Raises:
            `KeyError` if the environment variables
                `MAPBOX_API_BASE_URL`, `MAPBOX_API_TOKEN`, 
                and `MAPBOX_USERNAME` do not exist.

        Returns:
            `None`
        """
        try:
            self._token = os.environ["MAPBOX_API_TOKEN"]
            self._base_url = os.environ["MAPBOX_API_BASE_URL"]
            self._username = os.environ["MAPBOX_USERNAME"]
        except KeyError as e:
            raise RuntimeError(
                "Failed to instantiate a MapboxTilesetClient. "
                f"Missing required environment variable \"{e}\"."
            )

    def _build_query_params(self, fields: BaseFieldset) -> Dict:
        """Builds HTTP URL query parameters for every model
        field that contains a "name" property.

        Args:
            fields (`BaseFieldset`): The Mapbox fields
                used in the request.

        Returns:
            (`dict`): The parameter key-value pairs.
        """
        params = {}
        for field in fields.model_dump().values():
            if "name" in field:
                params[field["name"]] = field["value"]
        return params

    def create_or_append_tileset_source(
        self,
        source_id: str,
        file: io.IOBase) -> Dict:
        """Creates a new tileset source from a data file or
        appends an additional file to the tileset source if it
        already exists. (The "create" and "append" endpoints described
        in the documentation appear to now be the same.) The API token
        must have a scope of "tilesets:write".
        
        Documentation:
            - ["Create a tileset source"](https://docs.mapbox.com/api/maps/mapbox-tiling-service/#create-a-tileset-source)
            - ["Example response: Create a tileset source"](https://docs.mapbox.com/api/maps/mapbox-tiling-service/#response-create-a-tileset-source)
            - ["Append to an existing tileset source"](https://docs.mapbox.com/api/maps/mapbox-tiling-service/#append-to-an-existing-tileset-source)
            - ["Example response: Append to an existing tileset source"](https://docs.mapbox.com/api/maps/mapbox-tiling-service/#append-to-an-existing-tileset-source)
        
        Args:
            source_id (`str`): The id for the tile source
                to be created. Limited to 32 characters
                and the only allowed special characters are
                "-" and "_".

            file (`io.IOBase`): The data file.

        Returns:
            (`dict`): Metadata for the newly-created tileset source.
        """
        # Validate fields used to build HTTP request
        fields = TilesetSourceCreateFieldset(
            token=Token(value=self._token),
            username=Username(value=self._username),
            source_id=TilesetSourceId(value=source_id),
            file=TilesetSourceFile(value=file)
        )
        
        # Build request URL
        url = (
            f"{self._base_url}/tilesets/v1/sources/"
            f"{fields.username.value}/{fields.source_id.value}"
        )

        # Build query parameters
        params = self._build_query_params(fields)

        # Make request
        r = requests.post(url, params=params, files={"file": fields.file.value})
        if not r.ok:
            raise RuntimeError(
                "The request to create a new tileset source "
                f"for user \"{fields.username.value}\" failed "
                f"with a \"{r.status_code} - {r.reason}\" "
                f"status code and the text \"{r.text}\"."
            )
        
        return r.json()
   
    def create_tileset(
        self,
        formal_name: str,
        display_name: str,
        source_id: str,
        layer_name: str,
        min_zoom: int,
        max_zoom: int) -> Dict:
        """Creates a new tileset on the Mapbox server side.

        Documentation:
        - ["Create a tileset"](https://docs.mapbox.com/api/maps/mapbox-tiling-service/#create-a-tileset)
        - ["Recipe Specification"](https://docs.mapbox.com/mapbox-tiling-service/reference/#layers)
        - ["Example request body: Create a tileset"](https://docs.mapbox.com/api/maps/mapbox-tiling-service/#example-request-body-create-a-tileset)
        - ["Response: Create a tileset"](https://docs.mapbox.com/api/maps/mapbox-tiling-service/#response-create-a-tileset)
        - ["Glossary: Zoom Level"](https://docs.mapbox.com/help/glossary/zoom-level/)

        Args:
            formal_name (`str`): The unique name of the tileset.
                Limited to 32 characters and only allows '-' 
                and '_' as special characters. Does not contain
                the "{username}." prefix.

            display_name (`str`): The descriptive name of
                the tileset. Limited to 64 characters.

            source_id (`str`): The id of a pre-existing 
                tileset source, from which the tileset 
                will be created.

            layer_name (`str`): The layer to include in
                the tileset. Must be a string with only
                underscores and alphanumeric characters.

            min_zoom (`int`): The minimum zoom level.
                Must be between 0 and 16, inclusive,
                and less than or equal to the `max_zoom`.

            max_zoom (`int`): The maximum zoom level.
                Must be between 0 and 16, inclusive.

        Returns:
            (`Dict`): Metadata containing a success message.
        """
        # Validate fields used to build HTTP request
        fields = TilesetCreateFieldset(
            token=Token(value=self._token),
            username=Username(value=self._username),
            display_name=TilesetDisplayName(value=display_name),
            formal_name=TilesetFormalName(value=formal_name),
            layer_name=TilesetLayerName(value=layer_name),
            max_zoom=TilesetZoom(value=max_zoom),
            min_zoom=TilesetZoom(value=min_zoom),
            source_id=TilesetSourceId(value=source_id)
        )

        # Build request URL
        url = (
            f"{self._base_url}/tilesets/v1/"
            f"{fields.username.value}.{fields.formal_name.value}"
        )       
        
        # Build request body
        body = {
            "recipe": {
                "version": 1,
                "layers": {
                   fields.layer_name.value: {
                        "source": (
                            "mapbox://tileset-source/"
                            f"{fields.username.value}/{fields.source_id.value}"
                        ),
                        "minzoom": fields.min_zoom.value,
                        "maxzoom": fields.max_zoom.value
                    }
                }
            },
            "name": fields.display_name.value
        }

        # Build query parameters
        params = self._build_query_params(fields)

        # Make request
        r = requests.post(url, params=params, json=body)
        if not r.ok:
            raise RuntimeError(
                "The request to create a new tileset "
                f"for user \"{fields.username.value}\" failed "
                f"with a \"{r.status_code} - {r.reason}\" "
                f"status scode and the text \"{r.text}\"."
            )
        
        return r.json()

    def delete_tileset(self, tileset_formal_name: str) -> None:
        """Permanently deletes a tileset.

        Documentation:
        - ["Delete tileset"](https://docs.mapbox.com/api/maps/mapbox-tiling-service/#delete-tileset)

        Args:
            tileset_formal_name (`str`): The id for the tileset to be deleted.

        Returns:
            (`None`)
        """
        # Validate fields used to build HTTP request
        fields = TilesetDeleteFieldset(
            token=Token(value=self._token),
            username=Username(value=self._username),
            tileset_formal_name=TilesetFormalName(value=tileset_formal_name)
        )

        # Build request URL
        url = (
            f"{self._base_url}/tilesets/v1/"
            f"{fields.username.value}.{fields.tileset_formal_name.value}"
        )

        # Build query parameters
        params = self._build_query_params(fields)

        # Make request
        r = requests.delete(url, params=params)
        if not r.ok:
            raise RuntimeError(
                "The request to delete the tileset "
                f"\"{fields.tileset_formal_name.value}\" for user \""
                f"{fields.username.value}\" failed with a "
                f"\"{r.status_code} - {r.reason}\" status "
                f"code and the text \"{r.text}\"."
            )  

    def delete_tileset_source(self, source_id: str) -> None:
        """Permanently deletes a tileset source and all of its
        files. This action is recommended if all related tileset
        publishing jobs have completed. Deleting tileset sources
        will not affect the published tilesets generated from them.

        Documentation:
        - ["Delete a tileset source"](https://docs.mapbox.com/api/maps/mapbox-tiling-service/#delete-a-tileset-source)
        - ["Append to an existing tileset source"](https://docs.mapbox.com/api/maps/mapbox-tiling-service/#append-to-an-existing-tileset-source) (See note)

        Args:
            source_id (`str`): The id for the tile source to be deleted.

        Returns:
            (`None`)
        """
        # Validate fields used to build HTTP request
        fields = TilesetSourceDeleteFieldset(
            token=Token(value=self._token),
            username=Username(value=self._username),
            source_id=TilesetSourceId(value=source_id)
        )

        # Build request URL
        url = (
            f"{self._base_url}/tilesets/v1/sources/"
            f"{fields.username.value}/{fields.source_id.value}"
        )

        # Build query parameters
        params = self._build_query_params(fields)

        # Make request
        r = requests.delete(url, params=params)
        if not r.ok:
            raise RuntimeError(
                "The request to delete the tileset source "
                f"\"{fields.source_id.value}\" for user \""
                f"{fields.username.value}\" failed with a \""
                f"{r.status_code} - {r.reason}\" status code "
                f"and the text \"{r.text}\"."
            )        

    def get_tilejson_metadata(self, tileset_formal_name: str) -> Dict:
        """Retrieves the TileJSON metadata for a given tileset.

        Documentation:
        - ["TileJSON Specification"]("https://github.com/mapbox/tilejson-spec/")
        - ["Retrieve TileJSON metadata"](https://docs.mapbox.com/api/maps/mapbox-tiling-service/#retrieve-tilejson-metadata)
        - ["Example response: Retrieve TileJSON metadata"](https://docs.mapbox.com/api/maps/mapbox-tiling-service/#example-response-retrieve-tilejson-metadata)

        Args:
            tileset_formal_name (`str`): The unique, formal name
                of the tileset.

        Returns:
            (`dict`): Metadata for the job.
        """
        # Validate fields used to build HTTP request
        fields = TilesetMetadataGetFieldset(
            token=Token(value=self._token),
            username=Username(value=self._username),
            tileset_formal_name=TilesetFormalName(value=tileset_formal_name)
        )

        # Build request URL
        url = (
            f"{self._base_url}/v4/{fields.username.value}."
            f"{fields.tileset_formal_name.value}.json"
        )

        # Build query parameters
        params = self._build_query_params(fields)

        # Make request
        r = requests.get(url, params=params)
        if not r.ok:
            raise RuntimeError(
                "The request to fetch TileJSON metadata for "
                f"tileset \"{fields.tileset_formal_name.value}\" "
                f"under user \"{fields.username.value}\" failed "
                f"with a \"{r.status_code} - {r.reason}\" status "
                f"code and the text \"{r.text}\"."
            )
        
        return r.json()

    def get_tileset_job(self, tileset_formal_name: str, job_id: str) -> Dict:
        """Retrieves the latest status of a tileset job.
        The API token must have a scope of "tilesets:read".

        Documentation:
        - ["Retrieve information about a single tileset job"](https://docs.mapbox.com/api/maps/mapbox-tiling-service/#retrieve-information-about-a-single-tileset-job)
        - ["Example response: Retrieve information about a single tileset job"](https://docs.mapbox.com/api/maps/mapbox-tiling-service/#example-response-retrieve-information-about-a-single-tileset-job)

        Args:
            tileset_formal_name (`str`): The unique, formal name
                of the tileset.

            job_id (`str`): The tileset processing job id.

        Returns:
            (`dict`): Metadata for the job.
        """
        # Validate fields used to build HTTP request
        fields = TilesetJobGetFieldset(
           token=Token(value=self._token),
           username=Username(value=self._username),
           tileset_formal_name=TilesetFormalName(value=tileset_formal_name),
           job_id=TilesetJobId(value=job_id)
        )

        # Build request URL
        url = (
            f"{self._base_url}/tilesets/v1/{fields.username.value}."
            f"{fields.tileset_formal_name.value}/jobs/{fields.job_id.value}"
        )

        # Build query parameters
        params = self._build_query_params(fields)

        # Make request
        r = requests.get(url, params=params)
        if not r.ok:
            raise RuntimeError(
                "The request to fetch tileset processing job "
                f"\"{fields.job_id.value}\" for tileset "
                f"\"{fields.tileset_formal_name.value}\" under user"
                f"\"{fields.username.value}\" failed with a "
                f"\"{r.status_code} - {r.reason}\" status "
                f"code and the text \"{r.text}\"."
            )
        
        return r.json()

    def list_tileset_jobs(
        self,
        tileset_formal_name: str,
        stage: Optional[str]=None,
        limit: Optional[int]=None,
        start: Optional[str]=None) -> List[Dict]:
        """Lists information about all jobs associated with
        a tileset in the current user account. The API token
        must have a scope of "tilesets:list".

        Documentation:
        - ["List information about all jobs for a tileset"](https://docs.mapbox.com/api/maps/mapbox-tiling-service/#list-information-about-all-jobs-for-a-tileset)
        - ["Example response: List information about all jobs for a tileset"](https://docs.mapbox.com/api/maps/mapbox-tiling-service/#example-response-list-information-about-all-jobs-for-a-tileset)
        - ["Pagination"](https://docs.mapbox.com/api/overview/#pagination)

        Args:
            tileset_formal_name (`str`): The unique, formal name of the tileset.

            stage (`str`): Filters results by processing stage.
                Valid choices include: "processing", "queued",
                "success", "failed", or "superseded".

            limit (`int`): The maximum number of tileset sources to
                return. Ranges from 1 to 500 and defaults to 100 on
                the Mapbox API server side.

            start (`str`): The tileset source after which to
                start the list. The key is found in the `Link`
                header of a response.

        Returns:
            (`list` of `dict`): A list of tileset job metadata objects.
        """
        # Validate fields used to build HTTP request
        fields = TilesetJobListFieldset(
           token=Token(value=self._token),
           username=Username(value=self._username),
           tileset_formal_name=TilesetFormalName(value=tileset_formal_name),
           stage=TilesetJobStage(value=stage),
           limit=ResultSetLimit(value=limit),
           start=ResultSetStart(value=start)
        )

        # Build request URL
        url = (
            f"{self._base_url}/tilesets/v1/{fields.username.value}."
            f"{fields.tileset_formal_name.value}/jobs"
        )

        # Build query parameters
        params = self._build_query_params(fields)

        # Make request
        r = requests.get(url, params=params)
        if not r.ok:
            raise RuntimeError(
                "The request to list tileset job metadata "
                f"for user \"{fields.username.value}\" failed "
                f"with \"{r.status_code} - {r.reason}\" status "
                f"code and the text \"{r.text}\"."
            )
        
        return r.json()

    def list_tileset_sources(
        self,
        sort_by: Optional[str]=None,
        limit: Optional[int]=None,
        start: Optional[str]=None) -> List[Dict]:
        """Lists the tileset sources that belong to the current user
        account. The API token must have a scope of "tilesets:list".

         Documentation:
        - ["List tileset sources"](https://docs.mapbox.com/api/maps/mapbox-tiling-service/#list-tileset-sources)
        - ["Example response: List tileset sources"](https://docs.mapbox.com/api/maps/mapbox-tiling-service/#example-response-list-tileset-sources)
        - ["Pagination"](https://docs.mapbox.com/api/overview/#pagination)

        Args:
            sort_by (`str`): Filters results by property
                (i.e., `created` or `modified` timestamps).

            limit (`int`): The maximum number of tileset sources to
                return. Ranges from 1 to 500 and defaults to 100 on
                the Mapbox API server side.

            start (`str`): The tileset source after which to
                start the list. The key is found in the `Link`
                header of a response.

        Returns:
            (`list` of `dict`): A list of tileset source objects.
        """
        # Validate fields used to build HTTP request
        fields = TilesetSourceListFieldset(
           token=Token(value=self._token),
           username=Username(value=self._username),
           sort_by=ResultSetTimestampSortBy(value=sort_by),
           limit=ResultSetLimit(value=limit),
           start=ResultSetStart(value=start)
        )

        # Build request URL
        url = f"{self._base_url}/tilesets/v1/sources/{fields.username.value}"

        # Build query parameters
        params = self._build_query_params(fields)

        # Make request
        r = requests.get(url, params=params)
        if not r.ok:
            raise RuntimeError(
                "The request to list tileset sources for user "
                f"\"{fields.username.value}\" failed with a "
                f"\"{r.status_code} - {r.reason}\" status "
                f"code and the text \"{r.text}\"."
            )
        
        return r.json()

    def list_tilesets(
        self,
        type: Optional[str]=None,
        visibility: Optional[str]=None,
        sort_by: Optional[str]=None,
        limit: Optional[int]=None,
        start: Optional[str]=None) -> List[Dict]:
        """Lists the tilesets that belong to the current user account.
        The API token must have a scope of "tilesets:list".

        Documentation:
        - ["List tilesets"](https://docs.mapbox.com/api/maps/mapbox-tiling-service/#list-tilesets)
        - ["Example response: List tilesets"](https://docs.mapbox.com/api/maps/mapbox-tiling-service/#example-response-list-tilesets)
        - ["Pagination"](https://docs.mapbox.com/api/overview/#pagination)

        Args:
            type (`str`): Filters results by tileset type
                (i.e., "raster" or "vector").

            visibility (`str`): Filters results by tileset
                visiblity (i.e., `private` or `public`).

            sort_by (`str`): Filters results by property
                (i.e., `created` or `modified` timestamps).

            limit (`int`): The maximum number of tilesets to return.
                Ranges from 1 to 500 and defaults to 100 on
                the Mapbox API server side.

            start (`str`): The tileset after which to start
                the list. The key is found in the `Link`
                header of a response.

        Returns:
            (`list` of `dict`): A list of tileset objects.
        """
        # Validate fields used to build HTTP request
        fields = TilesetListFieldset(
           token=Token(value=self._token),
           username=Username(value=self._username),
           type=TilesetType(value=type),
           visibility=TilesetVisibility(value=visibility),
           sort_by=ResultSetTimestampSortBy(value=sort_by),
           limit=ResultSetLimit(value=limit),
           start=ResultSetStart(value=start)
        )

        # Build request url
        url = f"{self._base_url}/tilesets/v1/{fields.username.value}"

        # Build query parameters
        params = self._build_query_params(fields)

        # Make request
        r = requests.get(url, params=params)
        if not r.ok:
            raise RuntimeError(
                "The request to list tilesets for user "
                f"\"{fields.username.value}\" failed with a "
                f"\"{r.status_code} - {r.reason}\" status "
                f"code and the text \"{r.text}\"."
            )

        return r.json()

    def publish_tileset(self, tileset_formal_name: str) -> Dict:
        """Publishes a tileset from its source, configured by a recipe.
        Starts a asynchronous processing job that can be monitored
        for completion. Requires an API token with the scope "tilesets:write".

        Documentation:
        - ["Publish a tileset"](https://docs.mapbox.com/api/maps/mapbox-tiling-service/#publish-a-tileset)
        - ["Response: Publish a tileset"](https://docs.mapbox.com/api/maps/mapbox-tiling-service/#response-publish-a-tileset)

        Args:
            tileset_formal_name (`str`): The unique, formal name of the tileset.

        Return:
            (`dict`): Metadata containing an informative message and job id.
        """
        # Validate fields used to build HTTP request
        fields = TilesetJobCreateFieldset(
           token=Token(value=self._token),
           username=Username(value=self._username),
           tileset_formal_name=TilesetFormalName(value=tileset_formal_name)
        )

        # Build request URL
        url = (
            f"{self._base_url}/tilesets/v1/{fields.username.value}."
            f"{fields.tileset_formal_name.value}/publish"
        )

        # Build query parameters
        params = self._build_query_params(fields)

        # Make request
        r = requests.post(url, params=params)
        if not r.ok:
            raise RuntimeError(
                "The request to publish the tileset "
                f"\"{fields.tileset_formal_name.value}\" for user "
                f"\"{fields.username.value}\" failed with a "
                f"\"{r.status_code} - {r.reason}\" status "
                f"code and the text \"{r.text}\"."
            )
        
        return r.json()

    def update_tileset_recipe(
        self,
        tileset_formal_name: str,
        source_id: str,
        layer_name: str,
        min_zoom: int,
        max_zoom: int) -> None:
        """Updates a pre-existing tileset recipe.

        Documentation:
        - ["Updates a tileset's recipe"](https://docs.mapbox.com/api/maps/mapbox-tiling-service/#update-a-tilesets-recipe)
        - ["Recipe Specification"](https://docs.mapbox.com/mapbox-tiling-service/reference/#layers)

        Args:
            tileset_formal_name (`str`): The unique, formal name of the tileset.

            source_id (`str`): The id of a 
                pre-existing tileset source, from which
                the tileset will be created.

            layer_name (`str`): The layer to include in
                the tileset. Must be a string with only
                underscores and alphanumeric characters.

            min_zoom (`int`): The minimum zoom level.
                Must be between 0 and 16, inclusive,
                and less than or equal to the `max_zoom`.

            max_zoom (`int`): The maximum zoom level.
                Must be between 0 and 16, inclusive.

        Returns:
            `None`
        """
         # Validate fields used to build HTTP request
        fields = TilesetRecipeUpdateFieldset(
           token=Token(value=self._token),
           username=Username(value=self._username),
           tileset_formal_name=TilesetFormalName(value=tileset_formal_name),
           source_id=TilesetSourceId(value=source_id),
           layer_name=TilesetLayerName(value=layer_name),
           max_zoom=TilesetZoom(value=max_zoom),
           min_zoom=TilesetZoom(value=min_zoom)
        )

        # Build request URL
        url = (
            f"{self._base_url}/tilesets/v1/{fields.username.value}."
            f"{fields.tileset_formal_name.value}/recipe"
        )

        # Build request body
        body = {
            "version": 1,
            "layers": {
                fields.layer_name.value: {
                    "source": (
                        "mapbox://tileset-source/"
                        f"{fields.username.value}/{fields.source_id.value}"
                    ),
                    "minzoom": fields.min_zoom.value,
                    "maxzoom": fields.max_zoom.value
                }
            }
        }

        # Build query parameters
        params = self._build_query_params(fields)

        # Make request
        r = requests.patch(url, params=params, json=body)
        if not r.ok:
            raise RuntimeError(
                "The request to update the tileset "
                f"\"{fields.tileset_formal_name.value}\" for user "
                f"\"{fields.username.value}\" failed with a "
                f"\"{r.status_code} - {r.reason}\" status "
                f"code and the text \"{r.text}\"."
            )

class MapboxTilesetSyncClient:
    """Orchestrates a data sync between one or more
    line-delimited GeoJSON files and Mapbox tilesets.
    """

    def __init__(self, logger: logging.Logger) -> None:
        """Initializes a new instance of a `MapboxTilesetSyncClient`.

        Args:
            logger (`logging.Logger`): An instance of a sstandard logger.
        
        Returns:
            `None`
        """
        self._client = MapboxTilingApiClient()
        self._file_helper = FileSystemHelperFactory.get()
        self._logger = logger

    def __enter__(self) -> Self:
        """Prepares for data syncing by deleting all current 
        tileset sources and taking an inventory of available tilesets.

        Args:
            `None`

        Returns:
            `None`
        """
        # Log start of setup process
        self._logger.info("Preparing for data sync.")

        # Delete all tileset sources
        self._logger.info("Deleting all tileset sources.")
        self._delete_tileset_sources()

        # Fetching existing tilesets
        self._logger.info("Fetching pre-existing tilesets.")
        self._tileset_names = [t["name"] for t in self._client.list_tilesets()]
        if self._tileset_names:
            self._logger.info(
                f"Found {len(self._tileset_names)} existing tileset(s) "
                f"on Mapbox server: {', '.join(self._tileset_names)}."
            )
        else:
            self._logger.info("No tilesets found.")
        
        return self

    def __exit__(
        self,
        type: Optional[Type[BaseException]],
        value: Optional[BaseException],
        traceback: Optional[TracebackType]) -> None:
        """Cleans up artifacts created by the data sync by
        deleting all tileset sources on the server side and
        then persists a snapshot of the tilesets by fetching
        and storing their TileJSON metadata.

        Args:
            type (`type` of `BaseException` | `None`): The exception type.

            value (`BaseException` | `None`): The exception instance.

            traceback (`TracebackType` | `None`): The exception traceback.

        Returns:
            `None`
        """
        # Log start of clean-up process
        self._logger.info("Beginning clean-up process.")

        # Delete all tileset sources
        self._logger.info("Deleting all tileset sources.")
        self._delete_tileset_sources()

        # Fetch metadata
        self._logger.info("Fetching tilesets' TileJSON metadata.")
        all_metadata = []
        for tileset in self._client.list_tilesets():
            tileset_formal_name = tileset["id"].split(".")[-1]
            metadata = self._client.get_tilejson_metadata(tileset_formal_name)
            all_metadata.append(metadata)

        # Write metadata to file
        self._logger.info("Persisting TileJSON metadata to file.")
        fpath = settings.MAPBOX_TILEJSON_METADATA_FILE
        with self._file_helper.open_file(fpath, "w") as f:
            json.dump(all_metadata, f, indent=4)
        
    def _append_tileset_source_file(self, source_id: str, fpath: str) -> None:
        """Appends a file to a tileset source.

         References:
        - ["Upload large source files to Mapbox Tiling Service"](https://docs.mapbox.com/help/troubleshooting/upload-large-source-files-mts/#split-the-file)

        Args:
            source_id (`str`): The unique identifier for
                the tileset source.

            fpath (`str`): The path to data file.

        Returns:
            `None`
        """
        # Log start of process
        self._logger.info(f"Opening tileset source file at \"{fpath}\".")
        
        # Initialize settings for limiting no. of GeoJSON lines sent to server
        batch_size = settings.MAPBOX_TILESET_SOURCE_BATCH_SIZE
        end_of_file = False

        # Process file
        with self._file_helper.open_file(fpath) as f:
            while not end_of_file:
                
                # Write temp file with line count up to batch size
                with tempfile.TemporaryDirectory() as temp_dir:
                    self._logger.info(
                        "Writing partial file contents to temp file."
                    )
                    tmp_fpath = f"{temp_dir}/tmp.geojsonl"
                    with open(tmp_fpath, "w") as tmp:
                        for _ in range(batch_size):
                            line = f.readline()
                            if not line:
                                end_of_file = True
                                break
                            tmp.write(line)
                            tmp.write("\n")

                    # Upload temp file to Mapbox tileset source
                    self._logger.info(f"Uploading temp file to Mapbox.")
                    with open(tmp_fpath, "r") as tmp:
                        self._client.create_or_append_tileset_source(
                            source_id=source_id,
                            file=tmp
                        )

    def _delete_tileset_sources(self) -> None:
        """Deletes all existing tileset sources on
        the Mapbox server side for the account given
        by environment variable settings.

        Args:
            `None`

        Returns:
            `None`
        """
        for source in self._client.list_tileset_sources():
            source_id = source["id"].split("/")[-1]
            self._logger.info(
                f"Deleting pre-existing tileset source \"{source_id}\"."
            )
            self._client.delete_tileset_source(source_id)

    def _monitor_tileset_publishing_job(
        self,
        tileset_formal_name: str,
        job_id: str) -> None:
        """Montitors a tileset publishing job until a terminal state is reached.

        Args:
            tileset_formal_name (`str`): The unique, formal name of the tileset.

            job_id (`str`): The unique identifier for the job.

        Returns:
            `None`
        """
        # Fetch publish delay from configuration settings
        delay = settings.MAPBOX_TILESET_PUBLISH_SECONDS_WAIT

        # Monitor until error or success occurs
        while True:

            # Add delay between calls
            self._logger.info(
                f"Sleeping for {str(delay)} second(s) before "
                "fetching updated publishing job status."
            )
            time.sleep(delay)
            
            # Fetch job status from API
            job = self._client.get_tileset_job(tileset_formal_name, job_id)

            # Handle indeterminate status
            if job["stage"] in ("processing", "queued"):
                self._logger.info(f"Job currently {job['stage']}.")
                continue

            # Handle success status
            elif job["stage"] == "success":
                self._logger.info(f"Tileset successfully published. {str(job)}")
                return
            
            # Handle superseded status
            elif job["stage"] == "superseded":
                self._logger.info("The job has been superseded by another.")
                return
            
            # Handle failure status
            elif job["stage"] == "failed":
                raise RuntimeError(
                    "Tileset publishing failed with "
                    f"{len(job['errors'])} errors. "
                    " ".join(e for e in job["errors"])
                )
            
            # Handle unknown status
            else:
                 raise RuntimeError(
                    "An unknown job status was encountered: "
                    f"\"{job['stage']}\"."
                )

    def _upsert_tileset(
        self,
        id: str,
        name: str,
        min_zoom: int,
        max_zoom: int) -> None:
        """Upserts a tileset using a tileset recipe 
        and reference to a tileset source.

        Args:
            id (`str`): The tileset id. Limited to 32
                characters and only allows '-' and '_' 
                as special characters.

            name (`str`): The tileset (display) name.
                Limited to 64 characters.

            min_zoom (`str`): The minimum zoom level.
                Must be between 0 and 16, inclusive, and 
                less than or equal to the maximum zoom.

            max_zoom (`str`): The maximum zoom level.
                Must be between 0 and 16, inclusive, and
                greater than or equal to the minimum zoom.
        
        Returns:
            `None`
        """
        # If tileset already exists, attempt update
        if name in self._tileset_names:
            self._logger.info(
                f"Updating existing tileset \"{name}\" using "
                "new recipe created from tileset source."
            )
            self._client.update_tileset_recipe(
                tileset_formal_name=id,
                source_id=id,
                layer_name=id,
                min_zoom=min_zoom,
                max_zoom=max_zoom
            )
            return
        
        # Otherwise, attempt insert
        self._logger.info(
            f"Creating existing tileset \"{name}\" using "
            "new recipe created from tileset source."
        )
        self._client.create_tileset(
            formal_name=id,
            display_name=name,
            source_id=id,
            layer_name=id,
            min_zoom=min_zoom,
            max_zoom=max_zoom
        )
     
    def sync_tileset(
        self,
        formal_name: str,
        display_name: str,
        min_zoom: int,
        max_zoom: int,
        files: List[str]) -> None:
        """Creates or updates a tileset with one or more data files
        and metadata (i.e., min and max zoom, name, and id).

        Args:
            formal_name (`str`): The unique, formal name 
                of the tileset, used internally by Mapbox.
                Limited to 32 characters and only allows 
                '-' and '_' as special characters.

            formal_name (`str`): The tileset's user-friendly
                display name. Limited to 64 characters.

            min_zoom (`str`): The minimum zoom level.
                Must be between 0 and 16, inclusive, and 
                less than or equal to the maximum zoom.

            max_zoom (`str`): The maximum zoom level.
                Must be between 0 and 16, inclusive, and
                greater than or equal to the minimum zoom.

            files (`list` of `str`): The paths to the
                line-delimited GeoJSON files used to
                populate the tileset.

        Returns:
            `None`
        """
        # Log start of data sync
        self._logger.info(f"Syncing tileset \"{display_name}\".")

        # Upload tileset source files
        self._logger.info(
            f"Adding data files to tileset source \"{formal_name}\"."
        )
        for pth in files:
            try:
                self._append_tileset_source_file(formal_name, pth)
            except Exception as e:
                raise RuntimeError("Error appending files to "
                                   f"tileset source. {e}") from None

        # Create new tileset (without publishing) or update tileset if exists
        try:
            self._upsert_tileset(formal_name, display_name, min_zoom, max_zoom)
        except Exception as e:
                raise RuntimeError(f"Error upserting tileset. {e}") from None
        
         # Queue new job to publish tileset
        try:
            self._logger.info("Publishing tileset on Mapbox.")
            queued_job = self._client.publish_tileset(formal_name)
            job_id = queued_job["jobId"]
        except Exception as e:
            raise RuntimeError("Failed to queue tileset publishing "
                               f"job. {e}") from None

        # Monitor job until terminal state reached
        try:
            self._logger.info(f"Publishing job queued with id \"{job_id}\".")
            self._monitor_tileset_publishing_job(formal_name, job_id)
        except Exception as e:
            raise RuntimeError(f"Failed to publish tileset. {e}") from None
        
