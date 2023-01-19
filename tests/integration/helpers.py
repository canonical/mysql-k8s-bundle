# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
import itertools
from typing import Dict, List, Optional

import mysql.connector
from juju.unit import Unit
from pytest_operator.plugin import OpsTest
from tenacity import Retrying, stop_after_delay, wait_fixed

SERVER_CONFIG_USERNAME = "serverconfig"
DATABASE_NAME = "continuous_writes_database"
TABLE_NAME = "data"


# Copied from https://github.com/canonical/mysql-k8s-operator/blob/51ca494daf62ef9f1aa787d3ff97a52607f21c78/tests/integration/helpers.py
async def get_unit_address(ops_test: OpsTest, unit_name: str) -> str:
    """Get unit IP address.
    Args:
        ops_test: The ops test framework instance
        unit_name: The name of the unit
    Returns:
        IP address of the unit
    """
    status = await ops_test.model.get_status()
    return status["applications"][unit_name.split("/")[0]].units[unit_name]["address"]


async def get_cluster_status(ops_test: OpsTest, unit: Unit) -> Dict:
    """Get the cluster status by running the get-cluster-status action.
    Args:
        ops_test: The ops test framework
        unit: The unit on which to execute the action on
    Returns:
        A dictionary representing the cluster status
    """
    get_cluster_status_action = await unit.run_action("get-cluster-status")
    cluster_status_results = await get_cluster_status_action.wait()
    return cluster_status_results.results.get("status", {})


async def get_primary_unit(
    ops_test: OpsTest,
    unit: Unit,
    app_name: str,
) -> str:
    """Helper to retrieve the primary unit.
    Args:
        ops_test: The ops test object passed into every test case
        unit: A unit on which to execute commands/queries/actions on
        app_name: The name of the test application
    Returns:
        A juju unit that is a MySQL primary
    """
    cluster_status = await get_cluster_status(ops_test, unit)

    primary_label = [
        label
        for label, member in cluster_status["defaultreplicaset"]["topology"].items()
        if member["mode"] == "r/w"
    ][0]
    primary_name = "/".join(primary_label.rsplit("-", 1))

    for unit in ops_test.model.applications[app_name].units:
        if unit.name == primary_name:
            return unit

    return None


async def execute_queries_on_unit(
    unit_address: str,
    username: str,
    password: str,
    queries: List[str],
    commit: bool = False,
) -> List:
    """Execute given MySQL queries on a unit.
    Args:
        unit_address: The public IP address of the unit to execute the queries on
        username: The MySQL username
        password: The MySQL password
        queries: A list of queries to execute
        commit: A keyword arg indicating whether there are any writes queries
    Returns:
        A list of rows that were potentially queried
    """
    connection = mysql.connector.connect(
        host=unit_address,
        user=username,
        password=password,
    )
    cursor = connection.cursor()

    for query in queries:
        cursor.execute(query)

    if commit:
        connection.commit()

    output = list(itertools.chain(*cursor.fetchall()))

    cursor.close()
    connection.close()

    return output


async def get_server_config_credentials(unit: Unit) -> Dict:
    """Helper to run an action to retrieve server config credentials.
    Args:
        unit: The juju unit on which to run the get-password action for server-config credentials
    Returns:
        A dictionary with the server config username and password
    """
    action = await unit.run_action(action_name="get-password", username=SERVER_CONFIG_USERNAME)
    result = await action.wait()

    return result.results


async def get_process_pid(
    ops_test: OpsTest, unit_name: str, container_name: str, process: str
) -> int:
    """Return the pid of a process running in a given unit.
    Args:
        ops_test: The ops test object passed into every test case
        unit_name: The name of the unit
        container_name: The name of the container in the unit
        process: The process name to search for
    Returns:
        A integer for the process id
    """
    get_pid_commands = [
        "ssh",
        "--container",
        container_name,
        unit_name,
        "pgrep",
        process,
    ]
    return_code, pid, _ = await ops_test.juju(*get_pid_commands)

    assert (
        return_code == 0
    ), f"Failed getting pid, unit={unit_name}, container={container_name}, process={process}"

    stripped_pid = pid.strip()
    if not stripped_pid:
        return -1

    return int(stripped_pid)


# Copied from https://github.com/canonical/mysql-k8s-operator/blob/51ca494daf62ef9f1aa787d3ff97a52607f21c78/tests/integration/high_availability/high_availability_helpers.py
async def get_max_written_value_in_database(ops_test: OpsTest, unit: Unit) -> int:
    """Retrieve the max written value in the MySQL database.
    Args:
        ops_test: The ops test framework
        unit: The MySQL unit on which to execute queries on
    """
    server_config_credentials = await get_server_config_credentials(unit)
    unit_address = await get_unit_address(ops_test, unit.name)

    select_max_written_value_sql = [f"SELECT MAX(number) FROM `{DATABASE_NAME}`.`{TABLE_NAME}`;"]

    output = await execute_queries_on_unit(
        unit_address,
        server_config_credentials["username"],
        server_config_credentials["password"],
        select_max_written_value_sql,
    )

    return output[0]


async def get_application_name(ops_test: OpsTest, application_name: str) -> str:
    """Returns the name of the application with the provided application name.
    This enables us to retrieve the name of the deployed application in an existing model.
    Note: if multiple applications with the application name exist,
    the first one found will be returned.
    """
    status = await ops_test.model.get_status()

    for application in ops_test.model.applications:
        # note that format of the charm field is not exactly "mysql" but instead takes the form
        # of `local:focal/mysql-6`
        if application_name in status["applications"][application]["charm"]:
            return application

    return None


async def ensure_n_online_mysql_members(
    ops_test: OpsTest, number_online_members: int, mysql_units: Optional[List[Unit]] = None
) -> bool:
    """Waits until N mysql cluster members are online.
    Args:
        ops_test: The ops test framework
        number_online_members: Number of online members to wait for
        mysql_units: Expected online mysql units
    """
    mysql_application = await get_application_name(ops_test, "mysql")

    if not mysql_units:
        mysql_units = ops_test.model.applications[mysql_application].units
    mysql_unit = mysql_units[0]

    try:
        for attempt in Retrying(stop=stop_after_delay(5 * 60), wait=wait_fixed(10)):
            with attempt:
                cluster_status = await get_cluster_status(ops_test, mysql_unit)
                online_members = [
                    label
                    for label, member in cluster_status["defaultreplicaset"]["topology"].items()
                    if member["status"] == "online"
                ]
                assert len(online_members) == number_online_members
                return True
    except RetryError:
        return False


async def send_signal_to_pod_container_process(
    ops_test: OpsTest, unit_name: str, container_name: str, process: str, signal_code: str
) -> None:
    """Send the specified signal to a pod container process.
    Args:
        ops_test: The ops test framework
        unit_name: The name of the unit to send signal to
        container_name: The name of the container to send signal to
        process: The name of the process to send signal to
        signal_code: The code of the signal to send
    """
    kubernetes.config.load_kube_config()

    pod_name = unit_name.replace("/", "-")

    send_signal_command = f"pkill --signal {signal_code} -f {process}"
    response = kubernetes.stream.stream(
        kubernetes.client.api.core_v1_api.CoreV1Api().connect_get_namespaced_pod_exec,
        pod_name,
        ops_test.model.info.name,
        container=container_name,
        command=send_signal_command.split(),
        stdin=False,
        stdout=True,
        stderr=True,
        tty=False,
        _preload_content=False,
    )
    response.run_forever(timeout=5)

    assert (
        response.returncode == 0
    ), f"Failed to send {signal_code} signal, unit={unit_name}, container={container_name}, process={process}"


async def ensure_all_units_continuous_writes_incrementing(
    ops_test: OpsTest, mysql_units: Optional[List[Unit]] = None
) -> None:
    """Ensure that continuous writes is incrementing on all units.
    Also, ensure that all continuous writes up to the max written value is available
    on all units (ensure that no committed data is lost).
    """
    mysql_application_name = await get_application_name(ops_test, "mysql")

    if not mysql_units:
        mysql_units = ops_test.model.applications[mysql_application_name].units

    primary = await get_primary_unit(ops_test, mysql_units[0], mysql_application_name)

    last_max_written_value = await get_max_written_value_in_database(ops_test, primary)

    select_all_continuous_writes_sql = [f"SELECT * FROM `{DATABASE_NAME}`.`{TABLE_NAME}`"]
    server_config_credentials = await get_server_config_credentials(mysql_units[0])

    async with ops_test.fast_forward():
        for attempt in Retrying(stop=stop_after_delay(2 * 60), wait=wait_fixed(10)):
            with attempt:
                # ensure that all units are up to date (including the previous primary)
                for unit in mysql_units:
                    unit_address = await get_unit_address(ops_test, unit.name)

                    # ensure the max written value is incrementing (continuous writes is active)
                    max_written_value = await get_max_written_value_in_database(ops_test, unit)
                    assert (
                        max_written_value > last_max_written_value
                    ), "Continuous writes not incrementing"

                    # ensure that the unit contains all values up to the max written value
                    all_written_values = await execute_queries_on_unit(
                        unit_address,
                        server_config_credentials["username"],
                        server_config_credentials["password"],
                        select_all_continuous_writes_sql,
                    )
                    for number in range(1, max_written_value):
                        assert (
                            number in all_written_values
                        ), f"Missing {number} in database for unit {unit.name}"

                    last_max_written_value = max_written_value
