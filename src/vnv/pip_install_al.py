#!/usr/bin/env python
import contextlib
import os
import argparse
import shutil
import multiprocessing as mp
import subprocess
import tempfile
try:
    from wheel_filename import parse_wheel_filename, InvalidFilenameError
except ModuleNotFoundError as e:
    raise ModuleNotFoundError("Fix error with `pip install wheel-filename`") from e


DRY_RUN = False
FORCE_REINSTALL = True
PIP_USER = False
DO_OPERATION = [os.symlink, shutil.copyfile][1]  # [1]: Way faster and less multiprocessing errors :)
DO_CLEANUP = True
RND_PKGS = os.getenv("RND_PACKAGES", "")
# sys.executable resolves to something like /film/tools/packages/cache/python/3.9.7.3/openssl-1.1.1/bin/python,
# which is not what we want
#
# shutil.which("python") resolves to something like /home/users/~/venvs/tests/new_venv2/bin/python
PY = shutil.which("python")


def install_whl(queue, package, lives_in, force_reinstall):
    cmd = [
        PY,
        "-m",
        "pip",
        "install",
        "--extra-index-url",
        "https://pypi.org/api/pypi/pypi/simple",  # default (-i/--index-url Base URL) points to https://artifactx:443/artifactory/api/pypi/pypi/simple
        "--find-links",
        lives_in,
        package,
    ]
    if force_reinstall:
        cmd.insert(4, "--force-reinstall")
    if PIP_USER:
        cmd.append("--user")
    if DRY_RUN:
        cmd.append("--dry-run")
    try:
        queue.put(
            subprocess.check_call(
                args=cmd,
                cwd=lives_in,
            )
        )
    except Exception as e:
        print(e)
        print(" ".join(cmd))


def convert_egg(queue, package, lives_in, tmp_dir_egg2whl):
    # In theory (https://stackoverflow.com/a/21856049), `.egg`s can
    # be converted using wheel.whl on the fly without installing `wheel`
    # into the `venv` first. I was not successful with this yet -
    # So, the current implementation requires `wheel` to be installed (pip install wheel).
    #
    # wheel = "resources/wheel-0.44.0-py3-none-any.whl"
    cmd = [
        PY,
        "-m",
        "wheel",
        "convert",
        "--dest-dir",
        tmp_dir_egg2whl,
        os.path.join(lives_in, package)
    ]
    queue.put(
        subprocess.check_call(
            args=cmd,
            cwd=lives_in,
        )
    )


def install_into_venv(args):
    from_file = args.from_file
    serial = args.serial
    force_reinstall = args.force_reinstall

    convert_eggs = []
    install_whls = []
    install_whls_from_eggs = []

    user = os.path.expanduser("~")

    global python_paths

    if from_file is None:
        try:
            _python_paths = os.getenv("PYTHONPATH")
        except Exception as e:
            raise e
    else:
        if os.path.isfile(from_file):
            with open(from_file, "r") as fr:
                _python_paths = fr.read().rstrip()
        else:
            raise FileNotFoundError(f"File {from_file} not found.")

    try:
        python_paths = _python_paths.split(os.pathsep)
    except AttributeError as e:
        raise AttributeError(f"PYTHONPATH has no content. Can't split().") from e

    print(_python_paths)

    with (
        tempfile.TemporaryDirectory(dir=f"{user}/temp", prefix="pip_")
        if DO_CLEANUP
        else contextlib.nullcontext(tempfile.mkdtemp(dir=f"{user}/temp", prefix="pip_"))
    ) as tmp_dir:

    # if True:
    # with tempfile.TemporaryDirectory(dir=f"{user}/temp", prefix="pip_") as tmp_dir:
    #     tmp_dir = tempfile.mkdtemp(dir=f"{user}/temp", prefix="pip_")
        tmp_dir_egg2whl = tempfile.mkdtemp(dir=f"{tmp_dir}", prefix="egg2whl_")

        for i, path in enumerate(list(python_paths)):

            if not path.startswith("/film/tools/packages/") and not path.startswith(RND_PKGS):
                # Todo:
                #  done?
                #  Will skip packages from
                #  - /depts/rnd/dev/michaelmus/packages
                print(f"Ignored: {path}")
                continue

            if path.endswith((".egg", ".whl")) and os.path.isfile(path):
                # os.link(): cross device link error (naturally)
                _basename = os.path.basename(path)
                ext = os.path.splitext(_basename)[1]
                new_name = None
                if ext == ".egg":
                    print(f"egg: {_basename}")
                    DO_OPERATION(path, os.path.join(tmp_dir, new_name or _basename))
                    convert_eggs.append(new_name or _basename)
                elif ext == ".whl":
                    print(f"whl: {_basename}")
                    try:
                        parse_wheel_filename(_basename)
                    except InvalidFilenameError as e:
                        # most of our `.whl`s are not following
                        # the commonly agreed upon naming
                        # convention. `parse_wheel_filename()`
                        # raises an `InvalidFilenameError` in such
                        # a case. We then make sure that at least
                        # the name of the symlink to the malformatted
                        # name to our `.whl` does align with
                        # best practice.
                        split = _basename.split("-")
                        split.insert(2, "py3")
                        new_name = "-".join(split)
                        parse_wheel_filename(new_name)

                    DO_OPERATION(path, os.path.join(tmp_dir, new_name or _basename))
                    install_whls.append(new_name or _basename)

            # Todo: Not sure yet if we need this
            #         # Fix AL.libs namespace
            #         for p in ("AL/libs/__init__.py", "AL/__init__.py"):
            #             init = os.path.join(targetPath, p)
            #             if os.path.exists(init):
            #                 print("Patching: {init}".format(init=init))
            #                 with open(init, "w") as fo:
            #                     fo.write("__import__(\"pkg_resources\").declare_namespace(__name__)")
            #
            # setenv("PYTHONPATH", os.pathsep.join(python_paths))

        queue_1 = mp.Queue()
        # queue_2 = mp.Queue()
        queue_3 = mp.Queue()
        queue_4 = mp.Queue()
        # processes_convert = []
        # processes = []

        ############################
        # eggs don't work in venv
        # make sure this step completes 100% before continue
        print('STAGE 1')
        processes_1 = [
            mp.Process(
                target=convert_egg,
                args=(queue_1, egg, tmp_dir, tmp_dir_egg2whl)
            ) for egg in convert_eggs
        ]
        for process_1 in processes_1:
            process_1.start()
            if serial:
                process_1.join()
        if not serial:
            for process_1 in processes_1:
                process_1.join()
        queue_1.close()
        ############################

        ############################
        # append converted whl's (from egg's)
        print('STAGE 2')
        for whl in os.listdir(tmp_dir_egg2whl):
            install_whls_from_eggs.append(whl)
        ############################

        ############################
        # install whl's
        print('STAGE 3')
        processes_3 = [
            mp.Process(
                target=install_whl,
                args=(queue_3, whl, tmp_dir, force_reinstall)
            ) for whl in install_whls
        ]
        for process_3 in processes_3:
            process_3.start()
            if serial:
                process_3.join()
        if not serial:
            for process_3 in processes_3:
                process_3.join()
        queue_3.close()
        ############################

        ############################
        # install converted whl's (from egg's)
        print('STAGE 4')
        # Todo: don't know if this is "a real" issue
        #  Getting some problems at this stage:
        #  Traceback (most recent call last):
        #    File "/film/tools/packages/cache/python/3.9.7.3/openssl-1.1.1/lib/python3.9/multiprocessing/process.py", line 315, in _bootstrap
        #      self.run()
        #    File "/film/tools/packages/cache/python/3.9.7.3/openssl-1.1.1/lib/python3.9/multiprocessing/process.py", line 108, in run
        #      self._target(*self._args, **self._kwargs)
        #    File "/home/users/michaelmus/git/repos/AL_Sandbox/michaelmus/pip-install-al/pip_install_al.py", line 56, in install_whl
        #      subprocess.check_call(
        #    File "/film/tools/packages/cache/python/3.9.7.3/openssl-1.1.1/lib/python3.9/subprocess.py", line 373, in check_call
        #      raise CalledProcessError(retcode, cmd)
        #  subprocess.CalledProcessError: Command '['/film/tools/packages/cache/python/3.9.7.3/openssl-1.1.1/bin/python', '-m', 'pip', 'install', '--extra-index-url', 'https://pypi.org/api/pypi/pypi/simple', '--find-links', '/home/users/michaelmus/temp/pip_spuu9be1/egg2whl_5n49yibc', 'AL_pylib_shotrange-1.7.2-py39-none-any.whl']' returned non-zero exit status 1.
        #  ERROR: Could not install packages due to an OSError: [Errno 2] No such file or directory: '/home/users/michaelmus/venvs/tests/new_venv2/lib/python3.9/site-packages/AL/__init__.py'

        processes_4 = [
            mp.Process(
                target=install_whl,
                args=(queue_4, whl, tmp_dir_egg2whl, force_reinstall)
            ) for whl in install_whls_from_eggs
        ]
        for process_4 in processes_4:
            process_4.start()
            if serial:
                process_4.join()
        if not serial:
            for process_4 in processes_4:
                process_4.join()
        queue_4.close()
        # ############################


# def main(from_file=None):
def main(args):
    install_into_venv(args)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--from-file",
        type=str,
        dest="from_file",
        default=None,
        required=False,
        help="Specify a file with PYTHONPATH content, "
             "i.e. `echo ${PYTHONPATH} > pythonpath.txt`."
    )

    parser.add_argument(
        "--serial",
        action="store_true",
        dest="serial",
        default=False,
        required=False,
        help="No multiprocessing (only affects "
             "installation of `egg`s)."
    )

    parser.add_argument(
        "--force-reinstall",
        action="store_true",
        dest="force_reinstall",
        default=False,
        required=False,
        help="equal to `pip install --force-reinstall`."
    )

    args = parser.parse_args()

    main(
        args=args,
    )
