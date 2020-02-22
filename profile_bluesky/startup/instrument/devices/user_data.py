
"""
EPICS data about the user
"""

__all__ = [
    'bss_user_info',
    'user_data',
    ]

from ..session_logs import logger
logger.info(__file__)

from apstools.devices import ApsBssUserInfoDevice
from apstools.utils import trim_string_for_EPICS
from ..framework import sd
from ophyd import Component, Device, EpicsSignal


class UserDataDevice(Device):
    GUP_number = Component(EpicsSignal,         "9idcLAX:GUPNumber")
    macro_file = Component(EpicsSignal,         "9idcLAX:USAXS:macroFile")
    macro_file_time = Component(EpicsSignal,    "9idcLAX:USAXS:macroFileTime")
    run_cycle = Component(EpicsSignal,          "9idcLAX:RunCycle")
    sample_thickness = Component(EpicsSignal,   "9idcLAX:sampleThickness")
    sample_title = Component(EpicsSignal,       "9idcLAX:sampleTitle", string=True)
    scanning = Component(EpicsSignal,           "9idcLAX:USAXS:scanning")
    scan_macro = Component(EpicsSignal,         "9idcLAX:USAXS:scanMacro")
    spec_file = Component(EpicsSignal,          "9idcLAX:USAXS:specFile", string=True)
    spec_scan = Component(EpicsSignal,          "9idcLAX:USAXS:specScan", string=True)
    state = Component(EpicsSignal,              "9idcLAX:state", string=True)
    time_stamp = Component(EpicsSignal,         "9idcLAX:USAXS:timeStamp")
    user_dir = Component(EpicsSignal,           "9idcLAX:userDir", string=True)
    user_name = Component(EpicsSignal,          "9idcLAX:userName", string=True)

    # for GUI to know if user is collecting data: 0="On", 1="Off"
    collection_in_progress = Component(EpicsSignal, "9idcLAX:dataColInProgress")

    def set_state_plan(self, msg, confirm=True):
        """plan: tell EPICS about what we are doing"""
        msg = trim_string_for_EPICS(msg)
        yield from bps.abs_set(self.state, msg, wait=confirm)

    def set_state_blocking(self, msg):
        """ophyd: tell EPICS about what we are doing"""
        msg = trim_string_for_EPICS(msg)
        self.state.put(msg)


bss_user_info = ApsBssUserInfoDevice(
    "9id_bss:", name="bss_user_info")
sd.baseline.append(bss_user_info)

user_data = UserDataDevice(name="user_data")
sd.baseline.append(user_data)
