# Copyright 2021 nonanonno
# Licensed under the Apache License, Version 2.0
"""Represent DUB package and handle dub executable."""

import os
import shutil
import json

from pathlib import Path
from typing import Dict, Optional

from colcon_core.environment_variable import EnvironmentVariable

DUB_COMMAND_ENVIRONMENT_VARIABLE = EnvironmentVariable(
    'DUB_COMMAND', 'The full path to the DUB executable')

IS_WINDOWS = os.name == 'nt'


class DubPackage:
    """This class represents DUB package."""

    __slots__ = (
        'name',
        'version',
        'path',
        'executables'
    )

    def __init__(self, path: Path):
        self.name = None

        if (path / 'dub.json').exists():
            dub_cache = _load_json(path / 'dub.json')
        elif (path / 'dub.sdl').exists():
            raise RuntimeError('Not implemented : dub.sdl')
        else:
            return

        if 'name' not in dub_cache:
            raise RuntimeError('Failed to extract package name')

        self.name = dub_cache['name']
        if 'version' in dub_cache:
            self.version = dub_cache['version']
        else:
            self.version = '~master'
        self.path = path.absolute()
        self.executables = []

        if 'configurations' in dub_cache:
            for c in dub_cache['configurations']:
                e = dict()
                e['name'] = c['name']
                if 'targetName' in c:
                    e['target'] = c['targetName']
                else:
                    e['target'] = e['name']

                self.executables.append(e)
        else:
            self.executables.append({'name': None, 'target': self.name})

    @classmethod
    def load(cls, path: Path) -> Optional['DubPackage']:
        """Read DUB package file and construct instance."""
        dub_package = DubPackage(path)
        if dub_package.name is None:
            return None
        else:
            return dub_package


def _load_json(path: Path) -> Dict:
    with open(path, 'r') as f:
        return json.load(f)


def _which_executable(environment_variable: str, executable: str) -> str:
    """
    Determin the path of an executable.

    An environment variable can be used to override the location instead of
    relying on searching the PATH.

    :param str environment_variable: The name of the environment variable
    :param str executable_name: The name of the executable
    :rtype: str
    """
    cmd = None
    env_cmd = os.getenv(environment_variable)

    # Case of DUB_COMMAND (colcon)
    if env_cmd is not None and Path(env_cmd).is_file():
        cmd = env_cmd

    # Fallback (from Path)
    if cmd is None:
        cmd = shutil.which(executable)

    return cmd


DUB_EXECUTABLE = _which_executable(
    DUB_COMMAND_ENVIRONMENT_VARIABLE.name, 'dub')
