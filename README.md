# Canonical Distribution of MySQL + MySQLRouter

[![None](https://charmhub.io/mysql-k8s-bundle/badge.svg)](https://charmhub.io/mysql-k8s-bundle)

Welcome to the Canonical Distribution of MySQL + MySQLRouter.

The objective of this page is to provide directions to
get up and running with Canonical MySQL charms.

## Installation

Currently, we support this distribution with Ubuntu 20.04.

To get started, please take Ubuntu 22.04 LTS and install the
necessary components. Juju, MicroK8s (with add-ons as listed below):

```shell
sudo snap refresh
sudo snap install juju --classic
sudo snap install microk8s --classic
sudo snap install jhack # nice to have it nearby
sudo microk8s enable dns storage ha-cluster ingress hostpath-storage
sudo usermod -a -G microk8s $(whoami) && newgrp microk8s
```

To follow, please bootstrap the juju controller with microk8s using:

```shell
juju bootstrap microk8s my-microk8s
```

Finally add a juju model and deploy the bundle:

```shell
juju add-model my-mysql-k8s
juju deploy mysql-k8s-bundle --trust # --channel edge # Choose a channel!
juju status # you are ready!
juju status --watch 1s --storage --relations # watch all the information
```

Feel free to increase DEBUG verbosity for troubleshooting:

```shell
juju model-config 'logging-config=<root>=INFO;unit=DEBUG'
juju debug-log # show all logs together
juju debug-log --include mysql-k8s/0 --replay --tail # to check specific unit
```

To destroy the complete Juju model with all newly deployed charms and data:

```shell
juju destroy-model my-mysql-k8s -y --destroy-storage --force && \
juju add-model my-mysql-k8s && juju status
```

## Bundle Components

[![MySQL](https://charmhub.io/mysql-k8s/badge.svg)](https://charmhub.io/mysql-k8s) [![MySQL Router](https://charmhub.io/mysql-router-k8s/badge.svg)](https://charmhub.io/mysql-router-k8s) [![TLS Certificates](https://charmhub.io/tls-certificates-operator/badge.svg)](https://charmhub.io/tls-certificates-operator)

- [mysql-k8s](https://charmhub.io/mysql-k8s): A k8s charm to deploy MySQL with Group Replication.
- [mysql-router-k8s](https://charmhub.io/mysql-router-k8s) - a k8s charm to deploy MySQL Router.
- [tls-certificates-operator](https://charmhub.io/tls-certificates-operator) - TLS operator.

Note: The TLS settings in bundles use self-signed-certificates which are not recommended for production clusters, the tls-certificates-operator charm offers a variety of configurations, read more on the TLS charm [here](https://charmhub.io/tls-certificates-operator).

## Troubleshooting

If you have any problems or questions, please feel free to reach out. We'd be more than glad to help!

The fastest way to get our attention is to create a [discourse post](https://discourse.charmhub.io/).
