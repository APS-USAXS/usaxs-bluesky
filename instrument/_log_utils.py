"""
_log_utils.py

Pending apstools 1.6.9 release
"""

# TODO: pending apstools 1.6.9 release
# from apstools.utils import file_log_handler
# from apstools.utils import get_log_path
# from apstools.utils import setup_console_logging
# from apstools.utils import stream_log_handler
import logging
import pathlib


def get_log_path():
    path = pathlib.Path().cwd() / ".logs"
    if not path.exists():
        path.mkdir()
    return path


def setup_console_logging(logger):
    console_io_file = get_log_path() / "ipython_console.log"
    try:
        # start logging console to file
        # https://ipython.org/ipython-doc/3/interactive/magics.html#magic-logstart
        _ipython = get_ipython()
        if _ipython is not None:
            _ipython.magic(f"logstart -o -t {console_io_file} rotate")
        logger.info("Console logging: %s", console_io_file)
    except Exception:
        logger.exception("Could not setup console logging.")


def stream_log_handler():
    handler = logging.StreamHandler()

    # nice output format
    # https://docs.python.org/3/library/logging.html#logrecord-attributes
    formatter = logging.Formatter(
        (
            "%(levelname)-.1s"		# only first letter
            " %(asctime)s"
            " - "
            "%(message)s"
        ),
        datefmt="%a-%H:%M:%S"
    )
    formatter.default_msec_format = "%s.%03d"
    handler.setFormatter(formatter)
    handler.setLevel("INFO")

    return handler


def file_log_handler(
    logger_name, 
    file_name_base=None,
    maxBytes=0,
    backupCount=0,
    log_path=None,
    level=None,
):
    """
    standard setup for logging
        
    PARAMETERS
    
    logger_name : str
        name of the the logger
    
    file_name_base : str
        Part of the name to store the log file.
        Full name is `f"<log_path>/{file_name_base}.log"`
        in present working directory.
    
    log_path : str
        Part of the name to store the log file.
        Full name is `f"<log_path>/{file_name_base}.log"`
        in present working directory.
        default: (the present working directory)/LOG_DIR_BASE
    
    level : int
        Threshold for reporting messages with this logger.
        Logging messages which are less severe than *level* will be ignored.
        default: 10 (logging.DEBUG)
        see: https://docs.python.org/3/library/logging.html#levels
    
    maxBytes : (optional) int
        Log file *rollover* begins whenever the current 
        log file is nearly *maxBytes* in length.
        default: 0
    
    backupCount : (optional) int
        When *backupCount* is non-zero, the system will keep
        up to *backupCount* numbered log files (with added extensions
        `.1`, '.2`, ...).  The current log file always has no
        numbered extension.  The previous log file is the 
        one with the lowest extension number.
        default: 0
    
    **Note**:  When either *maxBytes* or *backupCount* are zero,
    log file rollover never occurs, so you generally want to set 
    *backupCount* to at least 1, and have a non-zero *maxBytes*.
    """
    file_name_base = file_name_base or logger_name
    log_path = log_path or get_log_path()
    log_file = log_path / f"{file_name_base}.log"
    level = level or logging.DEBUG

    if maxBytes > 0 or backupCount > 0:
        handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=maxBytes, backupCount=backupCount)
    else:
        handler = logging.FileHandler(log_file)

    handler.setLevel(level)

    formatter = logging.Formatter(
        (
            "|%(asctime)s"
            "|%(levelname)s"
            "|%(process)d"
            "|%(name)s"
            "|%(module)s"
            "|%(lineno)d"
            "|%(threadName)s"
            "| - "
            "%(message)s"
        )
    )
    formatter.default_msec_format = "%s.%03d"
    handler.setFormatter(formatter)

    return handler
