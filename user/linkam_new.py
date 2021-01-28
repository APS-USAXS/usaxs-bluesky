# this is a Linkam plan

from instrument.session_logs import logger
logger.info(__file__)


from bluesky import plan_stubs as bps
import subprocess
import time

from instrument.devices import linkam_ci94, linkam_tc1, terms
from instrument.plans import SAXS, USAXSscan, WAXS
from instrument.utils import getSampleTitle, resetSampleTitleFunction, setSampleTitleFunction

HEATER_SCRIPT = "/home/beams/USAXS/bin/heater_profile_manager.sh"
PULSE_MAX = 10000


def commandHeaterProcess(command="checkup"):
    """
    Send a command to the external heater process shell script.

    * checkup - (default) start the process if not already running
    * restart - stop (if running), then start the process
    * start - start the process
    * status - show process info if running
    * stop - stop the process
    """
    response = subprocess.run(
        f"{HEATER_SCRIPT} {command}".split(), capture_output=True
    )
    return response.stdout.decode().strip()


def myLinkamPlan(pos_X, pos_Y, thickness, scan_title, delaymin, md={}):
    """
    collect RT USAXS/SAXS/WAXS
    change temperature T to temp1 with rate1
    collect USAXS/SAXS/WAXS while Linkam is runinng on its own
    delaymin [minutes] is total time which the cycle should take.
    it will end after this time elapses...

    reload by
    # %run -m linkam
    """

    def myTitleFunction(title):
        return f"{title}_{linkam.value:.0f}C_{(time.time()-t1)/60:.0f}min"

    def collectAllThree(debug=True):
        if debug:
            #for testing purposes, set debug=True
            sampleMod = myTitleFunction(scan_title)
            print(sampleMod)
            yield from bps.sleep(20)
        else:
            yield from USAXSscan(pos_X, pos_Y, thickness, scan_title, md={})
            yield from SAXS(pos_X, pos_Y, thickness, scan_title, md={})
            yield from WAXS(pos_X, pos_Y, thickness, scan_title, md={})

    #linkam = linkam_tc1
    linkam = linkam_ci94
    logger.info(f"Linkam controller PV prefix={linkam.prefix}")

    setSampleTitleFunction(myTitleFunction)

    t1 = time.time()  # TODO: used?  (see below after trigger)
    yield from collectAllThree()

    # signal the (external) Linkam control python program to start
    logger.info("Starting external Linkam controller process ...")
    commandHeaterProcess("checkup")  # starts, if not already started
    yield from bps.sleep(1)  # wait for the process to start
    while terms.HeaterProcess.linkam_ready.get() != 1:
        yield from bps.sleep(1)  # wait until process is ready
    logger.info("External Linkam is ready ...")

    # here we need to trigger the Linkam control python program...
    logger.info("Stopping the External Linkam heating plan ...")
    # TODO: choose orderly or abrupt
    yield from bps.mv(terms.HeaterProcess.linkam_trigger, 1)  # orderly
    # commandHeaterProcess("stop")  # abrupt

    t1 = time.time()
    delay = delaymin * 60                                  # convert to seconds

    while time.time()-t1 < delay:                          # collects data for delay seconds
        yield from collectAllThree()

    logger.info("Finished after %.3f seconds", delay)

    # tell the Linkam control python program to exit...
    yield from bps.mv(terms.HeaterProcess.linkam_exit, 1)

    resetSampleTitleFunction()

    logger.info(f"finished")

