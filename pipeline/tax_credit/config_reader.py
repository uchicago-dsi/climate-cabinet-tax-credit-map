import importlib
from abc import ABC, abstractmethod, abstractproperty
from functools import lru_cache

import yaml
from tax_credit.load_job import AssocJob, LoadJob


class LoadConfigReader(ABC):
    """Class that reads the config for the dataload. The config cannot be modified at runtime. It is read once and executed."""

    @abstractmethod
    def __init__(self, filename):
        # raise NotImplementedError()
        pass

    @abstractproperty
    def base_jobs(self):
        pass

    @abstractproperty
    def dependent_jobs(self):
        pass

    @abstractproperty
    def assoc_jobs(self):
        pass


class _LoadConfigReaderImpl(LoadConfigReader):
    def __init__(self, filename):
        with open(filename, "r") as stream:
            self._config = yaml.safe_load(stream)
        self._base = self._config["base"] or {}
        self._dependent = self._config["dependent"] or {}
        self._assoc = self._config["assoc"] or {}

    @property
    def base_jobs(self) -> list[LoadJob]:
        base_jobs = []
        for job_name, job_details in self._base.items():
            base_jobs.append(parse_config_to_load_job(job_name, job_details))
        return base_jobs

    @property
    def dependent_jobs(self) -> list[LoadJob]:
        dependent_jobs = []
        for job_name, job_details in self._dependent.items():
            dependent_jobs.append(
                parse_config_to_load_job(job_name, job_details)
            )
        return dependent_jobs

    @property
    def assoc_jobs(self) -> list[AssocJob]:
        assoc_jobs = []
        for job_name, job_details in self._assoc.items():
            assoc_jobs.append(
                AssocJob(
                    job_name=job_name,
                    active=bool(job_details["active"]),
                    model=retrieve_class_from_string(job_details["model"]),
                    target=job_details["target"],
                    bonus=job_details["bonus"],
                    assoc_strategy=job_details["assoc_strategy"],
                    build_row_fn=None,
                    unique_fields=job_details["db_field_unique"],
                    update_fields=job_details["db_field_update"],
                )
            )
        return assoc_jobs


# TODO fix this
@lru_cache
def get_load_config_reader(filename):
    return _LoadConfigReaderImpl(filename)


def retrieve_class_from_string(class_str):
    module = importlib.import_module(class_str.split(":")[0])
    clazz = getattr(module, class_str.split(":")[1])
    return clazz


def retrieve_fn_from_string(fn_str):
    module = importlib.import_module(fn_str.split(":")[0])
    fn = getattr(module, fn_str.split(":")[1])
    return fn


def parse_config_to_load_job(job_name, job_details):
    return LoadJob(
        job_name=job_name,
        active=bool(job_details["active"]),
        filename=job_details["filename"],
        model=retrieve_class_from_string(job_details["model"]),
        file_format=job_details["file_format"],
        row_to_model=retrieve_fn_from_string(job_details["row_transform"]),
        file_field_names=job_details["file_field_required"],
        required_models=map(
            lambda m: retrieve_class_from_string(m),
            job_details.get("required_model", []),
        ),
        unique_fields=job_details["db_field_unique"],
        update_fields=job_details["db_field_update"],
        delimiter=job_details.get("delimiter", "|"),
    )
