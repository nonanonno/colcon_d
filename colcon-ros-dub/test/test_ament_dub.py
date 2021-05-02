# Copyright 2021 nonanonno
# Licensed under the Apache License, Version 2.0

import os
import pytest_shell.shell
from pathlib import Path
from typing import Optional
import shutil
import warnings


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
PATH_TO_THIS = str(Path(__file__).absolute().parent)


def test_ament_dub_package_execute(bash: pytest_shell.shell.bash):
    """Check if the ament_dub package was built by executing ros_dub_test2."""
    bash.cd(WORKSPACE_ROOT)
    assert bash.run_script_inline([
        './install/ros_dub_test2/lib/dub/ros_dub_test2/ros_dub_test2'
    ]) == 'ros_dub_test1'


def test_execute_via_ros_command(bash: pytest_shell.shell.bash):
    """Check if the executable can be call via ros2 run"""
    if not shutil.which('ros2'):
        warnings.warn("'ros2' does not exist, skip testing")
        return
    bash.cd(WORKSPACE_ROOT)
    assert bash.run_script_inline([
        'source ./install/setup.sh',
        'ros2 run ros_dub_test2 ros_dub_test2'
    ]).strip() == 'ros_dub_test1'


def test_colcon_test_success(bash: pytest_shell.shell.bash):
    """Check if the two ament_dub packages can be tested via colcon test."""
    bash.cd(WORKSPACE_ROOT)
    assert bash.run_script_inline([
        'source install/setup.sh',
        f'colcon test --paths {PATH_TO_THIS}/*'
        ' --dub-args -i success'
    ]).count('Summary: 2 packages finished') > 0


def test_colcon_test_fail(bash: pytest_shell.shell.bash):
    """Check if the two ament_dub packages can be tested via colcon test."""
    bash.cd(WORKSPACE_ROOT)
    bash.auto_return_code_error = False
    bash.run_script_inline([
        'source install/setup.sh',
        f'colcon test --paths {PATH_TO_THIS}/*'
        ' --dub-args -i fail'
        ' --return-code-on-test-failure'
    ])
    assert bash.last_return_code != 0
