
"""
Point Grey Blackfly area detector

note: this is one of the easiest area detector setups in Ophyd
"""

__all__ = [
    'blackfly_det',
    'blackfly_optical',
    ]

import logging

logger = logging.getLogger(__name__)
logger.info(__file__)

from .area_detector_common import Override_AD_plugin_primed
# from apstools.devices import AD_prime_plugin2
from bluesky import plan_stubs as bps

from ophyd import ADComponent
from ophyd import AreaDetector
from ophyd import ColorConvPlugin
from ophyd import EpicsSignal
from ophyd import ImagePlugin
from ophyd import PointGreyDetectorCam
from ophyd import SingleTrigger
from ophyd import TransformPlugin

import os

import warnings

from .area_detector_common import _validate_AD_FileWriter_path_
from .area_detector_common import area_detector_EPICS_PV_prefix
from .area_detector_common import DATABROKER_ROOT_PATH
from .area_detector_common import EpicsDefinesJpegFileNames
from .area_detector_common import EpicsDefinesTiffFileNames


RADIOGRAPHY_CAMERA = 'PointGrey BlackFly'                   # 9idFLY1:
OPTICAL_CAMERA = 'PointGrey BlackFly Optical'               # 9idFLY2:


# path for image files (as seen by EPICS area detector writer plugin)
# path seen by detector IOC
PATH_BASE = "/share1/USAXS_data/test/blackfly_optical"
WRITE_IMAGE_FILE_PATH = PATH_BASE + "/%Y/%m/%d/"
# path seen by databroker
READ_IMAGE_FILE_PATH = WRITE_IMAGE_FILE_PATH

_validate_AD_FileWriter_path_(WRITE_IMAGE_FILE_PATH, DATABROKER_ROOT_PATH)
_validate_AD_FileWriter_path_(READ_IMAGE_FILE_PATH, DATABROKER_ROOT_PATH)


class MyPointGreyDetector(SingleTrigger, AreaDetector):
    """PointGrey Black Fly detector(s) as used by 9-ID-C USAXS"""

    cam = ADComponent(PointGreyDetectorCam, "cam1:")
    image = ADComponent(ImagePlugin, "image1:")


class MyPointGreyDetectorJPEG(MyPointGreyDetector, AreaDetector):
    """
    Variation to write image as JPEG

    To save an image (using existing configuration)::

        blackfly_optical.stage()
        blackfly_optical.trigger()
        blackfly_optical.unstage()

    """

    jpeg1 = ADComponent(
        EpicsDefinesJpegFileNames,
        suffix = "JPEG1:",
        root = DATABROKER_ROOT_PATH,
        write_path_template = WRITE_IMAGE_FILE_PATH,
        read_path_template = READ_IMAGE_FILE_PATH,
        kind="normal",
        )
    trans1 = ADComponent(TransformPlugin, "Trans1:")
    cc1 = ADComponent(ColorConvPlugin, "CC1:")

    @property
    def image_file_name(self):
        return self.jpeg1.full_file_name.get()

    def image_prep(self, path, filename_base, order_number):
        plugin = self.jpeg1
        path = "/mnt" + os.path.abspath(path) + "/"  # MUST end with "/"
        yield from bps.mv(
            plugin.file_path, path,
            plugin.file_name, filename_base,
            plugin.file_number, order_number,
        )

    @property
    def should_save_image(self):
        return _flag_save_sample_image_.get() in (1, "Yes")

    def take_image(self):
        yield from bps.stage(self)
        yield from bps.trigger(self, wait=True)
        yield from bps.unstage(self)


class MyPointGreyDetectorTIFF(MyPointGreyDetector, AreaDetector):
    """
    Variation to write image as TIFF

    To save an image (using existing configuration)::

        blackfly_optical.stage()
        blackfly_optical.trigger()
        blackfly_optical.unstage()

    """

    tiff1 = ADComponent(
        EpicsDefinesTiffFileNames,
        suffix = "TIFF1:",
        root = DATABROKER_ROOT_PATH,
        write_path_template = WRITE_IMAGE_FILE_PATH,
        read_path_template = READ_IMAGE_FILE_PATH,
        kind="normal",
        )
    trans1 = ADComponent(TransformPlugin, "Trans1:")
    cc1 = ADComponent(ColorConvPlugin, "CC1:")

    @property
    def image_file_name(self):
        return self.tiff1.full_file_name.get()

    def image_prep(self, path, filename_base, order_number):
        plugin = self.tiff1
        path = "/mnt" + os.path.abspath(path) + "/"  # MUST end with "/"
        yield from bps.mv(
            plugin.file_path, path,
            plugin.file_name, filename_base,
            plugin.file_number, order_number,
        )

    @property
    def should_save_image(self):
        return _flag_save_sample_image_.get() in (1, "Yes")

    def take_image(self):
        yield from bps.stage(self)
        yield from bps.trigger(self, wait=True)
        yield from bps.unstage(self)


try:
    nm = RADIOGRAPHY_CAMERA
    prefix = area_detector_EPICS_PV_prefix[nm]
    blackfly_det = MyPointGreyDetector(
        prefix, name="blackfly_det",
        labels=["camera", "area_detector"])
except TimeoutError as exc_obj:
    msg = f"Timeout connecting with {nm} ({prefix})"
    logger.warning(msg)
    blackfly_det = None


_flag_save_sample_image_ = EpicsSignal(
    "9idcLAX:saveFLY2Image",
    string=True,
    name="_flag_save_sample_image_",
    )


try:
    nm = OPTICAL_CAMERA
    prefix = area_detector_EPICS_PV_prefix[nm]
    blackfly_optical = MyPointGreyDetectorJPEG(
        prefix, name="blackfly_optical",
        labels=["camera", "area_detector"])
    blackfly_optical.read_attrs.append("jpeg1")
    blackfly_optical.jpeg1.stage_sigs["file_write_mode"] = "Single"
    if not Override_AD_plugin_primed(blackfly_optical.jpeg1):
        warnings.warn(
            "NOTE: blackfly_optical.jpeg1 has not been primed yet."
            "  BEFORE using this detector in bluesky, call: "
            "  AD_prime_plugin2(blackfly_optical.jpeg1)"
        )
except TimeoutError as exc_obj:
    logger.warning(
        "Timeout connecting with %s (%s): %s",
        nm, prefix, exc_obj
    )
    blackfly_optical = None
