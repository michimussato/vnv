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

import argparse
import logging
import sys

from vnv.logging import setup_logging

from vnv.create_venv import create_venv
from vnv.create_venv import add_sub_parser as add_sub_parser__create_venv

from vnv.upgrade_pip import upgrade_pip
from vnv.upgrade_pip import add_sub_parser as add_sub_parser__upgrade_pip

from vnv.pip_install import pip_install_packages, pip_install_from_requirements
from vnv.pip_install import add_sub_parser as add_sub_parser__pip_install

from vnv.enter_venv import enter_venv
from vnv.enter_venv import add_sub_parser as add_sub_parser__enter_venv

from vnv.list_venvs import list_venvs
from vnv.list_venvs import add_sub_parser as add_sub_parser__list_venvs

from vnv.pip_freeze import add_sub_parser as add_sub_parser__pip_freeze

from vnv import __version__

__author__ = "Michael Mussato"
__copyright__ = "Michael Mussato"
__license__ = "MIT"

_logger = logging.getLogger(__name__)


# ---- Python API ----
# The functions defined in this section can be imported by users in their
# Python scripts/interactive interpreter, e.g. via
# `from vnv.skeleton import fib`,
# when using this Python module as a library.


# ---- CLI ----
# The functions defined in this section are wrappers around the main Python
# API allowing them to be called directly from the terminal as a CLI
# executable/script.


def parse_args(args):
    """Parse command line parameters

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--help"]``).

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """

    parser__base = argparse.ArgumentParser(
        description=__doc__,
    )

    subparsers = parser__base.add_subparsers(
        description="sub-command help",
        required=True,
        dest="sub_command",
    )

    add_sub_parser__create_venv(subparsers)
    add_sub_parser__upgrade_pip(subparsers)
    add_sub_parser__pip_install(subparsers)
    add_sub_parser__enter_venv(subparsers)
    add_sub_parser__list_venvs(subparsers)
    add_sub_parser__pip_freeze(subparsers)

    parser__base.add_argument(
        "--version",
        action="version",
        version=f"VNV {__version__}",
    )

    parser__base.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO,
    )
    parser__base.add_argument(
        "-vv",
        "--very-verbose",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG,
    )
    return parser__base.parse_args(args)


def main(args):
    """Wrapper allowing :func:`fib` to be called with string arguments in a CLI fashion

    Instead of returning the value from :func:`fib`, it prints the result to the
    ``stdout`` in a nicely formatted message.

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--verbose", "42"]``).
    """
    args = parse_args(args)
    setup_logging(args.loglevel)

    if args.sub_command == "create-venv":
        _logger.debug("Subcommand: create-venv...")
        create_venv()
        _logger.debug("Subcommand: create-venv done.")

    if args.sub_command == "upgrade-pip":
        _logger.debug("Subcommand: upgrade-pip...")
        upgrade_pip(venv_dir=args.upgrade_pip)
        _logger.debug("Subcommand: upgrade-pip done.")

    if args.sub_command == "pip-install-from-requirements":
        _logger.debug("Subcommand: pip-install-from-requirements...")
        pip_install_from_requirements(
            venv_dir=args.venv_dir,
            requirements=args.install_from_requirements,
        )
        _logger.debug("Subcommand: pip-install-from-requirements done.")

    if args.sub_command == "pip-install-packages":
        _logger.debug("Subcommand: pip-install-packages...")
        pip_install_packages(
            venv_dir=args.venv_dir,
            packages=args.install_packages,
        )
        _logger.debug("Subcommand: pip-install-packages done.")

    if args.sub_command == "enter-venv":
        _logger.debug("Subcommand: enter-venv...")
        enter_venv(
            venv_dir=args.venv_dir,
        )
        _logger.debug("Subcommand: enter-venv done.")

    if args.sub_command == "list-venvs":
        _logger.debug("Subcommand: list-venvs...")
        list_venvs(
            base_dir=args.base_dir,
        )
        _logger.debug("Subcommand: list-venvs done.")


def run():
    """Calls :func:`main` passing the CLI arguments extracted from :obj:`sys.argv`

    This function can be used as entry point to create console scripts with setuptools.
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    # ^  This is a guard statement that will prevent the following code from
    #    being executed in the case someone imports this file instead of
    #    executing it as a script.
    #    https://docs.python.org/3/library/__main__.html

    # After installing your project with pip, users can also run your Python
    # modules as scripts via the ``-m`` flag, as defined in PEP 338::
    #
    #     python -m vnv.skeleton 42
    #
    #     python -m vnv.skeleton.create_venv
    #
    #
    run()
