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

from vnv._utils import decode

from vnv.constants import PYTHON

__author__ = "Michael Mussato"
__copyright__ = "Michael Mussato"
__license__ = "MIT"

_logger = logging.getLogger(__name__)


# ---- Python API ----
# The functions defined in this section can be imported by users in their
# Python scripts/interactive interpreter, e.g. via
# `from vnv.skeleton import fib`,
# when using this Python module as a library.


def upgrade_pip(
        venv_dir: str,
) -> None:
    """

    Args:
        venv_dir: full path to venv
    """
    _logger.info(f"upgrade_pip {venv_dir=}...")

    activate = os.path.join(
        venv_dir,
        "bin",
        "activate",
    )

    cmd = [
        "source",
        activate,
        "&&",
        "pip",
        "install",
        "--upgrade",
        "pip",
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
        stderr=subprocess.PIPE,
        shell=True,
    )
    for line in proc.stdout:
        _logger.info(decode(line))

    return None


# ---- CLI ----
# The functions defined in this section are wrappers around the main Python
# API allowing them to be called directly from the terminal as a CLI
# executable/script.


def add_sub_parser(subparsers):

    parser__upgrade_pip = subparsers.add_parser(
        "upgrade-pip",
        help="pip install --upgrade pip",
    )

    parser__upgrade_pip.add_argument(
        "-vnv",
        "--upgrade-pip-venv",
        type=str,
        dest="upgrade_pip",
        required=True,
        default=None,
        help="--upgrade-pip-venv Help",
    )


if __name__ == "__main__":
    # ^  This is a guard statement that will prevent the following code from
    #    being executed in the case someone imports this file instead of
    #    executing it as a script.
    #    https://docs.python.org/3/library/__main__.html
    pass
