# Copyright 2021 nonanonno
# Licensed under the Apache License, Version 2.0
"""Represent DUB package and handle dub executable."""

import os
import shutil
import json

from pathlib import Path
from typing import Dict, Optional, List

from colcon_core.environment_variable import EnvironmentVariable
from colcon_core.logging import colcon_logger

DUB_COMMAND_ENVIRONMENT_VARIABLE = EnvironmentVariable(
    'DUB_COMMAND', 'The full path to the DUB executable')

DUB_PACKAGE_PATH_ENV = 'DUB_PACKAGE_PATH'

IS_WINDOWS = os.name == 'nt'

logger = colcon_logger.getChild(__name__)


class DubConfiguration:
    """This class represents DUB build configuration."""

    __slots__ = (
        'name',
        'target_type',
        'target_path',
        'target_name'
    )

    def __init__(self, config: Dict):
        if 'name' not in config:
            logger.warn("There is no 'name' field in this configuration")
            self.name = None
            return
        self.name = config['name']
        if 'targetName' in config:
            self.target_name = config['targetName']
        else:
            self.target_name = self.name
        if 'targetType' in config:
            self.target_type = config['targetType']
        else:
            self.target_type = 'executable'
        if 'targetPath' in config:  # This is a directory
            self.target_path = Path(config['targetPath'])
        else:
            self.target_path = Path('./')

    def valid(self):
        return self.name is not None

    def is_executable(self):
        return self.target_type == 'executable'

    def object_path(self):
        return self.target_path / self.target_name


class DubPackage:
    """This class represents DUB package."""

    __slots__ = (
        'name',
        'version',
        'path',
        'configurations',
        'install_files',
        'create_files'
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
        self.configurations = []

        if 'configurations' in dub_cache:
            for c in dub_cache['configurations']:
                dc = DubConfiguration(c)
                if dc.valid():
                    self.configurations.append(dc)
        else:
            self.configurations.append(
                DubConfiguration({'name': None, 'targetName': self.name}))

        os.environ['DUB_PACKAGE'] = self.name

        if 'installFiles' in dub_cache:
            self.install_files = _replace(dub_cache['installFiles'])
        else:
            self.install_files = {}
        if 'createFiles' in dub_cache:
            self.create_files = _replace(dub_cache['createFiles'])
        else:
            self.create_files = {}

    async def create_local_packages(self, depends: List['DubPackage']):
        packages = [
            {
                'name': dep.name,
                'path': str(dep.path),
                'version': dep.version
            } for dep in depends
        ]
        local_path = self.path / '.dub' / 'packages' / 'local-packages.json'
        local_path.parent.mkdir(parents=True, exist_ok=True)

        with open(local_path, 'w') as f:
            json.dump(packages, f, indent=4)

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


def _replace(src):
    if isinstance(src, str):
        return os.path.expandvars(src)
    elif isinstance(src, list):
        return [_replace(s) for s in src]
    elif isinstance(src, dict):
        dst = {}
        for key, value in src.items():
            dst_key = os.path.expandvars(key)
            dst_value = _replace(value)
            dst[dst_key] = dst_value
        return dst
    else:
        assert False


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
