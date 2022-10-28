
"""
Install a NeXus file writer for uascan raw data files

See ``instrument.utils.setup_new_user.newFile()``
to replace ``instrument.framework.callbacks.newSpecFile()``
"""

__all__ = [
    "nxwriter",
    ]

import logging

logger = logging.getLogger(__name__)
import logging

logger = logging.getLogger(__name__)
logger.info(__file__)

from .nxwriter_usaxs import NXWriterUascan
from ..framework import RE, callback_db

nxwriter = NXWriterUascan()
callback_db['nxwriter'] = RE.subscribe(nxwriter.receiver)
