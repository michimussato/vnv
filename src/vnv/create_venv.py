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

import subprocess
import logging
import sys

from vnv._utils import decode, _create_dirs

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


def create_venv(
        python: str = PYTHON,
) -> tuple[str, str, str]:
    """

    Args:
        python: path to python executable

    Returns:
        tuple[str, str, str]:
            full path to venv
            stdout
            stderr

    """
    _logger.info(f"create_venv {python=}...")

    dirs = _create_dirs()

    cmd = [
        python,
        "-m",
        "venv",
        dirs["venv_dir"],
    ]

    proc = subprocess.Popen(
        args=cmd,
        cwd=dirs["base_dir"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False,
    )

    stdout, stderr = proc.communicate()

    _logger.info(f"{decode(stdout)=}")
    _logger.info(f"{decode(stderr)=}")
    _logger.info(f"{dirs['venv_dir']=}")

    sys.stdout.writelines(
        f"Result:\n"
        f"{dirs['venv_dir']=}\n"
    )

    return dirs["venv_dir"], decode(stdout), decode(stderr)


# ---- CLI ----
# The functions defined in this section are wrappers around the main Python
# API allowing them to be called directly from the terminal as a CLI
# executable/script.


def add_sub_parser(subparsers):

    parser__create_venv = subparsers.add_parser(
        "create-venv",
        help="Create a virtual environment",
    )

    parser__create_venv.add_argument(
        "-p",
        "--python-interpreter",
        type=str,
        dest="python",
        required=False,
        default=PYTHON,
        help="--python-interpreter Help",
    )


if __name__ == "__main__":
    # ^  This is a guard statement that will prevent the following code from
    #    being executed in the case someone imports this file instead of
    #    executing it as a script.
    #    https://docs.python.org/3/library/__main__.html
    pass
