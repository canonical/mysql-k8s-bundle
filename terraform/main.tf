# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

locals {
  cos_enabled = var.cos_offers.dashboard != null ? true : false
  tls_enabled = var.tls_offer != null ? true : false
}

module "mysql_server" {
  source      = "git::https://github.com/canonical/mysql-k8s-operator//terraform?ref=main"
  model_name  = var.model
  app_name    = var.mysql_server.app_name
  base        = var.mysql_server.base
  channel     = var.mysql_server.channel
  revision    = var.mysql_server.revision
  constraints = var.mysql_server.constraints
  units       = var.mysql_server.units
}

module "mysql_router" {
  source      = "git::https://github.com/canonical/mysql-router-operators//kubernetes/terraform?ref=dpe"
  model_name  = var.model
  app_name    = var.mysql_router.app_name
  base        = var.mysql_router.base
  channel     = var.mysql_router.channel
  revision    = var.mysql_router.revision
  constraints = var.mysql_router.constraints
  units       = var.mysql_router.units
}
