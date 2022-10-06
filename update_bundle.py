#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import logging
import requests
import yaml
import sys

from pathlib import Path

logger = logging.getLogger(__name__)


def fetch_revision(charm, charm_channel):
    """Returns revision number for charm in channel."""
    charm_info = requests.get(
        f"https://api.snapcraft.io/v2/charms/info/{charm}?fields=channel-map"
    ).json()

    [track, risk] = charm_channel.split("/")

    for channel in charm_info["channel-map"]:
        if channel["channel"]["risk"] == risk and channel["channel"]["track"] == track:
            return channel["revision"]["revision"]

    raise ValueError(f"Revision not found for {charm} on {charm_channel}")

def update_bundle(bundle_path):
    """Updates a bundle's revision number."""
    bundle_data = yaml.safe_load(Path(bundle_path).read_text())

    for applications in bundle_data["applications"]:
        bundle_data["applications"][applications]["revision"] = fetch_revision(
            applications, bundle_data["applications"][applications]["channel"]
        )

    with open(bundle_path, 'w') as bundle:
        yaml.dump(bundle_data, bundle)
        bundle.close()


if __name__ == '__main__':
    update_bundle(sys.argv[1])
