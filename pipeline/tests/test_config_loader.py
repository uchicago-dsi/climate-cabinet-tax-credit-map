import pytest
from common.logger import LoggerFactory
from django.conf import settings
from tax_credit.config_reader import LoadConfigReader, get_load_config_reader
from tax_credit.load_job import LoadJob

logger = LoggerFactory.get(__name__)


def test_config_reader_cannot_be_created_directly():
    with pytest.raises(TypeError):
        LoadConfigReader()


def test_config_can_be_created_with_factory_function():
    filepath = (
        settings.PROJECT_DIR / "tests" / "test_configs" / "simple_config.yml"
    )
    assert isinstance(get_load_config_reader(filepath), LoadConfigReader)


def test_load_config_readers_are_the_same():
    filepath = (
        settings.PROJECT_DIR / "tests" / "test_configs" / "simple_config.yml"
    )
    assert get_load_config_reader(filepath) is get_load_config_reader(filepath)


def test_config_has_config_file_var():
    assert settings.CONFIG_FILE


def test_config_reader_can_get_sections():
    config_reader = get_load_config_reader(
        settings.PROJECT_DIR / "tests" / "test_configs" / "simple_config.yml"
    )
    base_jobs = config_reader.base_jobs
    dependent_jobs = config_reader.dependent_jobs
    assoc_jobs = config_reader.assoc_jobs
    logger.info(f"Config for base jobs : {base_jobs}")
    logger.info(f"Config for dependent jobs : {dependent_jobs}")
    logger.info(f"Config for assoc jobs : {assoc_jobs}")
    assert base_jobs is not None
    assert dependent_jobs is not None
    assert assoc_jobs is not None


def test_config_reader_can_create_a_load_job():
    config_reader = get_load_config_reader(
        settings.PROJECT_DIR / "tests" / "test_configs" / "simple_config.yml"
    )
    first_base_job = config_reader.base_jobs[0]
    assert isinstance(first_base_job, LoadJob)
    assert first_base_job.row_to_model is not None
    assert first_base_job.model is not None
