"""Classes and functions enabling the deployment of cloud infrastructure.
"""

import requests
import subprocess


class GcloudSqlClient:
    """ """

    def __init__(self) -> None:
        """"""

    def create_server(
        self,
        project_id,
        instance_id: str,
        region: str,
        db_version: str,
        password: str,
        tier: str,
        edition: str,
    ):
        """
        References:
        - https://cloud.google.com/sql/docs/postgres/instance-settings#settings-2ndgen
        """
        payload = {
            "name": instance_id,
            "region": region,
            "databaseVersion": db_version,
            "rootPassword": password,
            "settings": {
                "tier": tier,
                "edition": edition,
                "enableGoogleMlIntegration": False,
                "databaseFlags": [],
                "dataCacheConfig": {
                    "dataCacheEnabled": False,
                },
                "backupConfiguration": {"enabled": True},
                "passwordValidationPolicy": None,
                "ipConfiguration": {
                    "privateNetwork": None,
                    "authorizedNetworks": [],
                    "ipv4Enabled": False,
                    "enablePrivatePathForGoogleCloudServices": True,
                },
            },
        }


if __name__ == "__main__":
    client = GcloudSqlClient()
    config = {
        "project_id": "climate-cabinet-398217",
        "instance_id": "climate-cabinet-sql-temp-12345",
        "region": "us-central1",
        "db_version": "PostgreSQL 14",
        "password": "p@ssw0rd!123",
        "tier": "db-f1-micro",
        "edition": "Enterprise",
    }
    response = client.create_server(**config)
    print(response)
