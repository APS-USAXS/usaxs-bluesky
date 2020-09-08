
"""
custom callbacks
"""

__all__ = [
    'specwriter',
    'spec_comment',
    'newSpecFile',
]

from ..session_logs import logger
logger.info(__file__)

import apstools.filewriters
import apstools.utils
import datetime
import os

from .initialize import RE, callback_db
from ..utils.check_file_exists import filename_exists

# write scans to SPEC data file
specwriter = apstools.filewriters.SpecWriterCallback()
#_path = "/tmp"      # make the SPEC file in /tmp (assumes OS is Linux)
_path = os.getcwd() # make the SPEC file in current working directory (assumes is writable)
specwriter.newfile(os.path.join(_path, specwriter.spec_filename))
callback_db['specwriter'] = RE.subscribe(specwriter.receiver)

logger.info(f"writing to SPEC file: {specwriter.spec_filename}")
logger.info("   >>>>   Using default SPEC file name   <<<<")
logger.info("   file will be created when bluesky ends its next scan")
logger.info(f"   to change SPEC file, use command:   newSpecFile('title')")


def spec_comment(comment, doc=None):
    # supply our specwriter to the standard routine
    apstools.filewriters.spec_comment(comment, doc, specwriter)


def newSpecFile(title, scan_id=1):
    """
    user choice of the SPEC file name
    
    cleans up title, prepends month and day and appends file extension
    """
    raise RuntimeError("DEPRECATED: use ``newFile()``")
    # global specwriter
    # dt = datetime.datetime.now()
    # clean = apstools.utils.cleanupText(title)
    # fname = f"{dt.month:02d}_{dt.day:02d}_{clean}.dat"
    # if filename_exists(fname):
    #     logger.warning(">>> file already exists: %s <<<", fname)
    #     specwriter.newfile(fname, RE=RE)
    #     handled = "appended"
        
    # else:
    #     specwriter.newfile(fname, scan_id=scan_id, RE=RE)
    #     handled = "created"

    # logger.info(f"SPEC file name : {specwriter.spec_filename}")
    # logger.info(f"File will be {handled} at end of next bluesky scan.")
