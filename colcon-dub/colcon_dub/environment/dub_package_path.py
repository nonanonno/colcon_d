# Copyright 2021 nonanonno
# Licensed under the Apache License, Version 2.0
"""
Implement environment for DUB package.

Since DUB doesn't have a function to handle package search path using
environment variable, this sets `DUB_PACKAGE_PATH` as package path and tasks
see `DUB_PACKAGE_PATH` to find dependent packages' location.
"""

from pathlib import Path

from colcon_core import shell
from colcon_core.environment import EnvironmentExtensionPoint
from colcon_core.environment import logger
from colcon_core.plugin_system import satisfies_version

from colcon_dub.dub import DubPackage
from colcon_dub.dub import DUB_PACKAGE_PATH_ENV


class DubPackagePathEnvironment(EnvironmentExtensionPoint):
    """Extend the `DUB_PACKAGE_PATH` variable to find DUB packages."""

    def __init__(self):
        super().__init__()
        satisfies_version(
            EnvironmentExtensionPoint.EXTENSION_POINT_VERSION,
            '^1.0')

    def create_environment_hooks(
        self, prefix_path: Path, pkg_name: str):  # noqa D102
        hooks = []
        dub_path = prefix_path / 'lib' / 'dub' / pkg_name
        dub_package = DubPackage.load(dub_path)
        logger.log(1, "checking '%s'" % dub_path)

        if dub_package:
            hooks += shell.create_environment_hook(
                'dub_package_path', prefix_path, pkg_name,
                DUB_PACKAGE_PATH_ENV, str(dub_package.path), mode='prepend')

        return hooks
