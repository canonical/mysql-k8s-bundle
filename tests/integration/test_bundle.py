#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

"""Contains integration tests for the mysql-k8s-bundle."""

import logging

from pytest_operator.plugin import OpsTest

logger = logging.getLogger(__name__)


async def test_placeholder(ops_test: OpsTest) -> None:
    """A placeholder for an integration test to be implemented."""
    assert True
