# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_application" "certificates" {
  count = local.tls_enabled ? 1 : 0

  charm {
    name     = "self-signed-certificates"
    base     = var.certificates.base
    channel  = var.certificates.channel
    revision = var.certificates.revision
  }

  model       = var.model
  name        = var.certificates.app_name
  config      = var.certificates.config
  constraints = var.certificates.constraints
  units       = var.certificates.units
}

resource "juju_application" "grafana_agent" {
  count = local.cos_enabled ? 1 : 0

  charm {
    name     = "grafana-agent-k8s"
    base     = var.grafana_agent.base
    channel  = var.grafana_agent.channel
    revision = var.grafana_agent.revision
  }

  model       = var.model
  name        = var.grafana_agent.app_name
  config      = var.grafana_agent.config
  constraints = var.grafana_agent.constraints
  units       = var.grafana_agent.units
}

resource "juju_application" "s3_integrator" {
  charm {
    name     = "s3-integrator"
    base     = var.s3_integrator.base
    channel  = var.s3_integrator.channel
    revision = var.s3_integrator.revision
  }

  model       = var.model
  name        = var.s3_integrator.app_name
  config      = var.s3_integrator.config
  constraints = var.s3_integrator.constraints
  units       = var.s3_integrator.units
}
