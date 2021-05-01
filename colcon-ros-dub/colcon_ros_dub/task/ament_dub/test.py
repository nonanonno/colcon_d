# Copyright 2021 nonanonno
# Licensed under the Apache License, Version 2.0
"""Implement build task for ament_dub package."""

from typing import Optional

from colcon_dub.task.dub.test import DubTestTask
from colcon_core.logging import colcon_logger
from colcon_core.plugin_system import satisfies_version
from colcon_core.task import TaskExtensionPoint

logger = colcon_logger.getChild(__name__)


class AmentDubTestTask(TaskExtensionPoint):
    """Test ament_dub packages."""

    def __init__(self):
        super().__init__()
        satisfies_version(TaskExtensionPoint.EXTENSION_POINT_VERSION, '^1.0')

    async def test(
        self, *, additional_hooks=None) -> Optional[int]:  # noqa D102
        args = self.context.args  # TestPackageArguments
        logger.info("Testing ROS package in '{args.path}'"
                    "with build type 'ros.ament_dub'".format_map(locals()))

        extension = DubTestTask()
        extension.set_context(context=self.context)

        rc = await extension.test(additional_hooks=additional_hooks)
        if rc:
            return rc
