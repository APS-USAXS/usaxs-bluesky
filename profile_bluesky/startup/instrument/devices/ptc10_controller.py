"""
PTC10 Programmable Temperature Controller
"""

__all__ = [
    "ptc10",
]

# from ..session_logs import logger
# logger.info(__file__)
import logging  # TODO: switch back for operations

logger = logging.getLogger(__name__)

# from ophyd import EpicsSignal
from ophyd import Component
from ophyd import Device
from ophyd import EpicsSignalRO
from ophyd import EpicsSignalWithRBV
from ophyd import PVPositioner
from ophyd import Signal


class PTC10AioChannel(Device):
    """
    SRS PTC10 AIO module
    """

    voltage = Component(EpicsSignalRO, "voltage_RBV", kind="config")
    # highlimit = Component(EpicsSignalWithRBV, "highLimit", kind="config")
    lowlimit = Component(EpicsSignalWithRBV, "lowLimit", kind="config")
    iotype = Component(EpicsSignalWithRBV, "ioType", kind="config", string=True)
    setpoint = Component(EpicsSignalWithRBV, "setPoint", kind="config")
    ramprate = Component(EpicsSignalWithRBV, "rampRate", kind="config")

    pidmode = Component(EpicsSignalWithRBV, "pid:mode", kind="config", string=True)
    P = Component(EpicsSignalWithRBV, "pid:P", kind="config")
    I = Component(EpicsSignalWithRBV, "pid:I", kind="config")
    D = Component(EpicsSignalWithRBV, "pid:D", kind="config")

    inputchoice = Component(EpicsSignalWithRBV, "pid:input", kind="config", string=True)
    tunelag = Component(EpicsSignalWithRBV, "tune:lag", kind="config")
    tunestep = Component(EpicsSignalWithRBV, "tune:step", kind="config")
    tunemode = Component(EpicsSignalWithRBV, "tune:mode", kind="config", string=True)
    tunetype = Component(EpicsSignalWithRBV, "tune:type", kind="config", string=True)


class PTC10RtdChannel(Device):
    """
    SRS PTC10 RTD module channel
    """

    units = Component(EpicsSignalRO, "units_RBV", kind="config", string=True)
    sensor = Component(EpicsSignalWithRBV, "sensor", kind="config", string=True)
    channelrange = Component(EpicsSignalWithRBV, "range", kind="config", string=True)
    current = Component(EpicsSignalWithRBV, "current", kind="config", string=True)
    power = Component(EpicsSignalWithRBV, "power", kind="config", string=True)


class USAXS_PTC10(PVPositioner):
    """
    PTC10 as seen from the GUI screen

    The IOC templates and .db files provide a more general depiction.
    The PTC10 has feature cards, indexed by the slot where each is
    installed (2A, 3A, 5A, ...).  Here, slot 2 has four temperature
    sensor channels (2A, 2B, 2C, 2D).  The EPICS database template file
    calls for these EPICS database files:

    * PTC10_tc_chan.db  (channels 2A, 2B, 2C, 2D, ColdJ2)
    * PTC10_rtd_chan.db (channels 3A, 3B)
    * PTC10_aio_chan.db (channels 5A, 5B, 5C, 5D)
    """

    # PVPositioner interface
    readback = Component(EpicsSignalRO, "2A:temperature", kind="hinted")
    setpoint = Component(EpicsSignalWithRBV, "5A:highLimit", kind="hinted")
    done = Component(Signal, value=True, kind="omitted")
    done_value = True
    # TODO: stop Signal (and how to handle that)

    # for computation of soft `done` signal
    tolerance = Component(
        Signal, value=1, kind="config"
    )  # default +/- 1 degree for "at temperature"
    report_dmov_changes = Component(Signal, value=True, kind="omitted")

    # PTC10 base
    enable = Component(EpicsSignalWithRBV, "outputEnable", kind="config")

    # PTC10 thermocouple module
    temperatureB = Component(
        EpicsSignalRO, "2B:temperature", kind="hinted"
    )  # TODO: how used?
    temperatureC = Component(EpicsSignalRO, "2C:temperature", kind="normal")
    # temperatureD = Component(EpicsSignalRO, "2D:temperature", kind="omitted")  # it's a NaN now
    coldj2 = Component(
        EpicsSignalRO, "ColdJ2:temperature", kind="normal"
    )  # TODO: how used?

    # PTC10 RTD module
    rtd = Component(PTC10RtdChannel, "3A:")

    # PTC10 AIO module
    aio = Component(PTC10AioChannel, "5A:")

    def cb_readback(self, *args, **kwargs):
        """
        Called when readback changes (EPICS CA monitor event).
        """
        diff = self.readback.get() - self.setpoint.get()
        dmov = abs(diff) <= self.tolerance.get()
        if self.report_dmov_changes.get() and dmov != self.done.get():
            logger.debug(f"{self.name} reached: {dmov}")
        self.done.put(dmov)

    def cb_setpoint(self, *args, **kwargs):
        """
        Called when setpoint changes (EPICS CA monitor event).

        When the setpoint is changed, force ``done=False``.  For any move,
        ``done`` MUST change to ``!= done_value``, then change back to
        ``done_value (True)``.  Without this response, a small move
        (within tolerance) will not return.  Next update of readback
        will compute ``self.done``.
        """
        self.done.put(not self.done_value)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.readback.name = self.name

        # to compute the soft `done` signal
        self.readback.subscribe(self.cb_readback)
        self.setpoint.subscribe(self.cb_setpoint)


ptc10 = USAXS_PTC10("9idcTEMP:tc1:", name="ptc10")
ptc10.report_dmov_changes.put(True)  # a diagnostic
ptc10.tolerance.put(1.0)  # done when |readback-setpoint|<=tolerance
