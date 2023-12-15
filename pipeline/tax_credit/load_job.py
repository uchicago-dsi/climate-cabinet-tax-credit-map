from dataclasses import dataclass
from typing import Any, Callable, Type

from django.db.models import Model


@dataclass
class LoadJob:
    """Class holding information about a data base load job. Includes information regarding required files and validation prior to starting the job."""

    job_name: str
    active: bool

    # Connection between file and database
    filename: str
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

    delimiter: str = "|"

    # Note that when loading, a final pitfall is foreign keys -- this can't be readily checked until load time


@dataclass
class AssocJob:
    job_name: str
    active: bool
    model: Type[Model]

    target: str
    bonus: str

    assoc_strategy: str

    build_row_fn: Callable[[dict[str, Any]], Model]

    unique_fields: list[str]
    update_fields: list[str]
