
"""
suspenders : conditions that will interrupt the RunEngine execution
"""

__all__ = [
]

from ..session_logs import logger
logger.info(__file__)

import bluesky.suspenders
from ophyd import Signal

from ..framework import RE, sd
from .aps_source import aps
from .permit import BeamInHutch
from .shutters import mono_shutter
from .white_beam_ready_calc import white_beam_ready


if aps.inUserOperations:
    sd.monitors.append(aps.current)
    # # suspend when current < 2 mA
    # # resume 100s after current > 10 mA
    # logger.info("Installing suspender for low APS current.")
    # suspend_APS_current = bluesky.suspenders.SuspendFloor(
    #     aps.current, 2, resume_thresh=10, sleep=100)
    # RE.install_suspender(suspend_APS_current)

    # suspend if we do not believe white beam is ready
    # considers:
    #   - APS storage ring current
    #   - 9ID undulator
    #   - white beam shutter
    # Signal provided by 9idcLAX:userCalc9 PV (swait record)
    suspender_white_beam_ready = bluesky.suspenders.SuspendBoolLow(
        white_beam_ready.available, sleep=100
    )
    RE.install_suspender(suspender_white_beam_ready)

    # remove comment if likely to use this suspender (issue #170)
    # suspend_FE_shutter = bluesky.suspenders.SuspendFloor(FE_shutter.pss_state, 1)
    # RE.install_suspender(suspend_FE_shutter)

    logger.info(f"mono shutter connected = {mono_shutter.pss_state.connected}")
    # remove comment if likely to use this suspender (issue #170)
    # suspend_mono_shutter = bluesky.suspenders.SuspendFloor(mono_shutter.pss_state, 1)

    logger.info("Defining suspend_BeamInHutch.  Install/remove in scan plans as desired.")
    suspend_BeamInHutch = bluesky.suspenders.SuspendBoolLow(BeamInHutch)
    # be more judicious when to use this suspender (only within scan plans) -- see #180
    # RE.install_suspender(suspend_BeamInHutch)
    # logger.info("BeamInHutch suspender installed")

else:
    # simulators
    _simulated_beam_in_hutch = Signal(name="_simulated_beam_in_hutch")
    suspend_BeamInHutch = bluesky.suspenders.SuspendBoolHigh(_simulated_beam_in_hutch)
    # RE.install_suspender(suspend_BeamInHutch)
