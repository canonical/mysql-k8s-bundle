module "mysql" {
  source          = "git::https://github.com/paulomach/terraform-modules//modules/k8s/mysql?ref=feature/feature-sync-pg-mysql"
  juju_model_name = var.model_name
  channel         = var.mysql_charm_channel
  revision        = local.mysql_revisions[var.arch]
  config          = var.mysql_charm_config
  storage_size    = var.mysql_storage_size
  units           = var.mysql_charm_units
  constraints     = "arch=${var.arch}"
}

resource "juju_application" "backups_s3_integrator" {
  name  = "backups-s3-integrator"
  model = var.model_name
  trust = true

  charm {
    name     = "s3-integrator"
    channel  = var.s3_integrator_charm_channel
    revision = local.s3_integrator_revisions[var.arch]
  }

  config = {
    endpoint     = var.mysql_backup_endpoint
    bucket       = var.mysql_backup_bucket_name
    path         = var.model_name
    region       = var.mysql_backup_region
    s3-uri-style = "path"
  }

  units = 1

  provisioner "local-exec" {
    # There's currently no way to wait for the charm to be idle, hence the wait-for
    # https://github.com/juju/terraform-provider-juju/issues/202
    command = "juju wait-for application ${self.name} --query='name==\"${self.name}\" && status==\"blocked\"'; $([ $(juju version | cut -d. -f1) = '3' ] && echo 'juju run' || echo 'juju run-action') ${self.name}/leader sync-s3-credentials access-key=${var.mysql_backup_access_key} secret-key=${var.mysql_backup_secret_key}"
  }
}

resource "juju_application" "mysql_router" {
  count = var.data_integrator_enabled ? 1 : 0
  name  = "mysql-router"
  model = var.model_name
  trust = true

  charm {
    name     = "mysql-router-k8s"
    channel  = var.mysql_router_charm_channel
    revision = local.mysql_router_revisions[var.arch]
  }
}

resource "juju_application" "data_integrator" {
  count = var.data_integrator_enabled ? 1 : 0
  name  = "data-integrator"
  model = var.model_name

  charm {
    name     = "data-integrator"
    channel  = var.data_integrator_charm_channel
    revision = local.data_integrator_revisions[var.arch]
  }

  config = {
    database-name = var.data_integrator_database_name
  }

  units = 1
}

resource "juju_application" "self_signed_certificates" {
  count = var.enable_tls ? 1 : 0
  name  = "self-signed-certificates"
  model = var.model_name

  charm {
    name     = "self-signed-certificates"
    channel  = var.self_signed_certificates_charm_channel
    revision = local.tls_revisions[var.arch]
  }

  config = {
    ca-common-name = "${module.mysql.application_name} CA"
  }

  units = 1
}
