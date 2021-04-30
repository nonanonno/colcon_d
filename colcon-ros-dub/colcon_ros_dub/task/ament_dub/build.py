# Copyright 2021 nonanonno
# Licensed under the Apache License, Version 2.0
"""Implement build task for ROS DUB package."""

from pathlib import Path

from colcon_dub.task.dub.build import DubBuildTask
from colcon_core.logging import colcon_logger
from colcon_core.plugin_system import satisfies_version
from colcon_core.task import TaskExtensionPoint
from colcon_core.shell import create_environment_hook

logger = colcon_logger.getChild(__name__)


class AmentDubBuildTask(TaskExtensionPoint):
    """Build ROS DUB packages."""

    def __init__(self):
        super().__init__()
        satisfies_version(TaskExtensionPoint.EXTENSION_POINT_VERSION, '^1.0')

    async def build(
        self, *, additional_hooks=None, skip_hook_creation=False):  # noqa D102
        args = self.context.args  # BuildPackageArguments
        logger.info("Building ROS package in '{args.path}'"
                    "with build type 'ros.ament_dub'".format_map(locals()))

        extension = DubBuildTask()
        extension.set_context(context=self.context)

        additional_hooks = create_environment_hook(
            'ament_prefix_path', Path(args.install_base),
            self.context.pkg.name, 'AMENT_PREFIX_PATH', '', mode='prepend')

        rc = await extension.build(additional_hooks=additional_hooks,
                                   skip_hook_creation=skip_hook_creation)
        if rc:
            return rc
