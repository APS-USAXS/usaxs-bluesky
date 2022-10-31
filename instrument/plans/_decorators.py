"""
This code wil be hoisted to apsutils.
"""

from bluesky.utils import make_decorator
import logging

logger = logging.getLogger(__name__)


def restorable_stage_sigs_wrapper(user_plan, devices):
    """
    Save stage_sigs from each device and restore after the user_plan.

    The user_plan is free to modify the stage_sigs of each device
    without further need to preserve original values.
    """
    def display(preface):
        for device in devices:
            logger.debug(
                "%s: %s.stage_sigs: %s", preface, device.name, device.stage_sigs
            )

    def _restore():
        for device in reversed(devices):
            device.stage_sigs = original[device].copy()
        display("AFTER restore")

    original = {}
    display("ORIGINAL")
    for device in devices:
        original[device] = device.stage_sigs.copy()

    try:
        display("BEFORE plan")
        yield from user_plan
        display("AFTER plan")
    finally:
        _restore()


restorable_stage_sigs = make_decorator(restorable_stage_sigs_wrapper)
