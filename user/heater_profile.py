"""
Run a temperature profile on the sample heater as a Bluesky plan.

This file defines a function (bluesky "plan") named
    ``planHeaterProcess()``
that runs the desired temperature profile schedule.
All configuration is communicated via EPICS PVs
which are interfaced here as ophyd EpicsSignal objects.
Other plans and functions are used to simplify the
interface in planHeaterProcess().

Called (via ``import``) from ``heater_profile_process.py``
(which is started/stopped/restarted from ``heater_profile_manager.sh``),
both of which are in directory ``~/.ipython/profile/bluesky/usaxs_support/``.

See https://github.com/APS-USAXS/ipython-usaxs/issues/482 for details.
"""

from apstools import devices
from bluesky import plan_stubs as bps
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO

import datetime
import os
import time


SECOND = 1
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR
WEEK = 7 * DAY

# Create devices here so we remain independent of the instrument package.
exit_request_signal = EpicsSignal("9idcLAX:bit14", name="exit_request_signal")
linkam_ci94 = devices.Linkam_CI94_Device("9idcLAX:ci94:", name="linkam_ci94")
linkam_tc1 = devices.Linkam_T96_Device("9idcLINKAM:tc1:", name="linkam_tc1")

# write output to log file in userDir, name=MMDD-HHmm-heater-log.txt
user_dir = EpicsSignalRO("9idcLAX:userDir", name="user_dir", string=True)

for o in (exit_request_signal, linkam_ci94, linkam_tc1, user_dir):
    o.wait_for_connection()

log_file_name = os.path.join(
    user_dir.get(),
    datetime.datetime.now().strftime("%m%d-%H%M-heater-log.txt")
)

# make a common term for the ramp rate (devices use different names)
linkam_ci94.ramp = linkam_ci94.rate
linkam_tc1.ramp = linkam_tc1.ramprate

linkam = linkam_tc1     # choose which one
# linkam = linkam_ci94     # choose which one

# set tolerance for "in position" (Python term, not an EPICS PV)
# note: done = |readback - setpoint| <= tolerance
linkam.temperature.tolerance.put(1.0)
# sync the "inposition" computation
linkam.temperature.cb_readback()


class StopHeaterPlan(Exception):
    "Exception to stop the heater plan is stopping."


def readable_time(duration, rounding=2):
    """
    Return a string representation of the duration.

    EXAMPLES::

        readable_time(425) --> '7m 5s'
        readable_time(1425) --> '23m 45s'
        readable_time(21425) --> '5h 57m 5s'
        readable_time(360) --> '6m'
        readable_time(62.123) --> '1m 2.12s'
    """
    weeks = int(duration / WEEK)
    known = weeks * WEEK

    days = int((duration - known) / DAY)
    known += days * DAY

    hours = int((duration - known) / HOUR)
    known += hours * HOUR

    minutes = int((duration - known) / MINUTE)
    known += minutes * MINUTE

    seconds = round(duration - known, rounding)
    db = dict(w=weeks, d=days, h=hours, m=minutes, s=seconds)

    s = [
        f"{v}{k}"
        for k, v in db.items()
        if v != 0
    ]
    return " ".join(s)


def log_it(text):
    """Cheap, lazy way to add to log file.  Gotta be better way..."""
    if not os.path.exists(log_file_name):
        # create the file and header
        with open(log_file_name, "w") as f:
            f.write(f"# file: {log_file_name}\n")
            f.write(f"# created: {datetime.datetime.now()}\n")
            f.write(f"# from: {__file__}\n")
    with open(log_file_name, "a") as f:
        # write the payload
        dt = datetime.datetime.now()
        # ISO-8601 format time, ms precision
        iso8601 = dt.isoformat(sep=" ", timespec='milliseconds')
        f.write(f"{iso8601}: {text}\n")


def linkam_report():
    """Report current values for selected controller."""
    units = linkam.units.get()
    log_it(
        f"{linkam.name}"
        f" T={linkam.temperature.position:.1f}{units}"
        f" setpoint={linkam.temperature.setpoint.get():.1f}{units}"
        f" ramp:{linkam.ramp.get()}"
        f" settled: {linkam.temperature.inposition}"
        f" done: {linkam.temperature.done.get()}"
    )


def change_ramp_rate(value):
    """BS plan: change controller's ramp rate."""
    yield from bps.mv(linkam.ramp, value)
    log_it(
        f"Change {linkam.name} rate to {linkam.ramp.get():.0f} C/min"
    )


def check_for_exit(t0):
    """
    BS plan: Tell linkam controller to stop (a temperature change in progress).

    Can't call linkam.temperature.stop() since that has blocking code.
    Implement that method here by holding current position.

    Raise ``StopHeaterPlan`` exception is exit was requested.
    Otherwise return ```None``
    """
    # Watch for user exit while waiting
    if exit_request_signal.get() in (0, exit_request_signal.enum_strs[0]):
        # no exit requested
        return

    yield from bps.mv(linkam.temperature, linkam.position)
    minutes = (time.time() - t0) / 60
    log_it(
        "User requested exit during set"
        f" after {minutes:.2f}m."
        " Stopping the heater."  # FIXME: Stopping? or holding at temperature?
    )
    linkam_report()
    raise StopHeaterPlan(f"Stop requested after {minutes:.2f}m")


def linkam_change_setpoint_and_wait(value):
    """
    BS plan: change the temperature setpoint and wait for inposition.

    To change temperature and wait:
       bps.mv(linkam.temperature, value)
       Turns on heater power (if it was off).
    To just change temperature, do not wait (hint: use the setpoint directly):
       bps.mv(linkam.temperature.setpoint, value)
       Does NOT turn on heater power.
    """
    t0 = time.time()
    yield from bps.mv(
        linkam.temperature.setpoint, value,
    )
    log_it(f"Change {linkam.name} setpoint to {linkam.setpoint.get():.2f} C")
    while not linkam.temperature.inposition:
        yield from check_for_exit(t0)
        yield from bps.sleep(1)
    log_it(f"Done, that took {time.time()-t0:.2f}s")
    linkam_report()


def linkam_hold(duration):
    """BS plan: hold at temperature for the duration (s)."""
    log_it("{linkam.name} holding for {readable_time(duration)}")
    t0 = time.time()
    time_expires = t0 + duration
    while time.time() < time_expires:
        yield from check_for_exit(t0)
        yield from bps.sleep(1)
    log_it(f"{linkam.name} holding period ended")
    linkam_report()


def planHeaterProcess():
    """BS plan: Run one temperature profile on the sample heater."""
    log_it(f"Starting planHeaterProcess() for {linkam.name}")
    linkam_report()

    try:
        yield from change_ramp_rate(3)
        yield from linkam_change_setpoint_and_wait(1083)
        # two hours = 2 * HOUR, two minutes = 2 * MINUTE
        yield from linkam_hold(3 * HOUR)
        yield from change_ramp_rate(3)
        yield from linkam_change_setpoint_and_wait(40)
    except StopHeaterPlan:
        return

    # DEMO: signal for an orderly exit after first run
    yield from bps.mv(exit_request_signal, True)
