"""
Dectris Pilatus area detectors.
"""

__all__ = [
    'saxs_det',
    'waxs_det',
    ]

from ..session_logs import logger
logger.info(__file__)

from ophyd import AreaDetector
from ophyd import PilatusDetectorCam
from ophyd import Component, Device, EpicsSignalWithRBV
from ophyd import SingleTrigger, ImagePlugin, HDF5Plugin
from ophyd.areadetector import ADComponent
from ophyd.areadetector.filestore_mixins import FileStoreHDF5IterativeWrite

from .area_detector_common import area_detector_EPICS_PV_prefix
from .area_detector_common import DATABROKER_ROOT_PATH
from .area_detector_common import EpicsDefinesHDF5FileNames
from .area_detector_common import _validate_AD_FileWriter_path_

import pathlib


# path for HDF5 files (as seen by EPICS area detector HDF5 plugin)
# path seen by detector IOC
WRITE_HDF5_FILE_PATH_PILATUS = "/mnt/usaxscontrol/USAXS_data/test/pilatus/%Y/%m/%d/"
# path seen by databroker
READ_HDF5_FILE_PATH_PILATUS = "/share1/USAXS_data/test/pilatus/%Y/%m/%d/"

_validate_AD_FileWriter_path_(WRITE_HDF5_FILE_PATH_PILATUS, DATABROKER_ROOT_PATH)


class MyPilatusHDF5Plugin(EpicsDefinesHDF5FileNames):
    """adapt HDF5 plugin for Pilatus detector"""

    # fixes one problem, MUST end with path delimiter
    @property
    def write_path_template(self):
        rootp = self.reg_root
        delimiter = "/"
        if self.path_semantics == 'posix':
            ret = pathlib.PurePosixPath(self._write_path_template)
        elif self.path_semantics == 'windows':
            ret = pathlib.PureWindowsPath(self._write_path_template)
            delimiter = "\\"
        elif self.path_semantics is None:
            # We are forced to guess which path semantics to use.
            # Guess that the AD driver is running on the same OS as this client.
            ret = pathlib.PurePath(self._write_path_template)
        else:
            # This should never happen, but just for the sake of future-proofing...
            raise ValueError(f"Cannot handle path_semantics={self.path_semantics}")

        if self._read_path_template is None and rootp not in ret.parents:
            if not ret.is_absolute():
                ret = rootp / ret
            else:
                raise ValueError(
                    ('root: {!r} in not consistent with '
                     'read_path_template: {!r}').format(rootp, ret))

        return f"{ret}{delimiter}"  # THIS is the fix, MUST end with delimiter

    @write_path_template.setter
    def write_path_template(self, val):
        self._write_path_template = val


class MyPilatusDetector(SingleTrigger, AreaDetector):
    """Pilatus detector(s) as used by 9-ID-C USAXS"""

    cam = ADComponent(PilatusDetectorCam, "cam1:")
    image = ADComponent(ImagePlugin, "image1:")

    hdf1 = ADComponent(
        MyPilatusHDF5Plugin,
        suffix = "HDF1:",
        root = DATABROKER_ROOT_PATH,
        write_path_template = WRITE_HDF5_FILE_PATH_PILATUS,
        read_path_template = READ_HDF5_FILE_PATH_PILATUS,
        )


try:
    nm = "Pilatus 100k"
    prefix = area_detector_EPICS_PV_prefix[nm]
    saxs_det = MyPilatusDetector(
        prefix, name="saxs_det", labels=["camera", "area_detector"])
    saxs_det.read_attrs.append("hdf1")
except TimeoutError as exc_obj:
    msg = f"Timeout connecting with {nm} ({prefix})"
    logger.warning(msg)
    saxs_det = None

try:
    nm = "Pilatus 200kw"
    prefix = area_detector_EPICS_PV_prefix[nm]
    waxs_det = MyPilatusDetector(
        prefix, name="waxs_det", labels=["camera", "area_detector"])
    waxs_det.read_attrs.append("hdf1")
except TimeoutError as exc_obj:
    msg = f"Timeout connecting with {nm} ({prefix})"
    logger.warning(msg)
    waxs_det = None
