import os
import time


PYTHON = r"/usr/bin/python3.9"
BASE_DIR = os.path.join(os.path.expanduser("~"), ".vnv")
VNV_PREFIX = f"venv_from_vnv__{time.strftime('%Y-%m-%d_%H-%M-%S')}__"
