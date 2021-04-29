# Copyright 2021 nonanonno
# Licensed under the Apache License, Version 2.0

from pathlib import Path
from typing import Dict, Optional
import json


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
        dub_package = DubPackage(path)
        if dub_package.name is None:
            return None
        else:
            return dub_package


def _load_json(path: Path) -> Dict:
    with open(path, 'r') as f:
        return json.load(f)
