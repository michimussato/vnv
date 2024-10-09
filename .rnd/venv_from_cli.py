import os
import time
import shutil
import tempfile
import subprocess
import logging


logging.basicConfig(level=logging.INFO)
handler = logging.StreamHandler()
LOGGER = logging.getLogger(__name__)


PYTHON = r"/usr/bin/python3.9"
BASE_DIR = os.path.join(os.path.expanduser('~'), '.venv')


def decode(
        b: bytes,
) -> str:
    """

    Args:
        b (bytes): bytes to decode

    Returns:
        utf-8 decoded bytes

    """
    LOGGER.debug(f"decode...")

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
    LOGGER.debug(f"_create_dirs...")
    os.makedirs(
        name=base_dir,
        mode=0o700,
        exist_ok=True,
    )

    _prefix = f"venv_from_script__{time.strftime('%Y-%m-%d_%H-%M-%S')}__"

    venv_dir = tempfile.mkdtemp(
        dir=base_dir,
        prefix=_prefix,
    )
    LOGGER.info(f"{base_dir = }")
    LOGGER.info(f"{venv_dir = }")

    return {"base_dir": base_dir, "venv_dir": venv_dir}


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
    LOGGER.info(f"create_venv...")
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
    LOGGER.info(f"{decode(stdout) = }")
    LOGGER.info(f"{decode(stderr) = }")
    LOGGER.info(f"{dirs['venv_dir'] = }")

    return dirs["venv_dir"], decode(stdout), decode(stderr)


def upgrade_pip(
        venv_dir: str,
) -> None:
    """

    Args:
        venv_dir: full path to venv
    """
    LOGGER.info(f"upgrade_pip...")
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
        LOGGER.info(decode(line))

    return None


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
    LOGGER.info(f"upgrade_pip...")
    activate = os.path.join(venv_dir, "bin", "activate")

    _packages = ""

    if requirements:
        with open(requirements, "r") as fr:
            _packages += ",".join(fr.read().splitlines())
        LOGGER.info(f"{requirements = }")

    if packages:
        _packages = ",".join([_packages, packages])

    if all([requirements, packages]):
        LOGGER.debug(f"{requirements = }")
        LOGGER.debug(f"{packages = }")
        raise ValueError("requirements and packages cannot be specified at the same time")
    if not any([requirements, packages]):
        LOGGER.debug(f"{requirements = }")
        LOGGER.debug(f"{packages = }")
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
        LOGGER.info(decode(line))

    return None


def pip_freeze(
        venv_dir: str,
        *,
        requirements_base_dir: str = None
) -> None:
    """

    Args:
        venv_dir: full path to venv
        requirements_base_dir: directory of requirements.txt file to write
    """
    LOGGER.info(f"upgrade_pip...")
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
        "freeze",
        ">",
        os.path.join(
            requirements_base_dir,
            "requirements.txt",
        ),
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
        LOGGER.info(decode(line))

    return None


def enter_venv(
        venv_dir: str,
        *,
        delete_rcfile: bool = True,
) -> None:
    """

    Args:
        venv_dir: full path to venv
        delete_rcfile: keep or delete temporary venv rcfile
    """
    LOGGER.info(f"enter_venv...")
    LOGGER.info(f"{venv_dir = }")

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

        for alias in os.listdir(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "bashrc",
            )
        ):
            with open(
                    os.path.join(
                        os.path.dirname(os.path.realpath(__file__)),
                        "bashrc",
                        alias
                    )
            ) as _alias:
                tmp.writelines(_alias)

        # reset cursor (file is still open)
        tmp.seek(0)

        try:
            with open(tmp.name, "r") as tmp_inspect:
                LOGGER.info(f"{tmp.name = }")
                LOGGER.debug(tmp_inspect.read())

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
            LOGGER.error(e)

    return None


def get_venvs(
        base_dir: str = BASE_DIR,
) -> list[str]:
    """

    Args:
        base_dir: full path to venvs base dir

    Returns:
        list[str]: list of venv names
    """
    LOGGER.info(f"get_venvs...")
    _venvs = os.listdir(base_dir)
    LOGGER.info(f"{_venvs = }")
    return _venvs


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


def main():
    venv = create_venv()
    upgrade_pip(venv[0])
    pip_install_from_requirements(
        venv[0],
        requirements=os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "pip",
            "requirements.txt",
        ),
    )
    # # pip_install_from_requirements(venv[0], requirements="/home/michael/.venv/requirements.txt")
    # # pip_install_packages(venv[0], packages="dagster,dagster-webserver,DeepDiff")
    # pip_freeze(venv[0], requirements_base_dir=venv[1])
    locate(base_dir=venv[0])
    enter_venv(venv[0])
    # http://zed.github.io/GateOne/_modules/terminal.html#Terminal.dump_components


if __name__ == "__main__":
    main()
