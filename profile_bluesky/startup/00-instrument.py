"""
start bluesky in IPython session for 9-ID-C USAXS
"""


import pathlib, sys

path = pathlib.Path.home() / ".ipython" / "profile_bluesky" / "startup"
if str(path) not in sys.path:
    sys.path.append(str(path))

# terse exception tracebacks
get_ipython().run_line_magic('xmode', 'Minimal')

from instrument.collection import *
