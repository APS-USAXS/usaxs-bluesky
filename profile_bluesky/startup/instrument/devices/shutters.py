
"""
shutters
"""

__all__ = [
    'ccd_shutter',
    'FE_shutter',
    'mono_shutter',
    'ti_filter_shutter',
    'usaxs_shutter',
    'a_shutter_autoopen',
]

from ..session_logs import logger
logger.info(__file__)


from apstools.devices import ApsPssShutter
from apstools.devices import EpicsOnOffShutter
from apstools.devices import SimulatedApsPssShutterWithStatus
from ophyd import EpicsSignal
from ophyd import Component
from ophyd import Signal
import time

from .aps_source import aps
from .permit import operations_in_9idc

class My20IdPssShutter(ApsPssShutter):
    """
    Controls a single APS PSS shutter at 20ID.

    ======  =========  =====
    action  PV suffix  value
    ======  =========  =====
    open    _opn       1
    close   _cls       1
    ======  =========  =====
    """
    # bo records that reset after a short time, set to 1 to move
    open_signal = Component(EpicsSignal, "_opn")
    close_signal = Component(EpicsSignal, "_cls")

# class PssShutters(Device):
#     """
#     20ID A & B APS PSS shutters.

#     =======  =============
#     shutter  P, PV prefix
#     =======  =============
#     A        20id:shutter0
#     B        20id:shutter1
#     =======  =============
#     """
#     a_shutter = Component(My20IdPssShutter, "20id:shutter0")
#     b_shutter = Component(My20IdPssShutter, "20id:shutter1")

# pss_shutters = PssShutters("", name="pss_shutters")

if aps.inUserOperations and operations_in_9idc():
    FE_shutter = My20IdPssShutter(
        #20id:shutter0_opn and 20id:shutter0_cls
        "20id:shutter0",  
        name="FE_shutter")

    mono_shutter = My20IdPssShutter(
         #20id:shutter1_opn and 20id:shutter1_cls
        "20id:shutter1", 
        name="mono_shutter")

    usaxs_shutter = EpicsOnOffShutter(
        "9idcLAX:userTran3.A",
        name="usaxs_shutter")

    a_shutter_autoopen = EpicsSignal(
        "9idcLAX:AShtr:Enable",
        name="a_shutter_autoopen")

else:
    logger.warning("!"*30)
    if operations_in_9idc():
        logger.warning("Session started when APS not operating.")
    else:
        logger.warning("Session started when 20ID-C is not operating.")
    logger.warning("Using simulators for all shutters.")
    logger.warning("!"*30)
    FE_shutter = SimulatedApsPssShutterWithStatus(name="FE_shutter")
    mono_shutter = SimulatedApsPssShutterWithStatus(name="mono_shutter")
    usaxs_shutter = SimulatedApsPssShutterWithStatus(name="usaxs_shutter")
    a_shutter_autoopen = Signal(name="a_shutter_autoopen", value=0)


ti_filter_shutter = usaxs_shutter       # alias
ti_filter_shutter.delay_s = 0.2         # shutter needs some recovery time

ccd_shutter = EpicsOnOffShutter("9idcRIO:Galil2Bo0_CMD", name="ccd_shutter")


connect_delay_s = 1
while not mono_shutter.pss_state.connected:
    logger.info(f"Waiting {connect_delay_s}s for mono shutter PV to connect")
    time.sleep(connect_delay_s)


