resource "juju_integration" "s3_integrator_mysql" {
  model = var.model_name

  application {
    name = juju_application.backups_s3_integrator.name
  }

  application {
    name     = module.mysql.application_name
    endpoint = module.mysql.requires.s3_parameters
  }
}

resource "juju_integration" "mysql_self_signed_certificates" {
  count = var.enable_tls ? 1 : 0
  model = var.model_name

  application {
    name     = module.mysql.application_name
    endpoint = module.mysql.requires.certificates
  }
  application {
    name = juju_application.self_signed_certificates[0].name
  }
}

resource "juju_integration" "mysql_mysql_router" {
  count = var.data_integrator_enabled ? 1 : 0
  model = var.model_name

  application {
    name     = module.mysql.application_name
    endpoint = module.mysql.provides.database
  }
  application {
    name     = juju_application.mysql_router[0].name
    endpoint = "backend-database"
  }
}

resource "juju_integration" "mysql_router_data_integrator" {
  count = var.data_integrator_enabled ? 1 : 0
  model = var.model_name

  application {
    name     = juju_application.mysql_router[0].name
    endpoint = "database"
  }
  application {
    name     = juju_application.data_integrator[0].name
    endpoint = "mysql"
  }
}
