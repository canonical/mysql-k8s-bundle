# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

# INTEGRATIONS FOR THE OWNED COMPONENTS

resource "juju_integration" "mysql_server_router" {
  model = var.model

  application {
    name     = module.mysql_server.app_name
    endpoint = module.mysql_server.provides.database
  }
  application {
    name     = module.mysql_router.app_name
    endpoint = module.mysql_router.requires.backend_database
  }
}

# INTEGRATIONS FOR THE MYSQL SERVER CHARM

resource "juju_integration" "mysql_server_s3_integrator" {
  model = var.model

  application {
    name     = module.mysql_server.app_name
    endpoint = module.mysql_server.requires.s3_parameters
  }
  application {
    name     = juju_application.s3_integrator.name
    endpoint = "s3-credentials"
  }
}

resource "juju_integration" "mysql_server_certificates" {
  count = local.tls_enabled && var.mysql_server.units > 0 ? 1 : 0
  model = var.model

  application {
    name     = module.mysql_server.app_name
    endpoint = module.mysql_server.requires.certificates
  }
  application {
    name     = juju_application.certificates[0].name
    endpoint = "certificates"
  }
}

resource "juju_integration" "mysql_server_cos_dashboard" {
  count = local.cos_enabled && var.mysql_server.units > 0 ? 1 : 0
  model = var.model

  application {
    name     = module.mysql_server.app_name
    endpoint = module.mysql_server.provides.grafana_dashboard
  }
  application {
    name     = juju_application.grafana_agent[0].name
    endpoint = "grafana-dashboards-consumer"
  }
}

resource "juju_integration" "mysql_server_cos_metrics" {
  count = local.cos_enabled && var.mysql_server.units > 0 ? 1 : 0
  model = var.model

  application {
    name     = module.mysql_server.app_name
    endpoint = module.mysql_server.provides.metrics_endpoint
  }
  application {
    name     = juju_application.grafana_agent[0].name
    endpoint = "metrics-endpoint"
  }
}

# INTEGRATIONS FOR THE MYSQL ROUTER CHARM

resource "juju_integration" "mysql_router_certificates" {
  count = local.tls_enabled && var.mysql_router.units > 0 ? 1 : 0
  model = var.model

  application {
    name     = module.mysql_router.app_name
    endpoint = module.mysql_router.requires.certificates
  }
  application {
    name     = juju_application.certificates[0].name
    endpoint = "certificates"
  }
}

resource "juju_integration" "mysql_router_cos_dashboard" {
  count = local.cos_enabled && var.mysql_router.units > 0 ? 1 : 0
  model = var.model

  application {
    name     = module.mysql_router.app_name
    endpoint = module.mysql_router.provides.grafana_dashboard
  }
  application {
    name     = juju_application.grafana_agent[0].name
    endpoint = "grafana-dashboards-consumer"
  }
}

resource "juju_integration" "mysql_router_cos_metrics" {
  count = local.cos_enabled && var.mysql_router.units > 0 ? 1 : 0
  model = var.model

  application {
    name     = module.mysql_router.app_name
    endpoint = module.mysql_router.provides.metrics_endpoint
  }
  application {
    name     = juju_application.grafana_agent[0].name
    endpoint = "metrics-endpoint"
  }
}
