import pytest
from common.logger import LoggerFactory
from django.conf import settings
from django.core.management import call_command
from tax_credit.models import Geography, GeographyType, TargetBonusAssoc

logger = LoggerFactory.get(__name__)

LOAD_DEPENDENT_TABLES_COMMAND = "load_dependent_tables"
LOAD_ASSOC_TABLES_COMMAND = "load_assoc_table2"

SIMPLE_CONFIG_PATH = (
    settings.PROJECT_DIR / "tests" / "test_configs" / "simple_config.yml"
)


def change_config(config_file_path):
    def decorator(func):
        def wrapper(*args, **kwargs):
            orig_settings = settings.CONFIG_FILE
            settings.CONFIG_FILE = config_file_path
            settings.DEBUG = True
            try:
                func(*args, **kwargs)
            finally:
                settings.CONFIG_FILE = orig_settings

        return wrapper

    return decorator


@pytest.mark.django_db(transaction=True)
@change_config(SIMPLE_CONFIG_PATH)
def test_load_base_tables_can_take_smoke_test_option():
    # smoke test with 10 items per page, 5 pages
    page_size = 2
    page_num = 2
    cmd = f"load_base_tables --smoke-test {page_size} {page_num}".split()
    call_command(*cmd)
    geography_type_ct = GeographyType.objects.count()
    logger.info(
        f"Geography type count afer loading with page size {page_size} and "
        f"batch count {page_num} : {geography_type_ct}"
    )
    assert geography_type_ct > 0
    assert geography_type_ct <= page_size * page_num


@pytest.mark.django_db(transaction=True)
@change_config(SIMPLE_CONFIG_PATH)
def test_load_dependent_tables_loads_something():
    # smoke test with 10 items per page, 5 pages
    base_cmd = "load_base_tables"
    call_command(base_cmd)
    dependent_cmd = LOAD_DEPENDENT_TABLES_COMMAND
    call_command(dependent_cmd)
    geography_ct = Geography.objects.count()
    logger.info(f"Geography count after loading : {geography_ct}")
    assert geography_ct > 0


@pytest.mark.django_db(transaction=True)
@change_config(SIMPLE_CONFIG_PATH)
def test_load_assoc_with_county_fips_match():
    # smoke test with 10 items per page, 5 pages
    base_cmd = "load_base_tables"
    call_command(base_cmd)

    dependent_cmd = LOAD_DEPENDENT_TABLES_COMMAND
    call_command(dependent_cmd)

    assoc_cmd = f"{LOAD_ASSOC_TABLES_COMMAND} --target county".split()
    call_command(*assoc_cmd)

    assoc_ct = TargetBonusAssoc.objects.count()
    logger.info(f"Association table count after loading : {assoc_ct}")
    assert assoc_ct > 0


@pytest.mark.django_db(transaction=True)
@change_config(SIMPLE_CONFIG_PATH)
def test_load_assoc_with_state_fips_match():
    base_cmd = "load_base_tables"
    call_command(base_cmd)

    dependent_cmd = f"{LOAD_DEPENDENT_TABLES_COMMAND}"
    call_command(*dependent_cmd.split())

    assoc_cmd = f"{LOAD_ASSOC_TABLES_COMMAND} --target state"
    call_command(*assoc_cmd.split())

    assoc_ct_li = TargetBonusAssoc.objects.filter(
        bonus_geography_type="rural_coop"
    ).count()
    assoc_ct_rc = TargetBonusAssoc.objects.filter(
        bonus_geography_type="rural_coop"
    ).count()

    assert assoc_ct_li > 0
    assert assoc_ct_rc > 0


def test_environment_set():
    env = settings.ENV
    logger.info(f"Test environment running : {env}")
    assert env
