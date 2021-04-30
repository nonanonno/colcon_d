# Copyright 2021 nonanonno
# Licensed under the Apache License, Version 2.0
"""Implement test task for DUB package."""

from argparse import ArgumentParser
from pathlib import Path
from typing import Dict, Optional

from colcon_dub.dub import DUB_EXECUTABLE
from colcon_dub.dub import DubPackage

from colcon_core.logging import colcon_logger
from colcon_core.task import TaskExtensionPoint
from colcon_core.task import run
from colcon_core.plugin_system import satisfies_version
from colcon_core.shell import get_command_environment

logger = colcon_logger.getChild(__name__)


class DubTestTask(TaskExtensionPoint):
    """Test dub package."""

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

    async def test(
        self, *, additional_hooks=None) -> Optional[int]:  # noqa D102
        pkg = self.context.pkg
        args = self.context.args  # TestPackageArguments

        logger.info(
            "Testing DUB package in '{args.path}'".format_map(
                locals()))

        try:
            env = await get_command_environment(
                'test', args.build_base, self.context.dependencies)
        except RuntimeError as e:
            logger.error(str(e))
            return 1

        dub_package = DubPackage(Path(args.path))

        rc = await self._test(dub_package, env)
        if rc:
            return rc

    async def _test(self, dub: DubPackage, env: Dict) -> Optional[int]:
        self.progress('test')

        if DUB_EXECUTABLE is None:
            raise RuntimeError("Could not find 'dub' executable")

        args = self.context.args  # TestPackageArguments

        cmd = [DUB_EXECUTABLE, 'test']
        cmd += ['--']
        cmd += (self.context.args.dub_args or [])

        completed = await run(self.context, cmd, cwd=args.path, env=env)
        if completed.returncode:
            return completed.returncode
