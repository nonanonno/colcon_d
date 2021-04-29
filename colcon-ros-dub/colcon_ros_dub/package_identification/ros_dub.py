# Copyright 2021 nonanonno
# Licensed under the Apache License, Version 2.0

import copy

from colcon_core.package_identification \
    import PackageIdentificationExtensionPoint
from colcon_core.package_identification import PackageDescriptor
from colcon_core.plugin_system import satisfies_version
from colcon_dub.package_identification.dub import DubPackage
from colcon_ros.package_identification.ros import RosPackageIdentification


class RosDubPackageIdentification(PackageIdentificationExtensionPoint):
    """Identify ROS DUB package with 'package.xml' and DUB package."""

    # The priority needs to be higher than the ROS extensions identifying
    # packages using the build systems supported by ROS DUB.
    PRIORITY = RosPackageIdentification.PRIORITY

    def __init__(self):
        super().__init__()
        satisfies_version(
            PackageIdentificationExtensionPoint.EXTENSION_POINT_VERSION,
            '^1.0')

    def identify(self, desc: PackageDescriptor):
        """Check if the given path is ROS2 DUB package."""
        if desc.type is not None and desc.type != 'ros.dub':
            # This package was already identified as another package type
            return

        ros_desc = copy.deepcopy(desc)

        ros_extension = RosPackageIdentification()
        ros_extension.identify(ros_desc)

        if ros_desc.type != 'ros.dub':
            return

        dub_package = DubPackage.load(ros_desc.path)
        if not dub_package:
            return

        if ros_desc.name is not None and ros_desc.name != dub_package.name:
            raise RuntimeError('Package name already set to different value')

        desc.type = ros_desc.type
        desc.name = dub_package.name
        desc.dependencies = ros_desc.dependencies
        desc.hooks = ros_desc.hooks
        desc.metadata = ros_desc.metadata
