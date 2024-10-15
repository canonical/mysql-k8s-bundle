resource "juju_model" "mysql" {
  count = var.create_model ? 1 : 0
  name  = var.model_name
}
