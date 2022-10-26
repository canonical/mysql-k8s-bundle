# Canonical Distribution of MySQL + MySQLRouter

Welcome to the Canonical Distribution of MySQL + MySQLRouter.

The objective of this page is to provide directions to get up and running with Canonical MySQL
charms.

## Installation

Currently, we support this distribution with Ubuntu 20.04.

To get started, please install the following:
- Microk8s
- Juju

Then set up microk8s by enabling the `dns`, `ha-cluster` and `storage` add-ons.

To follow, please bootstrap the juju controller with microk8s using `juju bootstrap microk8s <controller_name>`.

Finally add a juju model with `juju add-model <model-name>` and deploy the bundle with `juju deploy mysql-k8s-bundle`.

## Bundle Components
- [mysql-k8s](https://charmhub.io/mysql-k8s): A k8s charm to deploy MySQL with Group Replication.
- [mysql-router-k8s](https://charmhub.io/mysql-router-k8s) - a k8s charm to deploy MySQL Router.
- [tls-certificates-operator](https://charmhub.io/tls-certificates-operator) - TLS operator. Note: The TLS settings in bundles use self-signed-certificates which are not recommended for production clusters, the tls-certificates-operator charm offers a variety of configurations, read more on the TLS charm [here](https://charmhub.io/tls-certificates-operator).

## Troubleshooting

If you have any problems or questions, please feel free to reach out. We'd be more than glad to help!

The fastest way to get our attention is to create a [discourse post](https://discourse.charmhub.io/).
