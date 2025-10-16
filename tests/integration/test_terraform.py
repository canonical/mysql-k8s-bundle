#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Contains integration tests for the terraform module."""

import logging
import subprocess

import pytest
from pytest_operator.plugin import OpsTest

from .helpers import get_app_statuses

logger = logging.getLogger(__name__)

active_apps = [
    "mysql-k8s",
]
blocked_apps = [
    "mysql-router-k8s",
    "s3-integrator",
]

TIMEOUT = 20 * 60
SHORT_TIMEOUT = 5 * 60


async def ensure_statuses(ops_test: OpsTest) -> None:
    """Ensure expected statuses of applications."""
    logger.info(f"Waiting for active: {', '.join(active_apps)}")
    await ops_test.model.block_until(
        lambda: get_app_statuses(ops_test, active_apps) == {"active"},
        timeout=TIMEOUT,
    )

    if blocked_apps:
        logger.info(f"Waiting for blocked: {', '.join(blocked_apps)}")
        await ops_test.model.block_until(
            lambda: get_app_statuses(ops_test, blocked_apps) == {"blocked"},
            timeout=SHORT_TIMEOUT,
        )


@pytest.mark.abort_on_fail
@pytest.mark.group(1)
async def test_terraform_install(ops_test: OpsTest) -> None:
    """Install terraform binary."""
    logger.info("Installing terraform binary")
    subprocess.check_call(
        ["sudo", "snap", "install", "terraform", "--classic"],
    )


@pytest.mark.abort_on_fail
@pytest.mark.group(1)
async def test_terraform(ops_test: OpsTest) -> None:
    """Deploy terraform module with app."""
    logger.info("Deploying terraform module")
    subprocess.check_call(
        ["terraform", "init"],
        cwd="terraform",
    )
    subprocess.check_call(
        ["terraform", "apply", "-auto-approve", "-var", f"model={ops_test.model.name}"],
        cwd="terraform",
    )

    # Terraform deployed apps do not show right away.
    # We must wait before checking for their statuses.
    await ops_test.model.block_until(
        lambda: set(ops_test.model.applications) == {*active_apps, *blocked_apps},
        timeout=SHORT_TIMEOUT,
    )

    await ensure_statuses(ops_test)

    logger.info("Configuring s3-integrator credentials")
    await (
        ops_test.model.applications["s3-integrator"]
        .units[0]
        .run_action(
            action_name="sync-s3-credentials",
            **{"access-key": "access", "secret-key": "secret"},
        )
    )

    blocked_apps.remove("s3-integrator")
    active_apps.append("s3-integrator")
    await ensure_statuses(ops_test)
