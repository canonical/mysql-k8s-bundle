# Charmed MySQL K8s Terraform solution

This is a Terraform module facilitating the deployment of Charmed MySQL K8s in integrated fashion, using the [Terraform juju provider](https://github.com/juju/terraform-provider-juju/). For more information, refer to the provider [documentation](https://registry.terraform.io/providers/juju/juju/latest/docs).

## API

### Inputs

| Name | Description | Type | Default | Required |
| - | - | - | - | - |
| `arch` | Architecture of the deployed model | `string` | `"amd64"` | no |
| `certificates_charm_channel` | Charm channel for self-signed-certificates | `string` | `"latest/stable"` | no |
| `certificates_charm_config` | Configuration options for the self-signed-certificates charm | `map(string)` | `{ca-common-name = "MySQL CA"}` | no |
| `certificates_charm_name` | Name of the certificates charm to use | `string` | `"self-signed-certificates"` | no |
| `certificates_charm_revision` | Charm revision number override for self-signed-certificates | `number` | `null` | no |
| `create_model` | Whether to create the model | `bool` | `false` | no |
| `data_integrator_charm_channel` | Charm channel for the data integrator | `string` | `"latest/stable"` | no |
| `data_integrator_charm_revision` | Charm revision number override for data-integrator | `number` | `null` | no |
| `data_integrator_database_name` | Database name for the data integrator | `string` | `""` | yes, if data_integrator is enabled |
| `data_integrator_enabled` | Whether to deploy the data integrator | `bool` | `false` | no |
| `enable_tls` | Whether to enable TLS for the MySQL operator | `bool` | `true` | no |
| `model_name` | Name of the model to create/use | `string` | `null` | yes |
| `mysql_backup_access_key` | Backup access key for the MySQL operator | `string` | `""` | yes |
| `mysql_backup_bucket_name` | Backup bucket for the MySQL operator | `string` | `""` | yes |
| `mysql_backup_endpoint` | Backup endpoint for the MySQL operator | `string` | `""` | yes |
| `mysql_backup_region` | Backup region for the MySQL operator | `string` | `""` | yes |
| `mysql_backup_secret_key` | Backup secret key for the MySQL operator | `string` | `""` | yes |
| `mysql_charm_channel` | Charm channel for the MySQL operator | `string` | `"8.0/stable"` | no |
| `mysql_charm_config` | Configuration options for the MySQL operator | `map(string)` | `{}` | no |
| `mysql_charm_revision` | Charm revision number override for MySQL | `number` | `null` | no |
| `mysql_charm_units` | Number of units for the MySQL operator | `number` | `3` | no |
| `mysql_router_charm_channel` | Charm channel for the MySQL router | `string` | `"8.0/stable"` | no |
| `mysql_router_charm_revision` | Charm revision number override for mysql-router-k8s | `number` | `null` | no |
| `mysql_storage_size` | Storage size for the MySQL operator | `string` | `"10G"` | no |
| `s3_integrator_charm_channel` | Charm channel for S3 integrator | `string` | `"latest/stable"` | no |
| `s3_integrator_charm_revision` | Charm revision number override for S3 integrator | `number` | `null` | no |


## Usage

This solution module is intended to be used either on its own or as part of a higher-level module. 

### Create model

If a model does not exist, it can be created by setting the `create_model` variable to `true`. 

```shell
terraform apply \
	-var mysql_backup_access_key='<access_key>' \ 
	-var mysql_backup_bucket_name='<bucket>' \ 
	-var mysql_backup_endpoint='<endpoint url>' \ 
	-var mysql_backup_region='<region>' \
	-var mysql_backup_secret_key='<secret_key>' \
    -var model_name='<model_name>' \
    -var create_model='true'
```

By default, it is set to `false`, requiring that the model already exists and is set through the `model_name` variable.

### Deploying to arm64

To deploy to arm64, set the `arch` variable to `arm64`.

```shell
terraform apply \
	-var mysql_backup_access_key='<access_key>' \ 
	-var mysql_backup_bucket_name='<bucket>' \ 
	-var mysql_backup_endpoint='<endpoint url>' \ 
	-var mysql_backup_region='<region>' \
	-var mysql_backup_secret_key='<secret_key>' \
    -var model_name='<model_name>' \
    -var arch='arm64'
```

### Charm revision override

To override any given component charm revision, set the respective variable to the desired revision number.

```shell
terraform apply \
    -var mysql_backup_access_key='<access_key>' \
    -var mysql_backup_bucket_name='<bucket>' \
    -var mysql_backup_endpoint='<endpoint url>' \
    -var mysql_backup_region='<region>' \
    -var mysql_backup_secret_key='<secret>' \
    -var model_name='<model_name>' \
    -var mysql_charm_revision=265
```

Make sure to select the correct revision for the deployment architecture.


### Using a different certificates charm

By default, the `self-signed-certificates` is used to provide TLS certificates to MySQL.
It's possible to use a certificate charm other then `self-signed-certificates`. Notice that for some
other, it's required to set (or unset) configuration accordingly, and override it's revision, e.g. when 
using [manual-tls-certificates](https://charmhub.io/manual-tls-certificates):

```shell
terraform apply \
    -var mysql_backup_access_key='<access_key>' \
    -var mysql_backup_bucket_name='<bucket>' \
    -var mysql_backup_endpoint='<endpoint url>' \
    -var mysql_backup_region='<region>' \
    -var mysql_backup_secret_key='<secret>' \
    -var model_name='<model_name>' \
    -var certificates_charm_channel="manual-tls-certificates" \
    -var certificates_charm_revision=108 \
    -var certificates_charm_config={}
```
