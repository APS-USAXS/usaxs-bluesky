# this is a Linkam plan using BS to control Linkam temeprature in sync with data collection
# JIL, 2021-11-12, modified to use updated before_command_list(), verify operations
# 

from instrument.session_logs import logger
logger.info(__file__)


from bluesky import plan_stubs as bps
import time

from instrument.devices import linkam_ci94, linkam_tc1
from instrument.plans import SAXS, USAXSscan, WAXS
from instrument.plans import before_command_list, after_command_list 
from ophyd import Signal

linkam_debug = Signal(name="linkam_debug",value=False)
#   In order to run as debug (without collecting data, only control Linkam) in command line run:
#linkam_debug.put(True)

def myLinkamPlan(pos_X, pos_Y, thickness, scan_title, temp1, rate1, delay1min, temp2, rate2, md={}):
    """
    *** Check code in /USAXS_data/Bluesky_plans/linam.py is using tc1, edit and reload if necessary ***
    1. collect 40C (~RT) USAXS/SAXS/WAXS
    2. change temperature T to temp1 with rate1, collect USAXS/SAXS/WAXS while heating
    3. when temp1 reached, hold for delay1min minutes, collecting data repeatedly
    4. change T to temp2 with rate2, collect USAXS/SAXS/WAXS while heating/cooling
    5. when temp2 reached, collect final data
    and it will end here...
    Temp is in C, delay is in minutes

    reload by
    # %run -m linkam
    """

    def setSampleName():
        return f"{scan_title}_{linkam.value:.0f}C_{(time.time()-t0)/60:.0f}min"

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

    linkam = linkam_tc1     #New Linkam from windows ioc (all except NIST 1500). 
    #linkam = linkam_ci94   #this is old TS1500 NIST from LAX
    logger.info(f"Linkam controller PV prefix={linkam.prefix}")
    isDebugMode = linkam_debug.get()
    
    if isDebugMode is not True:
        yield from before_command_list()                #this will run usual startup scripts for scans
    
    # Collect data at 40C as Room temperature data. 
    yield from bps.mv(linkam.rate, 200)                 #sets the rate of next ramp
    yield from linkam.set_target(40, wait=True)         #sets the temp of to 40C, waits until we get there (no data collection)
    t0 = time.time()                                    #reset time to 0 for data collection. 
    yield from collectAllThree(isDebugMode)

    #Heating cycle 1 - ramp up and hold 
    yield from bps.mv(linkam.rate, rate1)               #sets the rate of next ramp to rate1 (deg C/min)
    yield from linkam.set_target(temp1, wait=False)     #sets the temp target of this ramp, temp1 is in C
    logger.info(f"Ramping temperature to {temp1} C")    #logger info.

    while not linkam.settled:                           #runs data collection until we reach the temperature temp1.
        yield from collectAllThree(isDebugMode)         #note, that this checks on temp1 only once per USAXS/SAXS?WAXS cycle, basically once each 3-4 minutes
 
    t1 = time.time()                                    #reset timer for data collection
    delay1 = delay1min*60                               #convert minutes to seconds

    logger.info(f"Reached temperature, now collecting data for {delay1} seconds")
    
    while time.time()-t1 < delay1:                      # collects USAXS/SAXS/WAXS data for delay1 seconds
        yield from collectAllThree(isDebugMode)

    #Cooling cycle - cool down  
    logger.info(f"waited for {delay1} seconds, now changing temperature to {temp2} C")

    yield from bps.mv(linkam.rate, rate2)               #sets the rate of next ramp
    yield from linkam.set_target(temp2, wait=False)     #sets the temp target of next ramp, temp2 is in C. Typically cooling period

    while not linkam.settled:                           #runs data collection until we reach temp2
        yield from collectAllThree(isDebugMode)                    

    logger.info(f"reached {temp2} C")                   #record we reached tmep2

    #End run data collection - after cooling  
    yield from collectAllThree(isDebugMode)             #collect USAXS/SAXS/WAXS data at the end, typically temp2 is 40C

    logger.info(f"finished")                            #record end.
    
    if isDebugMode is not True:
       yield from after_command_list()                  # runs standard after scan scripts. 
