locals {
  mysql_revisions = {
    amd64 = 180, # renovate tag
    arm64 = 181
  }
  s3_integrator_revisions = {
    amd64 = 31,
    arm64 = 32
  }
  data_integrator_revisions = {
    amd64 = 41,
    arm64 = 40
  }
  mysql_router_revisions = {
    amd64 = 155,
    arm64 = 154
  }
  tls_revisions = {
    amd64 = 155,
    arm64 = 201
  }
}
