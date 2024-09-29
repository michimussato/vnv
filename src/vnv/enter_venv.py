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
import tempfile

__author__ = "Michael Mussato"
__copyright__ = "Michael Mussato"
__license__ = "MIT"

_logger = logging.getLogger(__name__)


# ---- Python API ----
# The functions defined in this section can be imported by users in their
# Python scripts/interactive interpreter, e.g. via
# `from vnv.skeleton import fib`,
# when using this Python module as a library.


def enter_venv(
        venv_dir: str,
        *,
        delete_rcfile: bool = True,  # Todo: CLI
) -> None:
    """

    Args:
        venv_dir: full path to venv
        delete_rcfile: keep or delete temporary venv rcfile
    """
    _logger.info(f"enter_venv...")
    _logger.info(f"{venv_dir = }")

    project_dir = venv_dir

    with tempfile.NamedTemporaryFile(
        delete=delete_rcfile,
        mode="w",
        prefix=".bashrc__",
    ) as tmp:
        # bash --rcfile with --login is not possible
        # so we get the content of .bashrc and add
        # it to tmp to mimic --login as current user
        with open(os.path.join(os.path.expanduser('~'), '.bashrc')) as bashrc:
            tmp.writelines(bashrc)

        tmp.write(f"source {venv_dir}/bin/activate\n")

        resources = os.path.join(
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(
                        os.path.realpath(__file__)
                    )
                )
            ),
            "resources",
            "bashrc",
        )

        for alias in os.listdir(resources):
            with open(
                    os.path.join(
                        resources,
                        alias
                    )
            ) as _alias:
                tmp.writelines(_alias)

        # reset cursor (file is still open)
        tmp.seek(0)

        try:
            with open(tmp.name, "r") as tmp_inspect:
                _logger.info(f"{tmp.name = }")
                _logger.debug(tmp_inspect.read())

            subprocess.run(
                [
                    "bash",
                    "--rcfile",
                    tmp.name,
                    "-i",
                ],
                cwd=project_dir,
                env={
                    **os.environ,
                    **{
                        "DAGSTER_CODE_LOCATIONS": os.path.join(venv_dir, "dagster_projects"),
                        "NEW_VAR": "NEW_VALUE",
                    }
                },
            )
        except Exception as e:
            _logger.error(e)

    return None


# ---- CLI ----
# The functions defined in this section are wrappers around the main Python
# API allowing them to be called directly from the terminal as a CLI
# executable/script.


def add_sub_parser(subparsers):

    parser__enter_venv = subparsers.add_parser(
        "enter-venv",
        help="Enter a virtual environment",
    )

    parser__enter_venv.add_argument(
        "-v",
        "--enter-venv-dir",
        type=str,
        dest="venv_dir",
        required=True,
        default=None,
        help="--enter-venv-dir Help",  # Todo
    )


if __name__ == "__main__":
    # ^  This is a guard statement that will prevent the following code from
    #    being executed in the case someone imports this file instead of
    #    executing it as a script.
    #    https://docs.python.org/3/library/__main__.html
    pass
