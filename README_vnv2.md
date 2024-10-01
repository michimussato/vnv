<!-- TOC -->
* [Setup](#setup)
  * [Clone Repo](#clone-repo)
  * [Vanilla AL Shell](#vanilla-al-shell)
  * [Install `vnv2` (Python 2)](#install-vnv2-python-2)
  * [Guides](#guides)
    * [Get PYTHONPATHs from Launcher Preset](#get-pythonpaths-from-launcher-preset)
    * [Save PYTHONPATH to Text File](#save-pythonpath-to-text-file)
    * [Get `python_dict` from Executable or JSON File](#get-python_dict-from-executable-or-json-file)
    * [Launch Python](#launch-python)
      * [Interactive Shell](#interactive-shell)
    * [`venv`](#venv)
      * [Create `venv`](#create-venv)
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

A wrapper that is Python 2 compatible to create 
`venv`s based on AL's list of Python interpreters.

# Setup

## Clone Repo

```
git clone https://github.com/michimussato/vnv.git
cd vnv
git checkout al-vnv
```

## Vanilla AL Shell

```
$ which python
/usr/bin/python
```

## Install `vnv2` (Python 2)

```
python src/vnv/py2/vnv2.py install
```

```
vnv2 --help
usage: vnv2.py [-h] [-v] [-vv]
               
               {install,uninstall,list-pythons,filter-versions,launch-python,get-pythonpaths-from-preset,get-python-dict-from-exe,pythonpath-to-txt,create-venv}
               ...

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         set loglevel to INFO
  -vv, --very-verbose   set loglevel to DEBUG

subcommands:
  sub-command help

  {install,uninstall,list-pythons,filter-versions,launch-python,get-pythonpaths-from-preset,get-python-dict-from-exe,pythonpath-to-txt,create-venv}
    install             Writes a symlink to `~/.local/bin`.
    uninstall           Deletes the symlink in `~/.local/bin`.
    list-pythons        List all Python executables in
                        `/film/tools/packages/python` and present them as
                        `python_dict`.
    filter-versions     Search for a specif range of versions in the
                        `python_dict`s list.
    launch-python       Run a Python interpreter from a `python_dict`.
                        Optionally run a package `-m` or a command `-c`.
    get-pythonpaths-from-preset
                        Extract `PYTHONPATH` from a resolved Launcher Preset.
    get-python-dict-from-exe
                        Resolve a Python executable path into a `python_dict`.
    pythonpath-to-txt   Parse individual `PYTHONPATH` items from a json file
                        (i.e. created by `get-pythonpaths-from-preset` into a
                        single `str` and write it to file.
    create-venv         Create a `venv` based on a `python_dict` Python
                        representation (Python 3+).
```

## Guides

### Get PYTHONPATHs from Launcher Preset

```
vnv2 get-pythonpaths-from-preset -p "/toolsets/personal/michaelmus/012_Maya_performance_production"
# Result: /tmp/pythonpaths.tmp3D6Ndj.json
```

### Save PYTHONPATH to Text File

```
vnv2 pythonpath-to-txt -p /tmp/pythonpaths.tmp3D6Ndj.json
# Result: /tmp/pythonpath.wMXPGW.txt
```

### Get `python_dict` from Executable or JSON File

```
vnv2 get-python-dict-from-exe -j "/tmp/pythonpaths.tmp3D6Ndj.json"
# Result: {'bin': '/film/tools/packages/python/3.9.7.3/openssl-1.1.1/bin', 'version_tuple': (3, 9, 7, 3), 'exe': '/film/tools/packages/python/3.9.7.3/openssl-1.1.1/bin/python', 'lib': '/film/tools/packages/python/3.9.7.3/openssl-1.1.1/lib', 'variant': 'openssl-1.1.1', 'version': '3.9.7.3'}
```

### Launch Python

#### Interactive Shell

```
vnv2 launch-python -p "{'bin': '/film/tools/packages/python/3.9.7.3/openssl-1.1.1/bin', 'version_tuple': (3, 9, 7, 3), 'exe': '/film/tools/packages/python/3.9.7.3/openssl-1.1.1/bin/python', 'lib': '/film/tools/packages/python/3.9.7.3/openssl-1.1.1/lib', 'variant': 'openssl-1.1.1', 'version': '3.9.7.3'}"
# Result
# Python 3.9.7 (default, Aug  9 2024, 12:30:35) 
# [GCC 6.3.1 20170216 (Red Hat 6.3.1-3)] on linux
# Type "help", "copyright", "credits" or "license" for more information.
# >>>
```

### `venv`

#### Create `venv`

```
vnv2 create-venv -p "{'bin': '/film/tools/packages/python/3.9.7.3/openssl-1.1.1/bin', 'version_tuple': (3, 9, 7, 3), 'exe': '/film/tools/packages/python/3.9.7.3/openssl-1.1.1/bin/python', 'lib': '/film/tools/packages/python/3.9.7.3/openssl-1.1.1/lib', 'variant': 'openssl-1.1.1', 'version': '3.9.7.3'}" -vh "/home/users/michaelmus/venvs" -vn "my-new-virtualenv"
# Result:
# /home/users/michaelmus/venvs/my-new-virtualenv
# activate: source /home/users/michaelmus/venvs/my-new-virtualenv/al_activate
```

#### Activate `venv`

```
source /home/users/michaelmus/venvs/my-new-virtualenv/al_activate
# Result: (my-new-virtualenv) michaelmus@sy1wse0076:~/test/vnv (al-vnv)$
```

#### PIP

##### Upgrade PIP

```
python -m pip install --upgrade pip
pip install wheel wheel-filename
pip install six marshmallow requests future brotli numpy distro simplejson
```

##### Install `vnv` (Python 3)

```
pushd $(dirname $(dirname $(dirname $(dirname $(readlink $(which vnv2))))))
pip install -e .
popd
```

##### Install AL Packages

```
python src/vnv/pip_install_al.py --serial --from-file /tmp/pythonpath.wMXPGW.txt
```

#### IDE

##### Python Interpreter

Specify this interpreter as default interpreter
in your IDE:

```
/home/users/michaelmus/venvs/my-new-virtualenv/python
```

##### Launch Scripts 

###### PyCharm

```
/home/users/michaelmus/venvs/my-new-virtualenv/pycharm
```

###### VsCode

```
/home/users/michaelmus/venvs/my-new-virtualenv/vscode
```

#### Deactivate `venv`

```
deactivate
```

