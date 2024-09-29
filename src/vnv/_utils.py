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
import tempfile
import logging
import shutil
import subprocess

from vnv.constants import BASE_DIR, VNV_PREFIX

__author__ = "Michael Mussato"
__copyright__ = "Michael Mussato"
__license__ = "MIT"

_logger = logging.getLogger(__name__)


# ---- Python API ----
# The functions defined in this section can be imported by users in their
# Python scripts/interactive interpreter, e.g. via
# `from vnv.skeleton import fib`,
# when using this Python module as a library.


def decode(
        b: bytes,
) -> str:
    """

    Args:
        b (bytes): bytes to decode

    Returns:
        utf-8 decoded bytes

    """
    _logger.debug(f"decoding {b=}...")

    return b.decode(encoding="utf-8").removesuffix("\n")


def _create_dirs(
        base_dir: str = BASE_DIR,
) -> dict[str, str]:
    """

    Args:
        base_dir:

    Returns (dict):
        base_dir: full path to base_dir
        venv_dir: full path to venv_dir
    """
    _logger.debug(f"_create_dirs {base_dir=}...")
    os.makedirs(
        name=base_dir,
        mode=0o700,
        exist_ok=True,
    )

    venv_dir = tempfile.mkdtemp(
        dir=base_dir,
        prefix=VNV_PREFIX,
    )
    _logger.info(f"{base_dir = }")
    _logger.info(f"{venv_dir = }")

    return {"base_dir": base_dir, "venv_dir": venv_dir}


def locate(
        *,
        base_dir: str = BASE_DIR,
        venv: str = None,
) -> None:
    """

    Args:
        base_dir: full path to venvs base dir
        base_dir: full path to venv
        venv: venv name
    """
    if venv is None:
        _path = base_dir
    else:
        _path = os.path.join(
            base_dir,
            venv,
        )
    subprocess.run(
        [
            shutil.which("xdg-open"),
            _path,
        ])

    return None


# ---- CLI ----
# The functions defined in this section are wrappers around the main Python
# API allowing them to be called directly from the terminal as a CLI
# executable/script.


if __name__ == "__main__":
    # ^  This is a guard statement that will prevent the following code from
    #    being executed in the case someone imports this file instead of
    #    executing it as a script.
    #    https://docs.python.org/3/library/__main__.html
    pass
