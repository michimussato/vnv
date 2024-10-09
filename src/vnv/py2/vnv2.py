#!/usr/bin/python
import getpass
import json
import os
import pprint
import sys
import glob
import copy
import re
import subprocess
import imp
import tempfile
import logging
import argparse
import ast

# from ...vnv import __version__

__author__ = "Michael Mussato"
__copyright__ = "Michael Mussato"
__license__ = "MIT"

_logger = logging.getLogger(__name__)


try:
    with open(os.path.expanduser(os.path.join("~", ".config", "vnv.json")), "r") as fr:
        VNV_CONF = json.load(fr)
except IOError:
    with open(os.path.expanduser(os.path.join("~", ".config", "vnv.json")), "w") as fw:
        VNV_CONF = {
            "PYTHONS_BASE": "/film/tools/packages/python",
            "EXE_VSCODE": "/usr/bin/code",
            "EXE_PYCHARM": "/opt/pycharm-community-2020.1.1/bin/pycharm.sh",
        }
        json.dump(VNV_CONF, fw, indent=2)


# setup
# git clone
# git checkout
# vanilla shell (python2.7)
# python vnv/src/vnv/py2/vnv2.py install
# vnv2 --help


def install():
    file_path = os.path.realpath(__file__)
    try:
        os.makedirs(os.path.join(os.path.expanduser("~"), ".local", "bin"))
    except OSError as e:
        _logger.debug("Directoy already exists: {e}".format(e=e))

    dst = os.path.join(os.path.expanduser("~"), ".local", "bin", "vnv2")

    try:
        os.symlink(file_path, dst)
    except OSError as e:
        _logger.debug("Symlink already exists: {e}".format(e=e))
    os.chmod(dst, 0o755)

    sys.stdout.writelines(
        "# Result:\n"
        "# installed: {dst}\n".format(
            dst=dst,
        )
    )


def uninstall():
    dst = os.path.join(os.path.expanduser("~"), ".local", "bin", "vnv2")
    os.remove(dst)

    sys.stdout.writelines(
        "# Result:\n"
        "# uninstalled: {dst}\n".format(
            dst=dst,
        )
    )


def _parse_pythons():

    packages_py = glob.glob(os.path.join(VNV_CONF["PYTHONS_BASE"], "*", "package.py"))

    pythons_ = []

    for package_py in packages_py:

        sys.path.insert(0, os.path.dirname(package_py))
        try:
            imp.reload(tmp_package)
        except NameError as e:
            import package as tmp_package
        package_ = {}
        package_["package"] = package_py
        package_["version"] = tmp_package.version
        package_["variants"] = tmp_package.variants
        package_["requires"] = tmp_package.requires
        pythons_.append(copy.deepcopy(package_))
        sys.path.pop(0)

    return pythons_


def list_pythons():
    pythons = _parse_pythons()

    pythons_ = []

    python_package = {}

    # for paths like
    # - /film/tools/packages/python/3.10.13.1/vfx_cxx-2021.0/openssl-1.1.1/zlib-1.2.8_thru_2
    mappings = {
        "+<2": "_thru_2",
    }

    for python in pythons:
        for variant in python["variants"]:

            python_package["version"] = python["version"]
            python_package["version_tuple"] = tuple([int(u) for u in python["version"].split('.')])
            for k, v in mappings.items():
                python_package["variant"] = os.sep.join(variant).replace(k, v)  # .partition("+<")[0]
            python_package["lib"] = os.path.join(VNV_CONF["PYTHONS_BASE"], python["version"], python_package["variant"], "lib")
            python_package["bin"] = os.path.join(VNV_CONF["PYTHONS_BASE"], python["version"], python_package["variant"], "bin")
            python_package["exe"] = os.path.join(python_package["bin"], "python")

            _logger.debug("Python found: {python_package}".format(python_package=python_package))
            pythons_.append(copy.deepcopy(python_package))

            # sys.stdout.writelines(
            #     "Result:\n"
            #     "cmd = {cmd}:\n"
            #     "{json_out}\n".format(
            #         cmd=cmd,
            #         json_out=json_out.name,
            #     )
            # )

    # return sorted(pythons_, key=lambda d: d["version"])
    # sorts 1.2 after 1.2.3 which is wrong, therefore:
    return sorted(pythons_, key=lambda d: d["version_tuple"])


def launch_python(
        python_dict=None,
        from_file=None,
        c=None,
        m=None,
):
    if (
            all([python_dict, from_file])
            or not any([python_dict, from_file])
    ):
        raise Exception("Specify EITHER --python-dict OR --from-file.")

    if isinstance(python_dict, str):
        python_dict = ast.literal_eval(python_dict)
        print python_dict

    if all([c, m]):
        raise Exception("Specify EITHER -c OR -m, not both.")

    if from_file is not None:
        with open(from_file, "r") as fr:
            python_dict = json.load(fr)

    args = [
        python_dict["exe"],
    ]

    if c is not None:
        args.extend(
            [
                "-c",
                "{command}".format(command=c)
            ]
        )

    if m is not None:
        args.append("-m")
        args.extend(
            "{command}".format(command=m).split(" ")
        )

    env = copy.deepcopy(os.environ)

    env_update = {
        "LD_LIBRARY_PATH": os.pathsep.join(
            [
                "/film/tools/packages/python/3.9.7.3/openssl-1.1.1/lib",
                "/film/tools/packages/zlib/1.2.11/lib",
                "/film/tools/packages/openssl/1.1.1.6/CentOS-7.8/vfx_cxx-2021.0/lib",
                python_dict["lib"],

            ]
        ),
        # "PATH": os.pathsep.join([
        #     "/film/tools/packages/cache/python/3.10.13.1/vfx_cxx-2021.0/openssl-1.1.1/zlib-1.2.8_thru_2/CentOS-7/lib",
        #     os.environ["PATH"],
        # ])
    }

    env.update(env_update)

    subprocess.call(
        args=args,
        # cwd=python["exe"],
        env=env,
    )

    return env_update


def filter_version(
        pythons,  # list
        equal_or_greater_than,  # tuple,
        but_less_than,  # tuple
):
    if isinstance(equal_or_greater_than, str):
        equal_or_greater_than = ast.literal_eval(equal_or_greater_than)
        # equal_or_greater_than = equal_or_greater_than.replace(" ", "")
        # equal_or_greater_than = tuple(int(i) for i in equal_or_greater_than.split("."))

    if isinstance(but_less_than, str):
        but_less_than = ast.literal_eval(but_less_than)
        # but_less_than = but_less_than.replace(" ", "")
        # but_less_than = tuple(int(i) for i in but_less_than.split("."))

    _logger.info("Equal or greater than: {equal_or_greater_than}".format(equal_or_greater_than=equal_or_greater_than))
    _logger.info("But less than: {but_less_than}".format(but_less_than=but_less_than))

    return list(filter(lambda d: equal_or_greater_than <= d["version_tuple"] < but_less_than, pythons))


def get_pythonpaths_from_preset(launcher_preset):

    with tempfile.NamedTemporaryFile(
        mode="w",
        delete=False,
        suffix=".py",
    ) as python_script:


        json_out = tempfile.NamedTemporaryFile(
            mode="w",
            delete=False,
            prefix="pythonpaths.",
            suffix=".json",
        )

        python_script.write(
        """
# Dynamic script to export ENV VARS to file
import os
import json

p = dict()
p["PYTHONPATH"] = os.environ["PYTHONPATH"].split(os.pathsep)
p["PYTHON_EXE"] = os.environ["PYTHON_EXE"]

with open(\"{out_json}\", "w") as fw:
    json.dump(p, fw, indent=2)

""".format(out_json=json_out.name)
        )

        python_script.seek(0)

        script_args = []
        script_args.append(python_script.name)

        cmd = [
            'rez',
            'env',
            'launcher2CL',
            '-c',
            '$LAUNCH_EXE -l shell -p {AL_LAUNCHER_PRESET} -c \"python {script_args}\"'.format(
                AL_LAUNCHER_PRESET=launcher_preset,
                script_args=" ".join(script_args),
            )
        ]

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        for line in proc.stdout:
            print line.rstrip("\n")
            # _logger.info(decode(line))

        sys.stdout.writelines(
            "# Result:\n"
            "# cmd = {cmd}\n"
            "# {json_out}\n".format(
                cmd=cmd,
                json_out=json_out.name,
            )
        )

        return json_out.name


def get_pythonpaths_from_packages(packages):

    with tempfile.NamedTemporaryFile(
        mode="w",
        delete=False,
        suffix=".py",
    ) as python_script:

        json_out = tempfile.NamedTemporaryFile(
            mode="w",
            delete=False,
            suffix=".json",
        )

        python_script.write(
        """
# Dynamic script to export ENV VARS to file
import os
import json

p = dict()
p["PYTHONPATH"] = os.environ["PYTHONPATH"].split(os.pathsep)
p["PYTHON_EXE"] = os.environ["PYTHON_EXE"]

with open(\"{out_json}\", "w") as fw:
    json.dump(p, fw, indent=2)

""".format(out_json=json_out.name)
        )

        python_script.seek(0)

        script_args = []
        script_args.append(python_script.name)

        cmd = [
            'rez',
            'env',
        ]
        cmd.extend(packages.split(","))
        cmd.extend(
            [
                '-c',
                "python {script_args}".format(
                    script_args=" ".join(script_args),
                )
            ]
        )

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        for line in proc.stdout:
            print line.rstrip("\n")
            # _logger.info(decode(line))

        sys.stdout.writelines(
            "# Result:\n"
            "# cmd = {cmd}:\n"
            "# {json_out}\n".format(
                cmd=cmd,
                json_out=json_out.name,
            )
        )

        return json_out.name


def get_python_dict_from_exe(
        exe=None,
        jsn=None,
        to_file=False,
):

    if all([exe, jsn]) or not any([exe, jsn]):
        raise Exception("Specify EITHER --exe OR --jsn, "
                        "not none or both.")

    _exe = None

    if jsn is not None:
        with open(jsn, "r") as fr:
            _exe = json.load(fr)["PYTHON_EXE"]
    elif exe is not None:
        _exe = exe

    pythons = list_pythons()

    matches = []

    for python in pythons:

        regex = "(\/film\/tools\/packages\/:?)(.*)(python\/:?)({version}\/)({variant}\/)(.*)".format(
            version=python["version"],
            variant=python["variant"],
        )

        if re.match(regex, _exe) is not None:
            matches.append(copy.deepcopy(python))

    if not bool(matches):
        raise Exception("No matches.")
    elif len(matches) > 1:
        raise Exception("Too many matches.")

    sys.stdout.writelines(
        "# Result:\n"
        "# {match}\n".format(match=matches[0])
    )

    if to_file:
        with tempfile.NamedTemporaryFile(
            mode="w",
            delete=False,
            suffix=".json",
        ) as fw:
            json.dump(matches[0], fw, indent=2)

        sys.stdout.writelines(
            "# {fw}\n".format(fw=fw.name)
        )

    return matches[0]


def create_venv(
        venv_home,
        venv_name,
        python_dict=None,
        from_file=None,
):
    if (
            all([python_dict, from_file])
            or not any([python_dict, from_file])
    ):
        raise Exception("Specify EITHER --python-dict OR --from-file.")

    if not all([VNV_CONF["EXE_VSCODE"], VNV_CONF["EXE_PYCHARM"]]):
        raise Exception("Set `EXE_VSCODE` and `EXE_PYCHARM` "
                        "before running this sub-command.")

    if isinstance(python_dict, str):
        python_dict = ast.literal_eval(python_dict)
    venv = os.path.expanduser(os.path.join(venv_home, venv_name))

    if from_file is not None:
        with open(from_file, "r") as fr:
            python_dict = json.load(fr)

    env = launch_python(python_dict=python_dict, m="venv {venv}".format(venv=venv))

    activate = os.path.join(venv, "al_activate")

    with open(activate, "w") as fw:
        fw.write("export LD_LIBRARY_PATH={env};\n".format(env=env["LD_LIBRARY_PATH"]))
        fw.write("export PYTHONUSERBASE=$(echo ${VIRTUAL_ENV});\n")  # Todo: necessary?
        fw.write('SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd );\n')
        fw.write("{activate}".format(activate="source $SCRIPT_DIR/bin/activate;\n".format(venv=venv)))
        fw.write("export PYTHONUSERBASE=$(echo ${VIRTUAL_ENV});\n")

    py_exe_ide = os.path.join(venv, "python")

    with open(py_exe_ide, "w") as fw:
        fw.write("#!/bin/sh\n")
        fw.write("export LD_LIBRARY_PATH={env};\n".format(env=env["LD_LIBRARY_PATH"]))
        fw.write("export PYTHONUSERBASE=$(echo ${VIRTUAL_ENV});\n")  # Todo: necessary?
        fw.write('SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd );\n')
        fw.write('$SCRIPT_DIR/bin/python "$@";\n')
        fw.write("exit 0\n")

    os.chmod(py_exe_ide, 0o0744)

    pycharm_exe = os.path.join(venv, "pycharm")

    with open(pycharm_exe, "w") as fw:
        fw.write("#!/bin/sh\n")
        fw.write("source {activate}\n".format(activate=activate))
        fw.write("/usr/bin/sh {pycharm_sh};\n".format(pycharm_sh=VNV_CONF["EXE_PYCHARM"]))
        fw.write("exit 0\n")

    os.chmod(pycharm_exe, 0o0744)

    vscode_exe = os.path.join(venv, "vscode")

    with open(vscode_exe, "w") as fw:
        fw.write("#!/bin/sh\n")
        fw.write("source {activate}\n".format(activate=activate))
        fw.write("{vscode_sh};\n".format(vscode_sh=VNV_CONF["EXE_VSCODE"]))
        fw.write("exit 0\n")

    os.chmod(vscode_exe, 0o0744)

    sys.stdout.writelines(
        "# Result:\n"
        "# venv = {venv}\n"
        "# python = {py_exe_ide}\n"
        "# vscode = {vscode_exe}\n"
        "# pycharm = {pycharm_exe}\n"
        "# activate: `source {activate}`\n".format(
            py_exe_ide=py_exe_ide,
            vscode_exe=vscode_exe,
            pycharm_exe=pycharm_exe,
            venv=venv,
            activate=activate,
        )
    )

    return venv


def pythonpath_to_txt(pythonpath):
    if isinstance(pythonpath, str):
        with open(pythonpath, "r") as fr:
            pythonpath = json.load(fr)["PYTHONPATH"]
    with tempfile.NamedTemporaryFile(
        mode="w",
        prefix="pythonpath.",
        suffix=".txt",
        delete=False,
    ) as fw:
        fw.write(os.pathsep.join(pythonpath))

    sys.stdout.writelines(
        "# Result:\n"
        "# {name}\n".format(name=fw.name)
    )

    return fw.name


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
        # required=False,
        dest="sub_command",
    )

    # Example
    # python /home/users/michaelmus/git/repos/vnv/src/vnv/py2/vnv2.py install
    subparser__setup = subparsers.add_parser(
        "install",
        help="Writes a symlink to `~/.local/bin`.",
    )

    # Example
    # python /home/users/michaelmus/git/repos/vnv/src/vnv/py2/vnv2.py uninstall
    # vnv2 uninstall
    subparser__setup = subparsers.add_parser(
        "uninstall",
        help="Deletes the symlink in `~/.local/bin`.",
    )

    subparser__list_pythons = subparsers.add_parser(
        "list-pythons",
        help="List all Python executables in `{PYTHONS_BASE}` "
             "and present them as `python_dict`.".format(PYTHONS_BASE=VNV_CONF["PYTHONS_BASE"]),
    )

    # Examples
    # # python /home/users/michaelmus/git/repos/vnv/src/vnv/py2/vnv2.py filter-versions -get "(3,7,0)" -blt "(3,8)" -p $(python /home/users/michaelmus/git/repos/vnv/src/vnv/py2/vnv2.py -v list-pythons)
    # python /home/users/michaelmus/git/repos/vnv/src/vnv/py2/vnv2.py filter-versions -get "(3,7,5)" -blt "(3,7,5,2)"
    subparser__filter_versions = subparsers.add_parser(
        "filter-versions",
        help="Search for a specific range of versions "
             "in the `python_dict`s list.",
    )
    # subparser__filter_versions.add_argument(
    #     "-p",
    #     "--pythons",
    #     dest="pythons",
    #     type=list,
    #     required=True,
    #     help="List of python_dicts."
    # )
    subparser__filter_versions.add_argument(
        "-get",
        "--equal-or-greater-than",
        dest="equal_or_greater_than",
        type=str,
        required=True,
        help="Greater or equal than `tuple`, i.e. '(3,5,9)'",
    )
    subparser__filter_versions.add_argument(
        "-blt",
        "--but-less-than",
        dest="but_less_than",
        type=str,
        required=True,
        help="But less than `tuple`, i.e. '(3,11)'",
    )

    subparser__launch_python = subparsers.add_parser(
        "launch-python",
        help="Run a Python interpreter from a `python_dict`. "
             "Optionally run a package `-m` or a "
             "command `-c`.",
    )
    group__subparser__launch_python_dict_from = subparser__launch_python.add_mutually_exclusive_group(
        required=True,
    )
    group__subparser__launch_python_dict_from.add_argument(
        "-p",
        "--python-dict",
        type=str,
        required=False,
        default=None,
        dest="python_dict",
        help="Python represented in `python_dict` as string.",
    )
    group__subparser__launch_python_dict_from.add_argument(
        "-ff",
        "--from-file",
        type=str,
        required=False,
        default=None,
        dest="from_file",
        help="Python represented in `python_dict` from json file.",
    )
    group__subparser__launch_python = subparser__launch_python.add_mutually_exclusive_group(
        required=False,
    )
    # Example
    # python /home/users/michaelmus/git/repos/vnv/src/vnv/py2/vnv2.py launch-python -c 'import os;print(os.environ)' -p "{'bin': '/film/tools/packages/python/3.9.7.3/openssl-1.1.1/bin', 'exe': '/film/tools/packages/python/3.9.7.3/openssl-1.1.1/bin/python', 'lib': '/film/tools/packages/python/3.9.7.3/openssl-1.1.1/lib', 'variant': 'openssl-1.1.1', 'version': '3.9.7.3', 'version_tuple': (3, 9, 7, 3)}"
    group__subparser__launch_python.add_argument(
        "-c",
        type=str,
        required=False,
        dest="c",
        help="As in `python -c 'import os;print(os.environ);print(os.getcwd())'`.",
    )
    # Example
    # python /home/users/michaelmus/git/repos/vnv/src/vnv/py2/vnv2.py launch-python -m 'venv /home/users/michaelmus/.venv1234' -p "{'bin': '/film/tools/packages/python/3.9.7.3/openssl-1.1.1/bin', 'exe': '/film/tools/packages/python/3.9.7.3/openssl-1.1.1/bin/python', 'lib': '/film/tools/packages/python/3.9.7.3/openssl-1.1.1/lib', 'variant': 'openssl-1.1.1', 'version': '3.9.7.3', 'version_tuple': (3, 9, 7, 3)}"
    # {'bin': '/film/tools/packages/python/3.9.7.3/openssl-1.1.1/bin', 'version_tuple': (3, 9, 7, 3), 'exe': '/film/tools/packages/python/3.9.7.3/openssl-1.1.1/bin/python', 'lib': '/film/tools/packages/python/3.9.7.3/openssl-1.1.1/lib', 'variant': 'openssl-1.1.1', 'version': '3.9.7.3'}
    group__subparser__launch_python.add_argument(
        "-m",
        type=str,
        required=False,
        dest="m",
        help="As in `python -m 'venv /path/to/venv'`.",
    )

    subparser__get_pythonpaths_from_preset = subparsers.add_parser(
        "get-pythonpaths-from-preset",
        help="Extract `PYTHONPATH` from a resolved Launcher Preset.",
    )
    # Example
    # python /home/users/michaelmus/git/repos/vnv/src/vnv/py2/vnv2.py get-pythonpaths-from-preset -p "/toolsets/personal/michaelmus/012_Maya_performance_production"
    # vnv2 get-pythonpaths-from-preset -p "/toolsets/personal/michaelmus/012_Maya_performance_production"
    subparser__get_pythonpaths_from_preset.add_argument(
        "-p",
        "--preset",
        type=str,
        required=True,
        dest="launcher_preset",
        help="The full path to the Launcher Preset, "
             "i.e '/toolsets/personal/michaelmus/012_Maya_performance_production'",
    )

    subparser__get_python_dict_from_exe = subparsers.add_parser(
        "get-python-dict-from-exe",
        help="Parse a JSON file or directly resolve a Python "
             "executable path into a `python_dict`.",
    )
    # Example
    # vnv2 get-python-dict-from-exe -e "/film/tools/packages/cache/python/3.9.7.3/openssl-1.1.1/bin/python3.9"
    # vnv2 get-python-dict-from-exe -j "/tmp/pythonpaths.tmp3D6Ndj.json"
    group__subparser__get_python_dict_from_exe = subparser__get_python_dict_from_exe.add_mutually_exclusive_group(
        required=False,
    )
    group__subparser__get_python_dict_from_exe.add_argument(
        "-e",
        "--exe",
        type=str,
        required=False,
        dest="exe",
        help="Get the `python_dict` representation of any python exe on the file system. "
             "i.e. '/film/tools/packages/cache/python/3.9.7.3/openssl-1.1.1/bin/python3.9'.",
    )
    group__subparser__get_python_dict_from_exe.add_argument(
        "-j",
        "--jsn",
        type=str,
        required=False,
        dest="jsn",
        help="Get the `python_dict` representation of any python exe on the file system. "
             "i.e. use `--json` to specify a `.json` file that was created "
             "using `get-pythonpaths-from-preset`.",
    )
    subparser__get_python_dict_from_exe.add_argument(
        "-tf",
        "--to-file",
        # type=bool,
        required=False,
        # default=False,
        action="store_true",
        dest="to_file",
        help="Write output to a temporary file."
    )

    subparser__pythonpath_to_txt = subparsers.add_parser(
        "pythonpath-to-txt",
        help="Parse individual `PYTHONPATH` items from a json file "
             "(i.e. created by `get-pythonpaths-from-preset` into a "
             "single `str` and write it to file.",
    )
    # Example
    # python /home/users/michaelmus/git/repos/vnv/src/vnv/py2/vnv2.py pythonpath-to-txt -p /tmp/pythonpaths.tmpjVI8zK.json
    subparser__pythonpath_to_txt.add_argument(
        "-p",
        "--pythonpath",
        type=str,
        dest="pythonpath",
        required=True,
        help="Specify path to json file that contains the pythonpaths. "
             "i.e. from `get-pythonpaths-from-preset`.",
    )

    # Example
    # python /home/users/michaelmus/git/repos/vnv/src/vnv/py2/vnv2.py create-venv -p "{'bin': '/film/tools/packages/python/3.9.7.3/openssl-1.1.1/bin', 'exe': '/film/tools/packages/python/3.9.7.3/openssl-1.1.1/bin/python', 'lib': '/film/tools/packages/python/3.9.7.3/openssl-1.1.1/lib', 'variant': 'openssl-1.1.1', 'version': '3.9.7.3', 'version_tuple': (3, 9, 7, 3)}" -vh "/home/users/michaelmus/temp" -vn "my-new-venv"
    # vnv2 create-venv -p "{'bin': '/film/tools/packages/python/3.9.7.3/openssl-1.1.1/bin', 'exe': '/film/tools/packages/python/3.9.7.3/openssl-1.1.1/bin/python', 'lib': '/film/tools/packages/python/3.9.7.3/openssl-1.1.1/lib', 'variant': 'openssl-1.1.1', 'version': '3.9.7.3', 'version_tuple': (3, 9, 7, 3)}" -vh "/home/users/michaelmus/temp" -vn "my-new-venv"
    subparser__create_venv = subparsers.add_parser(
        "create-venv",
        help="Create a `venv` based on a `python_dict` Python "
             "representation (Python 3+).",
    )
    group__subparser__create_venv = subparser__create_venv.add_mutually_exclusive_group(
        required=True,
    )
    group__subparser__create_venv.add_argument(
        "-p",
        "--python-dict",
        required=False,
        default=None,
        type=str,
        dest="python_dict",
        help="The Python interpreter represented as "
             "`python_dict` as string.",
    )
    group__subparser__create_venv.add_argument(
        "-ff",
        "--from-file",
        required=False,
        type=str,
        dest="from_file",
        default=None,
        help="The Python interpreter represented as "
             "`python_dict` from json file.",
    )
    subparser__create_venv.add_argument(
        "-vh",
        "--venv-home",
        required=True,
        type=str,
        dest="venv_home",
        help="The full path to the parent directory "
             "i.e. `/path/to/venvs/parent/`.",
    )
    subparser__create_venv.add_argument(
        "-vn",
        "--venv-name",
        required=True,
        type=str,
        dest="venv_name",
        help="The name of the `venv` that will be created "
             "within the `--venv-home`, i.e. "
             "`my-new-venv`.",
    )

    # parser__base.add_argument(
    #     "--version",
    #     action="version",
    #     version="VNV {version}".format(version=__version__),
    # )

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


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )


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

    if args.sub_command == "install":
        print "install"
        install()

    if args.sub_command == "uninstall":
        print "uninstall"
        uninstall()

    if args.sub_command == "list-pythons":
        print "list-pythons"
        result = list_pythons()
        pprint.pprint(result)

    if args.sub_command == "filter-versions":
        print "filter-versions"
        result = filter_version(
            # Todo: pythons=args.pythons,
            pythons=list_pythons(),
            equal_or_greater_than=args.equal_or_greater_than,
            but_less_than=args.but_less_than,
        )
        pprint.pprint(result)

    if args.sub_command == "launch-python":
        if not all(
                [
                    args.c,
                    args.m,
                ],
        ):
            launch_python(
                python_dict=args.python_dict,
                from_file=args.from_file,
            )

        else:
            if args.c is not None:
                launch_python(
                    python_dict=args.python_dict,
                    from_file=args.from_file,
                    c=args.c,
                )
            elif args.m is not None:
                launch_python(
                    python_dict=args.python_dict,
                    from_file=args.from_file,
                    m=args.m
                )

    if args.sub_command == "get-pythonpaths-from-preset":
        print "get-pythonpaths-from-preset"
        result = get_pythonpaths_from_preset(
            launcher_preset=args.launcher_preset,
        )

    if args.sub_command == "get-python-dict-from-exe":
        print "get-python-dict-from-exe"
        if args.exe is not None:
            print "from exe"
            result = get_python_dict_from_exe(
                exe=args.exe,
                to_file=args.to_file,
            )
        elif args.jsn is not None:
            print "from json"
            result = get_python_dict_from_exe(
                jsn=args.jsn,
                to_file=args.to_file,
            )

    if args.sub_command == "pythonpath-to-txt":
        print "pythonpath-to-txt"
        result = pythonpath_to_txt(
            pythonpath=args.pythonpath,
        )

    if args.sub_command == "create-venv":
        print "create-venv"
        result = create_venv(
            python_dict=args.python_dict,
            from_file=args.from_file,
            venv_home=args.venv_home,
            venv_name=args.venv_name,
        )


def run():
    """Calls :func:`main` passing the CLI arguments extracted from :obj:`sys.argv`

    This function can be used as entry point to create console scripts with setuptools.
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
    # next steps
    #
    # source /home/users/michaelmus/git/repos/AL_Sandbox/michaelmus/test_venv/test5/al_activate
    # python -m pip install --upgrade pip
    # pip install wheel wheel-filename
    # pip install six marshmallow requests future brotli numpy distro simplejson
    # pushd /home/users/michaelmus/git/repos/vnv
    # pip install -e .
    # popd
    # python /home/users/michaelmus/git/repos/vnv/src/vnv/pip_install_al.py --serial --from-file /tmp/pythonpath.NbtqlL.txt
    # pycharm: /home/users/michaelmus/git/repos/AL_Sandbox/michaelmus/test_venv/test5/pycharm

