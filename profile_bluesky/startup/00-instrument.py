"""
start bluesky in IPython session for 9-ID-C USAXS
"""


import os, pathlib, sys

path = os.path.abspath(
    os.path.join(pathlib.Path.home(), ".ipython", "profile_bluesky", "startup")
)
if path not in sys.path:
    sys.path.append(path)

from instrument.collection import *
