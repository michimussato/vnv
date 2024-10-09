from os import makedirs
from venv import create
from os.path import join, expanduser
from tempfile import mkdtemp


base_dir = join(expanduser('~'), '.venv')
makedirs(
    name=base_dir,
    mode=0o700,
    exist_ok=True
)
venv_dir = mkdtemp(dir=base_dir, prefix='venv_from_script')
create(
    env_dir=venv_dir,
    with_pip=True,
    system_site_packages=False,
    clear=False,
    symlinks=False,
    prompt=None,
    upgrade_deps=False,
)


def main():
    pass


if __name__ == "__main__":
    main()
