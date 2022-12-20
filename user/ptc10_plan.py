"""this is a PTC10 plan
    reload by
    # %run -im user.ptc10_plan
"""

import logging

logger = logging.getLogger(__name__)
logger.info(__file__)

from bluesky import plan_stubs as bps
import time

from instrument.devices.ptc10_controller import ptc10  
from instrument.plans import SAXS, USAXSscan, WAXS
from instrument.plans import before_command_list, after_command_list


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






def myPTC10Loop(pos_X, pos_Y, thickness, scan_title, delaySec, md={}):
    """
    Collect USAXS/SAXS/WAXS for time delaySec
    Append to name time and temperature. 
    PTC10 control is left to manual by user. 
    To run example:
    RE(myPTC10Loop(0,0,1.28,"testExp",60*60*2))
    this will run sample in sx= 0, sy=0, thickness=1.28mm for 2 hours.
    Sample names will look similar to :  testExp_120C_25min

    reload by
    # %run -im user.ptc10_plan
    """
    
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

    yield from before_command_list()                #this will run usual startup scripts for scans

    t0 = time.time()

    logger.info("Collecting data for %s sec",delaySec)

    while time.time()-t0 < delaySec:                          # collects data for delay1 seconds
        yield from collectAllThree()

    logger.info(f"finished")

    yield from after_command_list()                  # runs standard after scan scripts.


def myPTC10Plan(pos_X, pos_Y, thickness, scan_title, temp1, rate1, delay1, temp2, rate2, md={}):
    """
    collect RT USAXS/SAXS/WAXS - or not, change code
    change temperature T to temp1 with rate1
    collect USAXS/SAXS/WAXS while heating or sleep= change code... 
    when temp1 reached, hold for delay1 seconds, collecting data repeatedly
    change T to temp2 with rate2
    collect USAXS/SAXS/WAXS while changing temp
    when temp2 reached collect final data
    and it will end here...

    reload by
    # %run -i ptc10_local
    """
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

    yield from before_command_list()                #this will run usual startup scripts for scans
    t0 = time.time()
    yield from collectAllThree()                    #collect RT data

    yield from bps.mv(ptc10.ramp, 30/60.0)           # user wants C/min, controller wants C/s
    yield from bps.mv(ptc10.temperature.setpoint, temp1)                #Change the temperature and not wait
    yield from setheaterOn()

    logger.info(f"Ramping temperature to {temp1} C")

    while not ptc10.temperature.inposition:                      #runs data collection until next temp or sleeps. Change as needed. 
        yield from bps.sleep(5)
        logger.info(f"Still Ramping temperature to {temp1} C")
        #yield from collectAllThree()

    #logger.info("Reached temperature, now collecting data for %s minutes", delay1min)
    logger.info("Reached temperature, now collecting data for %s seconds", delay1)
    t1 = time.time()

    while time.time()-t1 < delay1:                          # collects data for delay1 seconds
        #yield from bps.sleep(5)
        logger.info(f"Collecting data for %s ",delay1)
        yield from collectAllThree()

    logger.info("waited for %s seconds, now changing temperature to %s C", delay1, temp2)

    yield from bps.mv(ptc10.ramp, rate2/60.0)                  #sets the rate of next ramp
    yield from bps.mv(ptc10.temperature, temp2)                #Change the temperature and wait to get there

    logger.info(f"reached {temp2} C")
    yield from setheaterOff()
    
    yield from after_command_list()                  # runs standard after scan scripts.

    logger.info(f"finished")
