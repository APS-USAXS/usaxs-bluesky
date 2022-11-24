"""
BS plan to run infinte data collection same as spec used to do.

load this way:

     %run -im user.finite_loop

* file: /USAXS_data/bluesky_plans/finite_loop.py
* aka:  ~/.ipython/user/finite_loop.py

* JIL, 2022-11-17 : first release
"""

import logging

logger = logging.getLogger(__name__)
logger.info(__file__)

from bluesky import plan_stubs as bps
from instrument.plans import before_command_list, after_command_list
from instrument.plans import SAXS, USAXSscan, WAXS, preUSAXStune
from ophyd import Signal
import time

#define conversions from seconds
SECOND = 1
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR
WEEK = 7 * DAY

#debug mode switch, may not be that useful in our case...
loop_debug = Signal(name="loop_debug", value=False)
#   In order to run as debug (without collecting data, only run through loop) in command line run:
#loop_debug.put(True)

def myFiniteLoop(pos_X, pos_Y, thickness, scan_title, delay1minutes, md={}):
    """
    Will run finite loop 
    delay1minutes - delay is in minutes

    reload by
    # %run -im user.finite_loop
    """

    def setSampleName():
        return (
            f"{scan_title}"
            f"_{(time.time()-t0)/60:.0f}min"
        )

    def collectAllThree(debug=False):
        sampleMod = setSampleName()
        if debug:
            #for testing purposes, set debug=True
            print(sampleMod)
            yield from bps.sleep(20)
        else:
            md["title"]=sampleMod
            yield from USAXSscan(pos_X, pos_Y, thickness, sampleMod, md={})
            sampleMod = setSampleName()
            md["title"]=sampleMod
            yield from SAXS(pos_X, pos_Y, thickness, sampleMod, md={})
            sampleMod = setSampleName()
            md["title"]=sampleMod
            yield from WAXS(pos_X, pos_Y, thickness, sampleMod, md={})

    isDebugMode = loop_debug.get()
    #isDebugMode = False

    if isDebugMode is not True:
        yield from before_command_list()                #this will run usual startup scripts for scans

    t0 = time.time()                                    # mark start time of data collection.
 
    checkpoint = time.time() + delay1minutes*MINUTE             # time to end ``delay1min`` hold period

    logger.info("Collecting data for %s minutes", delay1minutes)

    while time.time() < checkpoint:                         # collects USAXS/SAXS/WAXS data while holding at temp1
        yield from collectAllThree(isDebugMode)

    logger.info("finished")                            #record end.

    if isDebugMode is not True:
       yield from after_command_list()                  # runs standard after scan scripts.
