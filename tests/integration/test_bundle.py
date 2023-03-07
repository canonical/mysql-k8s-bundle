#!/usr/bin/env python
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

"""Contains integration tests for the mysql-k8s-bundle."""

import logging
import time

import pytest
from pytest_operator.plugin import OpsTest

from tests.integration.constants import APPLICATION_APP, MYSQL_APP, ROUTER_APP
from tests.integration.helpers import (
    ensure_all_units_continuous_writes_incrementing,
    ensure_n_online_mysql_members,
    get_primary_unit,
    get_process_pid,
    send_signal_to_pod_container_process,
)

MYSQL_CONTAINER_NAME = "mysql"
MYSQLD_PROCESS_NAME = "mysqld"

logger = logging.getLogger(__name__)


@pytest.mark.abort_on_fail
async def test_deploy_bundle(ops_test: OpsTest) -> None:
    """Deploy bundle."""
    async with ops_test.fast_forward():
        logger.info(f"Deploy MySQL K8s bundle and wait for up and running")
        await ops_test.model.deploy("./releases/latest/mysql-k8s-bundle.yaml", trust=True)
        await ops_test.model.wait_for_idle(apps=[ROUTER_APP], status="waiting", timeout=5 * 60)
        await ops_test.model.wait_for_idle(apps=[MYSQL_APP], status="active", timeout=15 * 60)


async def test_mysql_primary_switchover(ops_test: OpsTest):
    """Ensures writes continue after the primary is killed."""
    logger.info(f"Deploy {APPLICATION_APP} & relate to {ROUTER_APP}")
    await ops_test.model.deploy(APPLICATION_APP)
    await ops_test.model.relate(f"{APPLICATION_APP}:database", f"{ROUTER_APP}:database")
    await ops_test.model.wait_for_idle(
        apps=[MYSQL_APP, ROUTER_APP, APPLICATION_APP],
        status="active",
        raise_on_blocked=True,
        timeout=15 * 60,
    )
    logger.info("Start continuous writes")
    await ensure_all_units_continuous_writes_incrementing(ops_test)
    logger.info("Killing primary mysql")
    mysql_units = ops_test.model.applications[MYSQL_APP].units
    primary = await get_primary_unit(ops_test, mysql_units[0], MYSQL_APP)
    logger.info("Ensure all units in the cluster are online")
    assert await ensure_n_online_mysql_members(
        ops_test, 3
    ), "The deployed mysql application is not fully online"

    mysql_pid = await get_process_pid(
        ops_test, primary.name, MYSQL_CONTAINER_NAME, MYSQLD_PROCESS_NAME
    )

    await send_signal_to_pod_container_process(
        ops_test,
        primary.name,
        MYSQL_CONTAINER_NAME,
        MYSQLD_PROCESS_NAME,
        "SIGKILL",
    )

    logger.info("Wait for the SIGKILL above to take effect before continuing with checks")
    time.sleep(10)

    assert await ensure_n_online_mysql_members(
        ops_test, 3
    ), "The mysql application is not fully online after sending SIGKILL to primary"

    logger.info("Ensure the mysqld process got restarted and has a new process id")
    new_mysql_pid = await get_process_pid(
        ops_test, primary.name, MYSQL_CONTAINER_NAME, MYSQLD_PROCESS_NAME
    )
    assert (
        mysql_pid != new_mysql_pid
    ), "The mysql process id is the same after sending it a SIGKILL"

    new_primary = await get_primary_unit(ops_test, mysql_units[0], MYSQL_APP)
    assert (
        primary.name != new_primary.name
    ), "The mysql primary has not been reelected after sending a SIGKILL"

    logger.info("Ensure writes continue on all units except old primary")
    mysql_units = [unit for unit in mysql_units if unit.name != primary.name]
    await ensure_all_units_continuous_writes_incrementing(ops_test, mysql_units)

logger.info("Ensure writes continue on all units")
    async with ops_test.fast_forward():
        await ops_test.model.wait_for_idle(
            apps=[MYSQL_APP, ROUTER_APP, APPLICATION_APP],
            status="active",
            raise_on_blocked=True,
            timeout=15 * 60,
        )
        await ensure_all_units_continuous_writes_incrementing(ops_test)
