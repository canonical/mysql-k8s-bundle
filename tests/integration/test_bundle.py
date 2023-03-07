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
    get_application_name,
    get_primary_unit,
    get_process_pid,
    send_signal_to_pod_container_process,
)

MYSQL_CONTAINER_NAME = "mysql"
MYSQLD_PROCESS_NAME = "mysqld"
MODEL_CONFIG = {"logging-config": "<root>=INFO;unit=DEBUG"}

logger = logging.getLogger(__name__)


@pytest.mark.abort_on_fail
async def test_deploy_bundle(ops_test: OpsTest) -> None:
    """Deploy bundle."""
    await ops_test.model.set_config(MODEL_CONFIG)
    async with ops_test.fast_forward():
        await ops_test.model.deploy("./releases/latest/mysql-k8s-bundle.yaml", trust=True)

        await ops_test.model.wait_for_idle(apps=[MYSQL_APP], status="active", timeout=5 * 60)

        await ops_test.model.wait_for_idle(apps=[ROUTER_APP], status="waiting", timeout=5 * 60)


@pytest.mark.abort_on_fail
async def test_mysql_primary_switchover(ops_test: OpsTest):
    """Ensures writes continue after the primary is killed."""
    # Deploy application & relate to router
    await ops_test.model.deploy(
        APPLICATION_APP, application_name=APPLICATION_APP, num_units=1, channel="latest/edge"
    )
    await ops_test.model.relate(f"{APPLICATION_APP}:database", f"{ROUTER_APP}:database")
    logger.info("Waiting for applications to become active")
    await ops_test.model.wait_for_idle(
        apps=[MYSQL_APP, ROUTER_APP, APPLICATION_APP],
        status="active",
        raise_on_blocked=True,
        timeout=15 * 60,
    )
    # Start writes
    logger.info("Ensuring writes continue on all units")
    await ensure_all_units_continuous_writes_incrementing(ops_test)
    # Kill primary mysql
    mysql_units = ops_test.model.applications[MYSQL_APP].units
    primary = await get_primary_unit(ops_test, mysql_units[0], MYSQL_APP)
    # ensure all units in the cluster are online
    assert await ensure_n_online_mysql_members(
        ops_test, 3
    ), "The deployed mysql application is not fully online"

    mysql_pid = await get_process_pid(
        ops_test, primary.name, MYSQL_CONTAINER_NAME, MYSQLD_PROCESS_NAME
    )
    logger.info("Sending SIGKILL to primary mysql unit")
    await send_signal_to_pod_container_process(
        ops_test,
        primary.name,
        MYSQL_CONTAINER_NAME,
        MYSQLD_PROCESS_NAME,
        "SIGKILL",
    )
    # await ops_test.juju(
    #    "ssh", primary.name, f"--container {MYSQL_CONTAINER_NAME}", "sudo pkill -9 mysqld"
    # )

    # Wait for the SIGKILL above to take effect before continuing with test checks
    time.sleep(30)

    logger.info("Ensuring 3 online units")
    assert await ensure_n_online_mysql_members(
        ops_test, 3
    ), "The mysql application is not fully online after sending SIGKILL to primary"

    # ensure that the mysqld process got restarted and has a new process id
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

    # Ensure writes continue on all units except old primary
    mysql_units = [unit for unit in mysql_units if unit.name != primary.name]
    await ensure_all_units_continuous_writes_incrementing(ops_test, mysql_units)
    # Ensure writes continue on all units
    async with ops_test.fast_forward():
        await ops_test.model.wait_for_idle(
            apps=[MYSQL_APP, ROUTER_APP, APPLICATION_APP],
            status="active",
            raise_on_blocked=True,
            timeout=15 * 60,
        )
        await ensure_all_units_continuous_writes_incrementing(ops_test)


async def test_tls_connection(ops_test: OpsTest):
    """Ensures that the mysql application can be connected to over TLS."""
    test_app = await get_application_name(ops_test, APPLICATION_APP)

    test_app_unit = ops_test.model.applications[test_app].units[0]

    logger.info("Get current session cipher")
    action = await test_app_unit.run_action("get-session-ssl-cipher")
    result = await action.wait()

    cipher = result.results["cipher"]

    assert cipher == "TLS_AES_256_GCM_SHA384", "Cipher not set"
