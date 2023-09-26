"""Enforce some rules about the structure of the test folder."""

from django.conf import settings


def test_data_dir_is_correct():
    # assert settings.BASE_DIR == "tests/data"
    pass


def test_database_is_sqlite():
    """
    The main reason for this test is to make sure that all other tests run against a local sqlite
    database and don't whipe out prod on accident.
    """
    assert settings.DATABASES["default"]["ENGINE"].endswith("sqlite3")
