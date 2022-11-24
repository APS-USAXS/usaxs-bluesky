"""this is a PTC10 plan
    reload by
    # %run -im ptc10_plan
"""

import logging

logger = logging.getLogger(__name__)
logger.info(__file__)

from bluesky import plan_stubs as bps
import time

from instrument.devices.ptc10_controller import ptc10  
from instrument.plans import SAXS, USAXSscan, WAXS


# utility functions to use in heater

def setheaterOff():
    """
    switches heater off
    """
    yield from bps.mv(
        ptc10.enable, "Off",                            #power down
        ptc10.pid.pidmode, "Off"                        #Stop pid loop also
    )

def setheaterOn():
    """
    switches heater on
    """
    yield from bps.mv(
        ptc10.enable, "On",                            #power up
        ptc10.pid.pidmode, "On"                        #Start pid loop also
    )


def getSampleName():
    """
    return the name of the sample
    """
    return f"{scan_title}_{ptc10.position:.0f}C_{(time.time()-t0)/60:.0f}min"


def collectAllThree(debug=False):
    """
    documentation here
    """
    sampleMod = getSampleName()
    if debug:
        #for testing purposes, set debug=True
        print(sampleMod)
        yield from bps.sleep(20)
    else:
        md["title"]=sampleMod
        yield from USAXSscan(pos_X, pos_Y, thickness, sampleMod, md={})
        sampleMod = getSampleName()
        md["title"]=sampleMod
        yield from SAXS(pos_X, pos_Y, thickness, sampleMod, md={})
        sampleMod = getSampleName()
        md["title"]=sampleMod
        yield from WAXS(pos_X, pos_Y, thickness, sampleMod, md={})


def myPTC10Plan(pos_X, pos_Y, thickness, scan_title, temp1, rate1, delay1, temp2, rate2, md={}):
    """
    collect RT USAXS/SAXS/WAXS
    change temperature T to temp1 with rate1
    collect USAXS/SAXS/WAXS while heating
    when temp1 reached, hold for delay1 seconds, collecting data repeatedly
    change T to temp2 with rate2
    collect USAXS/SAXS/WAXS while changing temp
    when temp2 reached collect final data
    and it will end here...

    reload by
    # %run -i ptc10_local
    """

    temp1 = 50
    temp2 = 30
    delay1 = 20
    t0 = time.time()
    #yield from collectAllThree()                    #collect RT data

    yield from bps.mv(ptc10.ramp, 30/60.0)           # user wants C/min, controller wants C/s
    yield from bps.mv(ptc10.temperature.setpoint, temp1)                #Change the temperature and not wait
    yield from setheaterOn()

    logger.info(f"Ramping temperature to {temp1} C")

    while not ptc10.temperature.inposition:                      #runs data collection until next temp
        yield from bps.sleep(5)
        logger.info(f"Still Ramping temperature to {temp1} C")
        #yield from collectAllThree()

    logger.info(f"Reached temperature, now collecting data for {delay1} seconds")
    t1 = time.time()

    while time.time()-t1 < delay1:                          # collects data for delay1 seconds
        yield from bps.sleep(5)
        logger.info(f"Collecting data for {delay1} ")
        #yield from collectAllThree()

    logger.info(f"waited for {delay1} seconds, now changing temperature to {temp2} C")

    yield from bps.mv(ptc10.ramp, 20/60.0)       #sets the rate of next ramp
    yield from bps.mv(ptc10.temperature, temp2)                      #Change the temperature and wait to get there

    logger.info(f"reached {temp2} C")
    yield from setheaterOff()
    
    #yield from collectAllThree()

    logger.info(f"finished")
