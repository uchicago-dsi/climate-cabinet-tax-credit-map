from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Type

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
    row_to_model: Callable[[Dict[str, Any]], Model]

    # Info for validation
    file_field_names: List[str]
    required_models: List[Model]

    # Info for loading
    unique_fields: List[str]
    update_fields: List[str]

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
    build_row_fn: Callable[[Dict[str, Any]], Model]
    unique_fields: List[str]
    update_fields: List[str]
