# Copyright 2021 nonanonno
# Licensed under the Apache License, Version 2.0
"""Implement build task for DUB package."""

import os
from argparse import ArgumentParser
from pathlib import Path
from distutils.dir_util import copy_tree
from shutil import copy2
from typing import Dict, Optional

from colcon_dub.dub import DUB_EXECUTABLE
from colcon_dub.dub import DubPackage
from colcon_dub.dub import DUB_PACKAGE_PATH_ENV

from colcon_core.logging import colcon_logger
from colcon_core.task import TaskExtensionPoint
from colcon_core.task import run
from colcon_core.task import create_file
from colcon_core.plugin_system import satisfies_version
from colcon_core.shell import get_command_environment
from colcon_core.environment import create_environment_scripts

logger = colcon_logger.getChild(__name__)


class DubBuildTask(TaskExtensionPoint):
    """Build dub package."""

    def __init__(self):
        super().__init__()
        satisfies_version(TaskExtensionPoint.EXTENSION_POINT_VERSION, '^1.0')

    def add_arguments(self, *, parser: ArgumentParser):  # noqa: D102
        parser.add_argument(
            '--dub-args',
            nargs='*', metavar='*', type=str.lstrip,
            help='Pass arguments to DUB projects. '
            'Arguments matching other options must be prefixed by a space,\n'
            'e.g. --dub-args " --help"')

    async def build(
        self,
        additional_hooks=None,
        skip_hook_creation=False
    ) -> Optional[int]:  # noqa: D102
        pkg = self.context.pkg
        args = self.context.args  # BuildPackageArguments

        logger.info(
            "Building DUB package in '{args.path}'".format_map(
                locals()))

        try:
            env = await get_command_environment(
                'build', args.build_base, self.context.dependencies)
        except RuntimeError as e:
            logger.error(str(e))
            return 1

        dub_package = DubPackage(Path(args.path))

        rc = await self._configure(dub_package, env)
        if rc:
            return rc

        rc = await self._build(dub_package, env)
        if rc:
            return rc

        rc = await self._install(dub_package)
        if rc:
            return rc

        if not skip_hook_creation:
            create_environment_scripts(
                pkg, args, additional_hooks=additional_hooks)

    async def _configure(self, dub: DubPackage, env: Dict) -> Optional[int]:
        self.progress('configure')

        if DUB_EXECUTABLE is None:
            raise RuntimeError("Could not find 'dub' executable")

        depends = []
        if DUB_PACKAGE_PATH_ENV in env:
            for dep in env[DUB_PACKAGE_PATH_ENV].split(':'):
                dep_dub = DubPackage.load(Path(dep))
                if dep_dub and dep_dub.name in self.context.dependencies:
                    depends.append(dep_dub)

        await dub.create_local_packages(depends)

    async def _build(self, dub: DubPackage, env: Dict) -> Optional[int]:
        self.progress('build')
        args = self.context.args  # BuildPackageArguments

        for config in dub.configurations:
            cmd = [DUB_EXECUTABLE, 'build']
            if config.name is not None:
                cmd += ['-c', config.name]
            cmd += ['--']
            cmd += (self.context.args.dub_args or [])

            completed = await run(self.context, cmd, cwd=args.path, env=env)
            if completed.returncode:
                return completed.returncode

    async def _install(self, dub: DubPackage) -> Optional[int]:
        self.progress('install')
        args = self.context.args  # BuildPackageArguments

        # We now install to <install_base>/lib/dub/<package>
        src_dir = Path(dub.path)

        # Ignore git files
        files = [
            f for f in os.listdir(src_dir)
            if not f.startswith('.git')
            and f != '.' and f != '..'
        ]

        # install DUB
        for f in files:
            dst_f = Path(f).parts[-1]
            _copy_path(
                args, f,
                'lib/dub/{self.context.pkg.name}/{dst_f}'.format_map(locals()))

        # install builds
        for c in dub.configurations:
            if not c.is_executable():
                continue
            obj_path = c.object_path()
            _copy_path(
                args, obj_path,
                'lib/{self.context.pkg.name}/{obj_path}'.format_map(locals()))

        # install files
        for dst, files in dub.install_files.items():
            for f in files:
                dst_f = Path(f).parts[-1]
                _copy_path(
                    args, f,
                    '{dst}/{dst_f}'.format_map(locals()))

        # create files
        for dst, files in dub.create_files.items():
            for f in files:
                create_file(args, '{dst}/{f}'.format_map(locals()))


def _copy_path(args, src_path, dst_path):
    dst_path = Path(args.install_base) / dst_path
    src_path = Path(args.path) / src_path
    logger.info("'{src_path}' -> '{dst_path}'".format_map(locals()))
    try:
        os.makedirs(dst_path.parent, exist_ok=True)
    except RuntimeError as e:
        logger.error(str(e))
        return

    if src_path.is_file():
        copy2(src_path, dst_path)
    else:
        copy_tree(str(src_path), str(dst_path))
