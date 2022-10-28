
"""
rotate the sample with PI C867 motor
"""

__all__ = """
    PI_Off
    PI_onF
    PI_onR
""".split()

from ..session_logs import logger
logger.info(__file__)

from ..devices import pi_c867
from bluesky import plan_stubs as bps


def PI_Off(timeout=1, md=None):
    """
    Plan: stop rotating sample in either direction.

    NOTE:
        Do NOT stop either jog by sending 1 to the
        motor `.STOP` field.  That will result in a
        `FailedStatus` exception if the motor is
        in motion.
    """
    yield from bps.mv(
        pi_c867.jog_forward, 0,
        pi_c867.jog_reverse, 0,
        timeout=1,
    )


def PI_onF(timeout=10, md=None):
    """Plan: start rotating sample in forward direction."""
    yield from bps.mv(pi_c867.home, "forward", timeout=timeout)
    yield from bps.abs_set(pi_c867.jog_forward, 1)


def PI_onR(timeout=10, md=None):
    """Plan: start rotating sample in reverse direction."""
    yield from bps.mv(pi_c867.home, "reverse", timeout=timeout)
    yield from bps.abs_set(pi_c867.jog_reverse, 1)
