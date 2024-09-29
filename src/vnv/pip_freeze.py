"""
This is a skeleton file that can serve as a starting point for a Python
console script. To run this script uncomment the following lines in the
``[options.entry_points]`` section in ``setup.cfg``::

    console_scripts =
         fibonacci = vnv.skeleton:run

Then run ``pip install .`` (or ``pip install -e .`` for editable mode)
which will install the command ``fibonacci`` inside your current environment.

Besides console scripts, the header (i.e. until ``_logger``...) of this file can
also be used as template for Python modules.

Note:
    This file can be renamed depending on your needs or safely removed if not needed.

References:
    - https://setuptools.pypa.io/en/latest/userguide/entry_point.html
    - https://pip.pypa.io/en/stable/reference/pip_install
"""

import os
import subprocess
import logging
import sys

from vnv._utils import decode

__author__ = "Michael Mussato"
__copyright__ = "Michael Mussato"
__license__ = "MIT"

_logger = logging.getLogger(__name__)


# ---- Python API ----
# The functions defined in this section can be imported by users in their
# Python scripts/interactive interpreter, e.g. via
# `from vnv.skeleton import fib`,
# when using this Python module as a library.


def pip_freeze(
        venv_dir: str,
        *,
        requirements_base_dir: str = None
) -> str:
    """

    Args:
        venv_dir: full path to venv
        requirements_base_dir: directory of requirements.txt file to write
    """
    _logger.info(f"upgrade_pip...")
    activate = os.path.join(
        venv_dir,
        "bin",
        "activate",
    )

    requirements_txt = os.path.join(
        requirements_base_dir,
        "requirements.txt",
    )

    cmd = [
        "source",
        activate,
        "&&",
        "pip",
        "freeze",
        ">",
        requirements_txt,
        "&&",
        "deactivate",
        "&&",
        "exit",
        "0",
    ]

    proc = subprocess.Popen(
        args=" ".join(cmd),
        cwd=venv_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
    )
    for line in proc.stdout:
        _logger.info(decode(line))

    sys.stdout.writelines(
        f"Result:\n"
        f"{requirements_txt=}\n"
    )

    return requirements_txt


# ---- CLI ----
# The functions defined in this section are wrappers around the main Python
# API allowing them to be called directly from the terminal as a CLI
# executable/script.


def add_sub_parser(subparsers):

    parser__pip_install_packages = subparsers.add_parser(
        "pip-freeze",
        help="pip freeze and write to requirements.txt file",
    )

    parser__pip_install_packages.add_argument(
        "-v",
        "--venv",
        type=str,
        dest="venv_dir",
        required=True,
        default=None,
        help="--venv full path to venv Help",  # Todo
    )

    parser__pip_install_packages.add_argument(
        "-d",
        "--requirements-dir",
        type=str,
        dest="requirements_base_dir",
        required=False,
        default=None,
        help="--requirements-dir Help",  # Todo
    )


if __name__ == "__main__":
    # ^  This is a guard statement that will prevent the following code from
    #    being executed in the case someone imports this file instead of
    #    executing it as a script.
    #    https://docs.python.org/3/library/__main__.html
    pass
