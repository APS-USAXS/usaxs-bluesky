
"""
instrument constants
"""

__all__ = [
    'constants',
    ]

from ..session_logs import logger
logger.info(__file__)

constants = {
    "SAXS_TR_PINY_OFFSET" : 14, # measured on 10-16-2022 JIL, after move to 20ID, this is now X move...  
    "SAXS_TR_TIME" : 3, # how long to measure transmission 
    "SAXS_PINZ_OFFSET" : 5, # move of pinz before any sample or piny move
    "TR_MAX_ALLOWED_COUNTS" : 980000, # maximum allowed counts for upd before assume topped up
    "USAXS_AY_OFFSET" : 8, # USAXS transmission diode AY offset, calibrated by JIL 2018/04/10 For Delhi crystals diode is between 5 - 10 mm .. center is 8mm
    "MEASURE_DARK_CURRENTS" : True, # MEASURE dark currents on start of data collection
    "SYNC_ORDER_NUMBERS" : True, # sync order numbers among devices on start of collect data sequence
}
