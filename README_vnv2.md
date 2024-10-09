<!-- TOC -->
* [VNV](#vnv)
* [Setup](#setup)
  * [Clone Repo](#clone-repo)
  * [Vanilla AL Shell](#vanilla-al-shell)
  * [Install `vnv2` (Python 2)](#install-vnv2-python-2)
  * [Config](#config)
  * [Guides](#guides)
    * [Get PYTHONPATHs from Launcher Preset](#get-pythonpaths-from-launcher-preset)
    * [Save PYTHONPATH to Text File](#save-pythonpath-to-text-file)
    * [Get `python_dict` from Executable or JSON File](#get-python_dict-from-executable-or-json-file)
      * [--exe](#--exe)
      * [--jsn](#--jsn)
      * [--to-file](#--to-file)
    * [Launch Python](#launch-python)
      * [Interactive Shell](#interactive-shell)
        * [From `python_dict`](#from-python_dict)
        * [From JSON File](#from-json-file)
    * [`venv`](#venv)
      * [Create `venv`](#create-venv)
        * [From `python_dict`](#from-python_dict-1)
        * [From JSON File](#from-json-file-1)
      * [Activate `venv`](#activate-venv)
      * [PIP](#pip)
        * [Upgrade PIP](#upgrade-pip)
        * [Install `vnv` (Python 3)](#install-vnv-python-3)
        * [Install AL Packages](#install-al-packages)
      * [IDE](#ide)
        * [Python Interpreter](#python-interpreter)
        * [Launch Scripts](#launch-scripts-)
          * [PyCharm](#pycharm)
          * [VsCode](#vscode)
      * [Deactivate `venv`](#deactivate-venv)
<!-- TOC -->

---

# VNV

A wrapper that is Python 2 (`vnv2`) compatible to create 
`venv`s based on AL's list of Python interpreters.

# Setup

## Clone Repo

```shell
git clone https://github.com/michimussato/vnv.git
cd vnv
git checkout al-vnv
```

## Vanilla AL Shell

```shell
which python
/usr/bin/python
```

## Install `vnv2` (Python 2)

```shell
python src/vnv/py2/vnv2.py install
```

```shell
vnv2 --help
usage: vnv2 [-h] [-v] [-vv]
            
            {install,uninstall,config,list-pythons,filter-versions,launch-python,get-pythonpaths-from-preset,get-python-dict-from-exe,pythonpath-to-txt,create-venv}
            ...

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         set loglevel to INFO
  -vv, --very-verbose   set loglevel to DEBUG

subcommands:
  sub-command help

  {install,uninstall,config,list-pythons,filter-versions,launch-python,get-pythonpaths-from-preset,get-python-dict-from-exe,pythonpath-to-txt,create-venv}
    install             Writes a symlink to `~/.local/bin`.
    uninstall           Deletes the symlink in `~/.local/bin`.
    config              Displays `vnv` config from `~/.config/vnv.json`.
    list-pythons        List all Python executables in
                        `/film/tools/packages/python` and present them as
                        `python_dict`.
    filter-versions     Search for a specific range of versions in the
                        `python_dict`s list.
    launch-python       Run a Python interpreter from a `python_dict`.
                        Optionally run a package `-m` or a command `-c`.
    get-pythonpaths-from-preset
                        Extract `PYTHONPATH` from a resolved Launcher Preset.
    get-python-dict-from-exe
                        Parse a JSON file or directly resolve a Python
                        executable path into a `python_dict`.
    pythonpath-to-txt   Parse individual `PYTHONPATH` items from a json file
                        (i.e. created by `get-pythonpaths-from-preset` into a
                        single `str` and write it to file.
    create-venv         Create a `venv` based on a `python_dict` Python
                        representation (Python 3+).
```

## Config

Config file is located at
`~/.config/vnv.json`

The file gets created when script is run.

These settings get applied and need to be modified based
on your environment:

```json
{
  "EXE_PYCHARM": "/opt/pycharm-community-2020.1.1/bin/pycharm.sh", 
  "EXE_VSCODE": "/usr/bin/code", 
  "PYTHONS_BASE": "/film/tools/packages/python"
}
```

```shell
vnv2 config
# Result:
# Config:
{
  "EXE_PYCHARM": "/opt/pycharm-community-2020.1.1/bin/pycharm.sh", 
  "EXE_VSCODE": "/usr/bin/code", 
  "PYTHONS_BASE": "/film/tools/packages/python"
}
```

## Guides

### Get PYTHONPATHs from Launcher Preset

```shell
vnv2 get-pythonpaths-from-preset -p "/toolsets/personal/michaelmus/012_Maya_performance_production"
# Result:
# cmd = ['rez', 'env', 'launcher2CL', '-c', '$LAUNCH_EXE -l shell -p /toolsets/personal/michaelmus/012_Maya_performance_production -c "python /tmp/tmpxfDIlC.py"']
# /tmp/pythonpaths.tmp3D6Ndj.json
```

### Save PYTHONPATH to Text File

```shell
vnv2 pythonpath-to-txt -p "/tmp/pythonpaths.tmp3D6Ndj.json"
# Result: 
# /tmp/pythonpath.wMXPGW.txt
```

### Get `python_dict` from Executable or JSON File

#### --exe

```shell
vnv2 get-python-dict-from-exe -e "/film/tools/packages/python/3.9.7.3/openssl-1.1.1/bin/python"
# Result: 
# {'bin': '/film/tools/packages/python/3.9.7.3/openssl-1.1.1/bin', 'version_tuple': (3, 9, 7, 3), 'exe': '/film/tools/packages/python/3.9.7.3/openssl-1.1.1/bin/python', 'lib': '/film/tools/packages/python/3.9.7.3/openssl-1.1.1/lib', 'variant': 'openssl-1.1.1', 'version': '3.9.7.3'}
```

#### --jsn

```shell
vnv2 get-python-dict-from-exe -j "/tmp/pythonpaths.tmp3D6Ndj.json"
# Result: 
# {'bin': '/film/tools/packages/python/3.9.7.3/openssl-1.1.1/bin', 'version_tuple': (3, 9, 7, 3), 'exe': '/film/tools/packages/python/3.9.7.3/openssl-1.1.1/bin/python', 'lib': '/film/tools/packages/python/3.9.7.3/openssl-1.1.1/lib', 'variant': 'openssl-1.1.1', 'version': '3.9.7.3'}
```

#### --to-file

```shell
...
# Result:
# {'bin': '/film/tools/packages/python/3.9.7.3/openssl-1.1.1/bin', 'version_tuple': (3, 9, 7, 3), 'exe': '/film/tools/packages/python/3.9.7.3/openssl-1.1.1/bin/python', 'lib': '/film/tools/packages/python/3.9.7.3/openssl-1.1.1/lib', 'variant': 'openssl-1.1.1', 'version': '3.9.7.3'}
# /tmp/tmpr5t2fv.json
```

### Launch Python

#### Interactive Shell

##### From `python_dict`

```shell
vnv2 launch-python -p "{'bin': '/film/tools/packages/python/3.9.7.3/openssl-1.1.1/bin', 'version_tuple': (3, 9, 7, 3), 'exe': '/film/tools/packages/python/3.9.7.3/openssl-1.1.1/bin/python', 'lib': '/film/tools/packages/python/3.9.7.3/openssl-1.1.1/lib', 'variant': 'openssl-1.1.1', 'version': '3.9.7.3'}"
# Python 3.9.7 (default, Aug  9 2024, 12:30:35) 
# [GCC 6.3.1 20170216 (Red Hat 6.3.1-3)] on linux
# Type "help", "copyright", "credits" or "license" for more information.
# >>>
```

##### From JSON File

```shell
vnv2 launch-python -ff "/tmp/tmpr5t2fv.json"
# Python 3.9.7 (default, Aug  9 2024, 12:30:35) 
# [GCC 6.3.1 20170216 (Red Hat 6.3.1-3)] on linux
# Type "help", "copyright", "credits" or "license" for more information.
# >>>
```

### `venv`

#### Create `venv`

Note: Set `EXE_VSCODE` and `EXE_PYCHARM` in `vnv2.py` accordingly
before executing `create-venv`.

Todo: 
- [ ] write all tmp files to the venv folder too

##### From `python_dict`

```shell
vnv2 create-venv -p "{'bin': '/film/tools/packages/python/3.9.7.3/openssl-1.1.1/bin', 'version_tuple': (3, 9, 7, 3), 'exe': '/film/tools/packages/python/3.9.7.3/openssl-1.1.1/bin/python', 'lib': '/film/tools/packages/python/3.9.7.3/openssl-1.1.1/lib', 'variant': 'openssl-1.1.1', 'version': '3.9.7.3'}" -vh "~/venvs" -vn "my-new-virtualenv"
# Result:
# venv = ~/venvs/my-new-virtualenv
# python = ~/venvs/my-new-virtualenv/python
# vscode = ~/venvs/my-new-virtualenv/vscode
# pycharm = ~/venvs/my-new-virtualenv/pycharm
# activate: source ~/venvs/my-new-virtualenv/al_activate
```

##### From JSON File

```shell
vnv2 create-venv -ff "/tmp/tmpr5t2fv.json" -vh "~/venvs" -vn "my-new-virtualenv"
# Result:
# venv = ~/venvs/my-new-virtualenv
# python = ~/venvs/my-new-virtualenv/python
# vscode = ~/venvs/my-new-virtualenv/vscode
# pycharm = ~/venvs/my-new-virtualenv/pycharm
# activate: source ~/my-new-virtualenv/al_activate
```

#### Activate `venv`

```shell
source ~/venvs/my-new-virtualenv/al_activate
# Result: 
# (my-new-virtualenv) michaelmus@sy1wse0076:vnv (al-vnv)$
```

#### PIP

##### Upgrade PIP

```shell
python -m pip install --upgrade pip
pip install wheel wheel-filename
pip install six marshmallow requests future brotli numpy distro simplejson
```

##### Install `vnv` (Python 3)

```shell
pushd $(dirname $(dirname $(dirname $(dirname $(readlink $(which vnv2))))))
pip install -e .
popd
```

##### Install AL Packages

```shell
python src/vnv/pip_install_al.py --serial --from-file "/tmp/pythonpath.wMXPGW.txt"
```

#### IDE

##### Python Interpreter

Specify this interpreter as default interpreter
in your IDE:

`~/venvs/my-new-virtualenv/python`

##### Launch Scripts 

###### PyCharm

`~/venvs/my-new-virtualenv/pycharm`

###### VsCode

`~/venvs/my-new-virtualenv/vscode`

#### Deactivate `venv`

```shell
deactivate
```
