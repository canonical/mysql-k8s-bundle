#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

"""Contains integration tests for the mysql-k8s-bundle."""

import logging

from pytest_operator.plugin import OpsTest

from tests.integration.constants import MYSQL_APP, ROUTER_APP, TLS_APP

logger = logging.getLogger(__name__)


async def test_deploy_bundle(ops_test: OpsTest) -> None:
    """Deploy bundle."""

    async with ops_test.fast_forward():
        await ops_test.model.deploy("./releases/latest/mysql-k8s-bundle.yaml")

        await ops_test.model.wait_for_idle(
            app=[MYSQL_APP, ROUTER_APP, TLS_APP], status="active", timeout=5 * 60
        )
