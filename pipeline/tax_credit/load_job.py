from abc import ABC
from dataclasses import dataclass
from typing import Any, Callable, Type

from django.db.models import Model


@dataclass
class LoadJob(ABC):
    """
    Class holding information about a data base load job. Includes information regarding required
    files and validation prior to starting the job.
    """

    job_name: str

    # Connection between file and database
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


@dataclass
class FileLoadJob(LoadJob):
    file_name: str
    delimiter: str = "|"
