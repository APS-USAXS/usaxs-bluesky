
"""
configure for data collection in a console session
"""

# kickoff session logging
from .session_logs import logger
logger.info(__file__)

from . import mpl

# conda environment name
import os
_conda_prefix = os.environ.get("CONDA_PREFIX")
if _conda_prefix is not None:
    logger.info("CONDA_PREFIX = %s", _conda_prefix)
del _conda_prefix

logger.info("bluesky framework")
from .framework import *
from .devices import *
from .callbacks import *
from .plans import *
from .utils import *

from apstools.utils import *

from .plans.move_instrument import *
from .utils.setup_new_user import *
# ensure nothing clobbered our logger
from .session_logs import logger

logger.info("bluesky startup is complete")
