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
import logging

from vnv.constants import BASE_DIR

__author__ = "Michael Mussato"
__copyright__ = "Michael Mussato"
__license__ = "MIT"

_logger = logging.getLogger(__name__)


# ---- Python API ----
# The functions defined in this section can be imported by users in their
# Python scripts/interactive interpreter, e.g. via
# `from vnv.skeleton import fib`,
# when using this Python module as a library.


def list_venvs(
        base_dir: str = BASE_DIR,
) -> list[str]:
    """

    Args:
        base_dir: full path to venvs base dir

    Returns:
        list[str]: list of venv names
    """
    _logger.info(f"get_venvs...")
    _venvs = os.listdir(base_dir)
    _logger.info(f"{_venvs=}")
    return _venvs


# ---- CLI ----
# The functions defined in this section are wrappers around the main Python
# API allowing them to be called directly from the terminal as a CLI
# executable/script.


def add_sub_parser(subparsers):

    parser__create_venv = subparsers.add_parser(
        "list-venvs",
        help="List virtual environments in directory",
    )

    parser__create_venv.add_argument(
        "-l",
        "--list-venvs-in-directory",
        type=str,
        dest="base_dir",
        required=False,
        default=BASE_DIR,
        help="--list-venvs-in-directory Help",
    )


if __name__ == "__main__":
    # ^  This is a guard statement that will prevent the following code from
    #    being executed in the case someone imports this file instead of
    #    executing it as a script.
    #    https://docs.python.org/3/library/__main__.html
    pass
