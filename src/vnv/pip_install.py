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


def pip_install_from_requirements(
        venv_dir: str,
        requirements: str,
) -> None:
    """

    Args:
        venv_dir: full path to venv
        requirements: full path to requirements.txt file
    """
    _pip_install(
        venv_dir=venv_dir,
        requirements=requirements,
    )

    return None


def pip_install_packages(
        venv_dir: str,
        packages: str,
) -> None:
    """

    Args:
        venv_dir: full path to venv
        packages: comma separated list of packages to install
    """
    _pip_install(
        venv_dir=venv_dir,
        packages=packages,
    )

    return None


def _pip_install(
        venv_dir: str,
        *,
        requirements: str = None,
        packages: str = None,
) -> None:
    """

    Args:
        venv_dir (str): path to venv
        requirements (str): path to requirements.txt file
        packages (str): comma separated list of packages to install
    """
    _logger.info(f"upgrade_pip...")
    activate = os.path.join(venv_dir, "bin", "activate")

    _packages = ""

    if requirements:
        with open(requirements, "r") as fr:
            _packages += ",".join(fr.read().splitlines())
        _logger.info(f"{requirements = }")

    if packages:
        _packages = ",".join([_packages, packages])

    if all([requirements, packages]):
        _logger.debug(f"{requirements=}")
        _logger.debug(f"{packages=}")
        raise ValueError("requirements and packages cannot be specified at the same time")
    if not any([requirements, packages]):
        _logger.debug(f"{requirements=}")
        _logger.debug(f"{packages=}")
        raise ValueError("requirements and packages cannot be unspecified at the same time")

    cmd = [
        "source",
        activate,
        "&&",
        "pip",
        "install",
        *_packages.split(","),
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

    return None


# ---- CLI ----
# The functions defined in this section are wrappers around the main Python
# API allowing them to be called directly from the terminal as a CLI
# executable/script.


def add_sub_parser(subparsers):

    parser__pip_install_packages = subparsers.add_parser(
        "pip-install-packages",
        help="Supply comma-separated list of packages to install",
    )

    parser__pip_install_packages.add_argument(
        "-vnv",
        "--venv-dir",
        type=str,
        dest="venv_dir",
        required=True,
        default=None,
        help="--venv-path Help",  # Todo
    )

    parser__pip_install_packages.add_argument(
        "-i",
        "--install-packages",
        type=str,
        dest="install_packages",
        required=True,
        default=None,
        help="--install-packages Help",  # Todo
    )

    parser__pip_install_from_requirements = subparsers.add_parser(
        "pip-install-from-requirements",
        help="Supply path to requirements.txt file",
    )

    parser__pip_install_from_requirements.add_argument(
        "-vnv",
        "--venv-dir",
        type=str,
        dest="venv_dir",
        required=True,
        default=None,
        help="--venv-path Help",  # Todo
    )

    parser__pip_install_from_requirements.add_argument(
        "-i",
        "--install-from-requirements",
        type=str,
        dest="install_from_requirements",
        required=True,
        default=None,
        help="-install-from-requirements Help",  # Todo
    )


if __name__ == "__main__":
    # ^  This is a guard statement that will prevent the following code from
    #    being executed in the case someone imports this file instead of
    #    executing it as a script.
    #    https://docs.python.org/3/library/__main__.html
    pass
