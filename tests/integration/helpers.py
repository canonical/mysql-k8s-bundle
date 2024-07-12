# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

from typing import Dict

from juju.unit import Unit
from pytest_operator.plugin import OpsTest


async def get_unit_ip(ops_test: OpsTest, unit_name: str) -> str:
    """Get unit IP address."""
    status = await ops_test.model.get_status()
    return status["applications"][unit_name.split("/")[0]].units[unit_name]["address"]


async def get_credentials(unit: Unit, username: str) -> Dict:
    """Helper to run an action to retrieve server config credentials."""
    action = await unit.run_action(action_name="get-password", username=username)
    result = await action.wait()
    return result.results
