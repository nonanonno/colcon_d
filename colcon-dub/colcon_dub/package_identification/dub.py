# Copyright 2021 nonanonno
# Licensed under the Apache License, Version 2.0

from colcon_core.package_identification \
    import PackageIdentificationExtensionPoint
from colcon_core.package_identification import PackageDescriptor
from colcon_core.plugin_system import satisfies_version
from colcon_dub.dub import DubPackage


class DubPackageIdentification(PackageIdentificationExtensionPoint):
    """Identify DUB package with `dub.json` or `dub.sdl` file."""

    def __init__(self):
        super().__init__()
        satisfies_version(
            PackageIdentificationExtensionPoint.EXTENSION_POINT_VERSION,
            '^1.0')

    def identify(self, desc: PackageDescriptor):
        """Check if the given path contains a dub.json or dub.sdl."""
        if desc.type is not None and desc.type != 'dub':
            # This package was already identified as another package type
            return

        dub_package = DubPackage.load(desc.path)
        if not dub_package:
            return

        if desc.name is not None and desc.name != dub_package.name:
            raise RuntimeError('Package name already set to different value')

        desc.name = dub_package.name
        desc.type = 'dub'
