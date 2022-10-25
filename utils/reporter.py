
"""
report how much time remains in flyscan
"""

__all__ = [
    'remaining_time_reporter',
]

from ..session_logs import logger
logger.info(__file__)

from apstools.utils import run_in_thread
import time

@run_in_thread
def remaining_time_reporter(title, duration_s, interval_s=5, poll_s=0.05):
    if duration_s < interval_s:
        return
    t = time.time()
    expires = t + duration_s
    update = t + interval_s
    # print()
    while time.time() < expires:
        remaining = expires - t
        if t > update:
            update += interval_s
            logger.info(f"{title}: {remaining:.1f}s remaining")
        time.sleep(poll_s)
        t = time.time()
