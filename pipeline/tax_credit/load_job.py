from typing import Callable, Any, Type
import os
from dataclasses import dataclass

from django.conf import settings
from django.db.models import Model


@dataclass
class LoadJob:
    """Class holding information about a data base load job. Includes information regarding required files and validation prior to starting the job."""
    job_name: str

    # Connection between file and database
    file_name: str
    model: Type[Model]
    file_format: str

    # Instrictions for mapping -- should be static
    row_to_model: Callable[[dict[str, Any]], Model]

    # Info for validation
    file_field_names: list[str]
    required_models: list[Model]

    # Info for loading
    unique_fields: list[str]
    update_fields: list[str]

    delimiter: str = '|'

    # Note that when loading, a final pitfall is foreign keys -- this can't be readily checked until load time
