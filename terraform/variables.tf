variable "create_model" {
  description = "Model creation convenience flag"
  type        = bool
  default     = false
}

variable "model_name" {
  description = "Juju model name for deployment"
  type        = string
}

variable "arch" {
  description = "Deployment architecture"
  type        = string
  default     = "amd64"

  validation {
    condition     = var.arch == "amd64" || var.arch == "arm64"
    error_message = "Architecture must be either amd64 or arm64"
  }
}

variable "mysql_charm_channel" {
  description = "MySQL K8s charm channel"
  type        = string
  default     = "8.0/stable"
}


variable "mysql_charm_units" {
  description = "MySQL K8s charm units number"
  type        = number
  default     = 3
}

variable "mysql_backup_endpoint" {
  description = "MySQL K8s backup bucket endpoint"
  type        = string
}

variable "mysql_backup_bucket_name" {
  description = "MySQL K8s backup bucket name"
  type        = string
}

variable "mysql_backup_region" {
  description = "MySQL K8s backup bucket region"
  type        = string
}

variable "mysql_backup_access_key" {
  description = "MySQL K8s backup bucket access key"
  type        = string
}

variable "mysql_backup_secret_key" {
  description = "MySQL K8s backup bucket secret key"
  type        = string
  sensitive   = true
}

variable "mysql_storage_size" {
  description = "MySQL storage size"
  type        = string
  default     = "10G"
}

variable "mysql_charm_config" {
  description = "MySQL charm configuration"
  type        = map(string)
  default     = {}
}

variable "mysql_router_charm_channel" {
  description = "MySQL router charm channel"
  type        = string
  default     = "8.0/stable"
}


variable "data_integrator_enabled" {
  description = "Enable data integrator for external connectivity"
  type        = bool
  default     = false
}

variable "data_integrator_charm_channel" {
  description = "Data integrator charm channel"
  type        = string
  default     = "latest/stable"
}


variable "data_integrator_database_name" {
  description = "Data integrator database name"
  type        = string
  default     = ""
  validation {
    condition     = var.data_integrator_enabled == false || var.data_integrator_database_name != ""
    error_message = "data_integrator_database_name must be set if data_integrator_enabled is true."
  }
}

variable "enable_tls" {
  description = "Enable/enforce TLS through self-signed certificates"
  type        = bool
  default     = true
}

variable "s3_integrator_charm_channel" {
  description = "S3 integrator charm channel"
  type        = string
  default     = "latest/stable"
}


variable "certificates_charm_channel" {
  description = "Self Signed Certificates Operator charm channel"
  type        = string
  default     = "latest/stable"
}

variable "mysql_charm_revision" {
  description = "MySQL charm revision override"
  type        = number
  default     = null
}

variable "mysql_router_charm_revision" {
  description = "MySQL router charm revision override"
  type        = number
  default     = null
}

variable "s3_integrator_charm_revision" {
  description = "s3_integrator charm revision override"
  type        = number
  default     = null
}

variable "certificates_charm_revision" {
  description = "Certificates charm revision override"
  type        = number
  default     = null
}

variable "certificates_charm_name" {
  description = "Certificates charm name"
  type        = string
  default     = "self-signed-certificates"
}

variable "certificates_charm_config" {
  description = "Certificates charm configuration"
  type        = map(string)
  default     = { ca-common-name = "MySQL CA" }
}

variable "data_integrator_charm_revision" {
  description = "data-integrator charm revision override"
  type        = number
  default     = null
}

