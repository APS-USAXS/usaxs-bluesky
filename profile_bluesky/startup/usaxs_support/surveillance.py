"""
basic surveillance and logging of users' measurement code

A function to be called from users' custom code that
will archive that code for posterity. Similar to how the SPEC macros are recorded.

* Must be simple for user to call: yield from some_name()
* Must provide some value to user (or else they will not use it).
* Must copy user's code into posterity archive.

EXAMPLE::

    def myPlan(t_start, t_end, t_steps):
        text = f"measure from {t_start} to {t_end} in {t_steps} steps"
        usaxs_support.surveillance.make_archive(text)   # <---- ADD HERE

        t = t_start
        while t < t_end:
            yield from linkam.set_temperature(t)
            yield from bp.scan([detector], motor, 10, 20, 120)
            t += t_step

"""

from collections import OrderedDict
import datetime
import inspect
import logging
import os

logger = logging.getLogger(os.path.split(__file__)[-1])


def _write_archive_dict_(archive_dict):
    """
    writes dictionary contents to USAXS archive file as text, returns revised dict
    """
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    archive_path = "/share1/log/macros"
    archive_file = os.path.join(archive_path, f"{ts}-usaxs.txt")
    archive_dict["archive_file"] = archive_file
    archive_dict["archive_timestamp"] = ts

    with open(archive_file, "w") as fp:
        for k, v in archive_dict.items():
            fp.write(f"# {k}:\n")
            if k == "source_contents":
                fp.write("-"*20 + " source " + "-"*20 + "\n")
                fp.writelines(v)
                fp.write("-"*20 + " source " + "-"*20 + "\n")
            else:
                fp.write(f"{v}\n")
            fp.write("\n")
        logger.debug(f"Archive: {archive_file}")
    return archive_dict


def _create_archive_dict_(frame, text):
    """creates an archive dictionary from a stack frame (from usaxs_support)"""
    archive = OrderedDict()
    archive["text"] = text
    archive["source"] = frame.filename
    archive["is_file"] = not frame.filename.startswith('<')
    archive["line"] = frame.lineno
    archive["caller"] = frame.function
    archive["caller_code"] = ''.join(frame.code_context)
    if archive["is_file"]:
        if os.path.exists(frame.filename):
            with open(frame.filename, "r") as fp:
                archive["source_contents"] = fp.readlines()
            logger.debug(f"source code file: {frame.filename}")
        else:
            logger.debug(f"FileNotFound: {frame.filename}")
            archive["source_contents"] = "source not found"
    return archive


def make_archive(text=None):
    """
    copies caller function (and its source file) to permanent archive, returns dict

    Any text supplied by the caller will be written at the start of the archive.
    """
    frameinfo = inspect.getouterframes(inspect.currentframe(), 2)
    logger.debug(f"make_archive() called from: {frameinfo[1].filename}")
    archive = _create_archive_dict_(frameinfo[1], text or "")
    return _write_archive_dict_(archive)


def looky():
    text = """
    archive custom user code #228
    https://github.com/APS-USAXS/ipython-usaxs/issues/228

    This is just a demonstration.
    """
    print(make_archive(text))


if __name__ == "__main__":
    looky()