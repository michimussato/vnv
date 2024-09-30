import json
import os
import sys
import glob
import copy
import re
import subprocess
import imp
import tempfile


PYTHONS_BASE = "/film/tools/packages/python"


def _parse_pythons():

    packages_py = glob.glob(os.path.join(PYTHONS_BASE, "*", "package.py"))

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
            python_package["lib"] = os.path.join(PYTHONS_BASE, python["version"], python_package["variant"], "lib")
            python_package["bin"] = os.path.join(PYTHONS_BASE, python["version"], python_package["variant"], "bin")
            python_package["exe"] = os.path.join(python_package["bin"], "python")

            pythons_.append(copy.deepcopy(python_package))

    # return sorted(pythons_, key=lambda d: d["version"])
    # sorts 1.2 after 1.2.3 which is wrong, therefore:
    return sorted(pythons_, key=lambda d: d["version_tuple"])


def launch_python(python_dict, c=None, m=None):

    if all([c, m]):
        raise Exception("Specify EITHER -c OR -m, not both.")

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
            "Result:\n"
            "cmd = {cmd}:\n"
            "{json_out}\n".format(
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
            "Result:\n"
            "cmd = {cmd}:\n"
            "{json_out}\n".format(
                cmd=cmd,
                json_out=json_out.name,
            )
        )

        return json_out.name


def get_python_from_exe(exe):
    pythons = list_pythons()

    matches = []

    for python in pythons:

        regex = "(\/film\/tools\/packages\/:?)(.*)(python\/:?)({version}\/)({variant}\/)(.*)".format(
            version=python["version"],
            variant=python["variant"],
        )

        if re.match(regex, exe) is not None:
            matches.append(copy.deepcopy(python))

    if not bool(matches):
        raise Exception("No matches.")
    elif len(matches) > 1:
        raise Exception("Too many matches.")

    sys.stdout.writelines(
        "Result:\n"
        "{match}\n".format(match=matches[0])
    )

    return matches[0]


def create_venv(py_dict, venv_home, venv_name):
    venv = os.path.join(venv_home, venv_name)
    env = launch_python(python_dict=py_dict, m="venv {venv}".format(venv=venv))

    activate = os.path.join(venv, "al_activate")

    with open(activate, "w") as fw:
        fw.write("export LD_LIBRARY_PATH={env};\n".format(env=env["LD_LIBRARY_PATH"]))
        fw.write("export PYTHONUSERBASE=$(echo ${VIRTUAL_ENV});\n")  # Todo: necessary?
        fw.write('SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd );\n')
        fw.write("{activate}".format(activate="source $SCRIPT_DIR/bin/activate;\n".format(venv=venv)))
        fw.write("export PYTHONUSERBASE=$(echo ${VIRTUAL_ENV});\n")

    py_exe_pycharm = os.path.join(venv, "python")

    with open(py_exe_pycharm, "w") as fw:
        fw.write("#!/bin/sh\n")
        fw.write("export LD_LIBRARY_PATH={env};\n".format(env=env["LD_LIBRARY_PATH"]))
        fw.write("export PYTHONUSERBASE=$(echo ${VIRTUAL_ENV});\n")  # Todo: necessary?
        fw.write('SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd );\n')
        fw.write('$SCRIPT_DIR/bin/python "$@";\n')
        fw.write("exit 0\n")

    os.chmod(py_exe_pycharm, 0o0744)

    pycharm_exe = os.path.join(venv, "pycharm")
    pycharm_sh = "/scratch/michaelmus/Applications/pycharm-current/bin/pycharm.sh"

    with open(pycharm_exe, "w") as fw:
        fw.write("#!/bin/sh\n")
        fw.write("source {activate}\n".format(activate=activate))
        fw.write("{pycharm_sh};\n".format(pycharm_sh=pycharm_sh))
        fw.write("exit 0\n")

    os.chmod(pycharm_exe, 0o0744)

    sys.stdout.writelines(
        "Result:\n"
        "{venv}\n"
        "activate: source {activate}\n".format(
            venv=venv,
            activate=activate,
        )
    )

    return venv


def pythonpath_to_txt(pythonpath):
    with tempfile.NamedTemporaryFile(
        mode="w",
        prefix="pythonpath.txt.",
        delete=False,
    ) as fw:
        fw.write(os.pathsep.join(pythonpath))

    sys.stdout.writelines(
        "Result:\n"
        "{name}\n".format(name=fw.name)
    )

    return fw.name


if __name__ == "__main__":
    import pprint
    # pythons = list_pythons()
    # # pprint.pprint(pythons)
    #
    # python_filtered = filter_version(pythons, (3, 9), (3, 10))
    #
    # # for python in pythons:
    #
    # pprint.pprint(python_filtered)

    # python = list(filter(lambda d: d['version'] == 25, pythons))
    #
    # launch_python(python_filtered[-1])
    json_out = get_pythonpaths_from_preset(launcher_preset="/toolsets/personal/michaelmus/012_Maya_performance_production")
    # py_exe = json_out["PYTHON_EXE"]
    py_dict = get_python_from_exe("/film/tools/packages/cache/python/3.9.7.3/openssl-1.1.1/bin/python3.9")

    #######################
    with open(json_out, "r") as fr:
        data = json.load(fr)
    py_dict = get_python_from_exe(data["PYTHON_EXE"])
    python_paths = data["PYTHONPATH"]

    pythonpath_txt = pythonpath_to_txt(pythonpath=python_paths)

    create_venv(
        py_dict=py_dict,
        venv_home="/home/users/michaelmus/git/repos/AL_Sandbox/michaelmus/test_venv",
        venv_name="test5",
    )

    print pythonpath_txt

    #######################


    # launch_python(python_dict=py_dict, c="import os;print(os.environ);print(os.getcwd())")

    # create_venv(
    #     py_dict=py_dict,
    #     venv_home="/home/users/michaelmus/git/repos/AL_Sandbox/michaelmus/test_venv",
    #     venv_name="test1",
    # )

    # json_out = get_pythonpaths_from_packages(packages="python,AL_otio")
    # print json_out

    # next steps
    #
    # source /home/users/michaelmus/git/repos/AL_Sandbox/michaelmus/test_venv/test5/al_activate
    # python -m pip install --upgrade pip
    # pip install wheel wheel-filename
    # pip install six marshmallow requests future brotli numpy distro simplejson
    # pushd /home/users/michaelmus/git/repos/vnv
    # pip install -e .
    # popd
    # python /home/users/michaelmus/git/repos/vnv/src/vnv/pip_install_al.py --serial --from-file /tmp/pythonpath.txt.NbtqlL
    # pycharm: /home/users/michaelmus/git/repos/AL_Sandbox/michaelmus/test_venv/test5/pycharm

