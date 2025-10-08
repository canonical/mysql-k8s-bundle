# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

output "app_names" {
  description = "Names of of all deployed applications."
  value = {
    mysql_server  = module.mysql_server.app_name
    mysql_router  = module.mysql_router.app_name
    certificates  = juju_application.certificates[0].name
    grafana_agent = juju_application.grafana_agent[0].name
  }
}

output "provides" {
  description = "Map of all the provided endpoints"
  value = {
    database = module.mysql_router.provides.database,
  }
}
