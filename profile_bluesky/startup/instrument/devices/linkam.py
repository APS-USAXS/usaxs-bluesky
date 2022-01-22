"""
Linkam temperature controllers: T96 (tc1) & CI94 (older)
"""

__all__ = [
    'linkam_ci94',
    'linkam_tc1',
    ]

from ..session_logs import logger
logger.info(__file__)

from apstools.devices import Linkam_CI94_Device
from apstools.devices import Linkam_T96_Device


linkam_ci94 = Linkam_CI94_Device("9idcLAX:ci94:", name="ci94")
linkam_tc1 = Linkam_T96_Device("9idcLINKAM:tc1:", name="linkam_tc1")

for _o in (linkam_ci94, linkam_tc1):
    _o.wait_for_connection()

    # set tolerance for "in position" (Python term, not an EPICS PV)
    # note: done = |readback - setpoint| <= tolerance
    _o.temperature.tolerance.put(1.0)

    # sync the "inposition" computation
    _o.temperature.cb_readback()

    # easy access to the engineering units
    _o.units.put(
        _o.temperature.readback.metadata["units"]
    )

# make a common term for the ramp rate (devices use different names)
linkam_ci94.ramp = linkam_ci94.rate
linkam_tc1.ramp = linkam_tc1.ramprate
