#!/usr/bin/env python
# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Contains integration tests for the mysql-k8s-bundle."""

import itertools
import logging

import pytest
from pytest_operator.plugin import OpsTest

from .connector import MysqlConnector
from .helpers import get_credentials, get_unit_ip

waiting_apps = [
    "mysql-router-k8s",
]
active_apps = [
    "mysql-k8s",
    "self-signed-certificates",
    "sysbench",
]
blocked_apps = [
    "data-integrator",
    "grafana-agent-k8s",
    "mysql-router-data-integrator",
    "s3-integrator",
]

TIMEOUT = 20 * 60
SHORT_TIMEOUT = 5 * 60

logger = logging.getLogger(__name__)


async def ensure_statuses(ops_test: OpsTest) -> None:
    """Ensure expected statuses of applications."""
    logger.info(f"Waiting for active: {', '.join(active_apps)}")
    await ops_test.model.block_until(
        lambda: set([ops_test.model.applications[app].status for app in active_apps])
        == {"active"},
        timeout=TIMEOUT,
    )

    logger.info(f"Waiting for blocked: {', '.join(blocked_apps)}")
    await ops_test.model.block_until(
        lambda: set([ops_test.model.applications[app].status for app in blocked_apps])
        == {"blocked"},
        timeout=SHORT_TIMEOUT,
    )

    if waiting_apps:
        logger.info(f"Waiting for waiting: {', '.join(waiting_apps)}")
        await ops_test.model.block_until(
            lambda: set([ops_test.model.applications[app].status for app in waiting_apps])
            == {"waiting"},
            timeout=SHORT_TIMEOUT,
        )


@pytest.mark.abort_on_fail
async def test_smoke(ops_test: OpsTest) -> None:
    """Deploy bundle with apps and test various component integrations."""
    async with ops_test.fast_forward("5s"):
        logger.info("Deploying bundle")
        await ops_test.model.deploy("./releases/latest/mysql-k8s-bundle.yaml", trust=True)
        await ops_test.model.applications["mysql-k8s"].set_config({"profile": "testing"})
        await ensure_statuses(ops_test)

        logger.info("Configuring s3-integrator credentials")
        await ops_test.model.applications["s3-integrator"].units[0].run_action(
            action_name="sync-s3-credentials", **{"access-key": "access", "secret-key": "secret"}
        )

        blocked_apps.remove("s3-integrator")
        active_apps.append("s3-integrator")
        await ensure_statuses(ops_test)

        logger.info("Configuring data-integrator")
        await ops_test.model.applications["data-integrator"].set_config(
            {"database-name": "mysql-database"}
        )

        blocked_apps.remove("data-integrator")
        active_apps.append("data-integrator")
        await ensure_statuses(ops_test)

        logger.info("Confirming data-integrator's database exists")
        mysql_unit = ops_test.model.applications["mysql-k8s"].units[0]
        mysql_unit_address = await get_unit_ip(ops_test, mysql_unit.name)
        server_config_credentials = await get_credentials(mysql_unit, "serverconfig")

        database_config = {
            "user": server_config_credentials["username"],
            "password": server_config_credentials["password"],
            "host": mysql_unit_address,
            "raise_on_warnings": False,
        }

        with MysqlConnector(database_config, False) as cursor:
            cursor.execute("SHOW DATABASES;")
            databases = list(itertools.chain(*cursor.fetchall()))
            assert "mysql-database" in databases

        logger.info("Configuring mysql-router-data-integrator")
        await ops_test.model.applications["mysql-router-data-integrator"].set_config(
            {"database-name": "mysql-router-database"}
        )

        blocked_apps.remove("mysql-router-data-integrator")
        active_apps.append("mysql-router-data-integrator")

        waiting_apps.remove("mysql-router-k8s")
        active_apps.append("mysql-router-k8s")
        await ensure_statuses(ops_test)

        logger.info("Confirming data-integrator's database exists")
        with MysqlConnector(database_config, False) as cursor:
            cursor.execute("SHOW DATABASES;")
            databases = list(itertools.chain(*cursor.fetchall()))
            assert "mysql-router-database" in databases

        logger.info("Adding mysql-test-app unit")
        await ops_test.model.applications["mysql-test-app"].add_unit()

        waiting_apps.append("mysql-test-app")
        await ensure_statuses(ops_test)
