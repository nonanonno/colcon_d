# Copyright 2021 nonanonno
# Licensed under the Apache License, Version 2.0

import os
import pytest_shell.shell
from pathlib import Path
from typing import Optional


def _search_workspace(upper_than=2) -> Optional[str]:
    """
    Search workspace root by finding `install` directory.

    :param int upper_than:
        Search from parents[upper_than] of test directory.
        Default is repository root.
    """
    path = Path(__file__).absolute()
    if upper_than > 0:
        path = path.parents[upper_than - 1]
    for p in path.parents:
        if 'install' in os.listdir(p):
            return str(p)
    return None


WORKSPACE_ROOT = _search_workspace()


def test_dub_package_execute(bash: pytest_shell.shell.bash):
    """Check if the dub package was built by executing."""
    bash.cd(WORKSPACE_ROOT)
    assert bash.run_script_inline([
        './install/dub_test_package/lib/dub/dub_test_package/dub_test_package'
    ]) == 'Hello, World!'
