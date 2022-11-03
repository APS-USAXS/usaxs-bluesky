
"""
Bluesky plans to tune various axes and stages

NOTE:  Don't use blocking calls here
"""

__all__ = """
    empty_plan
    instrument_default_tune_ranges
    tune_a2rp
    tune_after_imaging
    tune_ar
    tune_asrp
    tune_diode
    tune_dx
    tune_dy
    tune_m2rp
    tune_mr
    tune_msrp
    tune_saxs_optics
    tune_usaxs_optics
    update_EPICS_tuning_widths
    """.split()

import logging

logger = logging.getLogger(__name__)
logger.info(__file__)

from bluesky import plan_stubs as bps
from ophyd import Kind
import time

from ..devices import autoscale_amplifiers, upd_controls, I0_controls, I00_controls
from ..devices import user_override
from ..devices.axis_tuning import axis_tune_range
from ..devices.axis_tuning import TUNE_METHOD_PEAK_CHOICE
from ..devices.axis_tuning import TUNING_DET_SIGNAL
from ..devices.axis_tuning import USING_MS_STAGE
from ..devices.stages import m_stage, ms_stage, s_stage, a_stage, as_stage, d_stage
from ..devices.shutters import mono_shutter, ti_filter_shutter
from ..devices.monochromator import monochromator
from ..devices.scalers import scaler0, I0_SIGNAL, I00_SIGNAL, UPD_SIGNAL
from ..devices.general_terms import terms
from ..devices.suspenders import suspend_BeamInHutch
from ..framework import RE
from .mode_changes import mode_USAXS
from .requested_stop import IfRequestedStopBeforeNextScan


# used in instrument_default_tune_ranges() below
user_override.register("usaxs_minstep")


def _tune_base_(axis, md={}):
    """
    plan for simple tune and report

    satisfies: report of tuning OK/not OK on console
    """
    yield from IfRequestedStopBeforeNextScan()
    logger.info(f"tuning axis: {axis.name}")
    axis_start = axis.position
    yield from bps.mv(
        mono_shutter, "open",
        ti_filter_shutter, "open",
    )
    yield from autoscale_amplifiers([upd_controls, I0_controls, I00_controls])
    yield from axis.tune(md=md)
    yield from bps.mv(
        ti_filter_shutter, "close",
        scaler0.count_mode, "AutoCount",
    )

    found = axis.tuner.peak_detected()
    logger.info(f"axis: {axis.name}")
    logger.info(f"starting position: {axis_start}")
    logger.info(f"peak detected: {found}")
    if found:
        logger.info(f"  max: {axis.tuner.peaks.max}")
        logger.info(f"  center: {axis.tuner.peaks.cen}")
        logger.info(f"  centroid: {axis.tuner.peaks.com}")
        logger.info(f"  fwhm: {axis.tuner.peaks.fwhm}")
    logger.info(f"final position: {axis.position}")


def tune_mr(md={}):
    yield from bps.mv(scaler0.preset_time, 0.1)
    md['plan_name'] = "tune_mr"
    # print(f"metadata={md}")  # TOO much data to print
    yield from _tune_base_(m_stage.r, md=md)


def tune_m2rp(md={}):
    yield from bps.sleep(0.2)   # piezo is fast, give the system time to react
    yield from bps.mv(scaler0.preset_time, 0.1)
    md['plan_name'] = "tune_m2rp"
    yield from _tune_base_(m_stage.r2p, md=md)
    yield from bps.sleep(0.1)   # piezo is fast, give the system time to react


def empty_plan(*args, **kwargs):
    logger.info(f"Doing nothing: args={args}, kwargs={kwargs}")
    yield from bps.null()


if m_stage.isChannelCut:
    m_stage.r2p.tuner = empty_plan      # TODO: should mimic TuneAxis()?
    m_stage.r2p.pre_tune_method = empty_plan
    m_stage.r2p.post_tune_method = empty_plan
    tune_m2rp = empty_plan


def tune_msrp(md={}):
    pass
    # yield from bps.mv(scaler0.preset_time, 0.1)
    # md['plan_name'] = "tune_msrp"
    # yield from _tune_base_(ms_stage.rp, md=md)


def tune_ar(md={}):
    yield from bps.mv(ti_filter_shutter, "open")
    ##redundant## yield from autoscale_amplifiers([upd_controls])
    yield from bps.mv(scaler0.preset_time, 0.1)
    yield from bps.mv(upd_controls.auto.mode, "manual")
    md['plan_name'] = "tune_ar"
    yield from _tune_base_(a_stage.r, md=md)
    yield from bps.mv(upd_controls.auto.mode, "auto+background")


def tune_asrp(md={}):
    pass
#     yield from bps.mv(ti_filter_shutter, "open")
#     ##redundant## yield from autoscale_amplifiers([upd_controls])
#     yield from bps.mv(scaler0.preset_time, 0.1)
#     yield from bps.mv(upd_controls.auto.mode, "manual")
#     md['plan_name'] = "tune_asrp"
#     yield from _tune_base_(as_stage.rp, md=md)
#     yield from bps.mv(upd_controls.auto.mode, "auto+background")


def tune_a2rp(md={}):
    yield from bps.mv(ti_filter_shutter, "open")
    yield from bps.sleep(0.1)   # piezo is fast, give the system time to react
    ##redundant## yield from autoscale_amplifiers([upd_controls])
    yield from bps.mv(scaler0.preset_time, 0.1)
    yield from bps.mv(upd_controls.auto.mode, "manual")
    md['plan_name'] = "tune_a2rp"
    yield from _tune_base_(a_stage.r2p, md=md)
    yield from bps.mv(upd_controls.auto.mode, "auto+background")
    yield from bps.sleep(0.1)   # piezo is fast, give the system time to react


def tune_dx(md={}):
    yield from bps.mv(ti_filter_shutter, "open")
    ##redundant## yield from autoscale_amplifiers([upd_controls])
    yield from bps.mv(scaler0.preset_time, 0.1)
    yield from bps.mv(upd_controls.auto.mode, "manual")
    md['plan_name'] = "tune_dx"
    yield from _tune_base_(d_stage.x, md=md)
    yield from bps.mv(upd_controls.auto.mode, "auto+background")


def tune_dy(md={}):
    yield from bps.mv(ti_filter_shutter, "open")
    ##redundant## yield from autoscale_amplifiers([upd_controls])
    yield from bps.mv(scaler0.preset_time, 0.1)
    yield from bps.mv(upd_controls.auto.mode, "manual")
    md['plan_name'] = "tune_dy"
    yield from _tune_base_(d_stage.y, md=md)
    yield from bps.mv(upd_controls.auto.mode, "auto+background")


def tune_diode(md={}):
    yield from tune_dx(md=md)
    yield from tune_dy(md=md)


# -------------------------------------------


def tune_usaxs_optics(side=False, md={}):
    """
    tune all the instrument optics currently in configuration

    This plan is for staff use.
    Users are advised to use preUSAXStune() instead.
    """
    yield from mode_USAXS()

    suspender_preinstalled = suspend_BeamInHutch in RE.suspenders
    if not suspender_preinstalled:
        yield from bps.install_suspender(suspend_BeamInHutch)

    yield from tune_mr(md=md)
    yield from tune_m2rp(md=md)
    if side:
        yield from tune_msrp(md=md)
        yield from tune_asrp(md=md)
    yield from tune_ar(md=md)
    yield from tune_a2rp(md=md)

    if not suspender_preinstalled:
        yield from bps.remove_suspender(suspend_BeamInHutch)

    yield from bps.mv(
        terms.preUSAXStune.num_scans_last_tune, 0,
        terms.preUSAXStune.epoch_last_tune, time.time(),
    )


def tune_saxs_optics(md={}):
    yield from tune_mr(md=md)
    yield from tune_m2rp(md=md)
    yield from bps.mv(
        #terms.preUSAXStune.num_scans_last_tune, 0,
        terms.preUSAXStune.epoch_last_tune, time.time(),
    )


def tune_after_imaging(md={}):
    epics_ar_tune_range = axis_tune_range.ar.get()  # remember

    # tune_ar with custom tune range if that is larger
    custom_range = 0.005
    if epics_ar_tune_range > custom_range:
        yield from bps.mv(axis_tune_range.ar, custom_range)
        yield from tune_ar(md=md)

    # finally, tune_ar with standard tune range
    yield from bps.mv(axis_tune_range.ar, epics_ar_tune_range)
    yield from tune_ar(md=md)
    yield from tune_a2rp(md=md)


def instrument_default_tune_ranges():
    """
    plan: (re)compute tune ranges for each of the tunable axes
    """
    yield from bps.null()

    d_stage.x.tuner.width = 11
    d_stage.x.tuner.width = 11

    if monochromator.dcm.energy.position < 10.99:  # ~ 10 keV for Si 220 crystals
        m_stage.r.tuner.width = 0.005
        a_stage.r.tuner.width = 0.003
        m_stage.r2p.tuner.width = 10
        a_stage.r2p.tuner.width = 7
        ms_stage.rp.tuner.width = 5
        as_stage.rp.tuner.width = 3
        minstep = user_override.pick("usaxs_minstep", 0.000045)
        logger.info("Setting minstep to %s", minstep)
        yield from bps.mv(terms.USAXS.usaxs_minstep, minstep)

    elif 10.99 <= monochromator.dcm.energy.position < 12.99:   # Si 220 crystals
        m_stage.r.tuner.width = 0.005
        a_stage.r.tuner.width = 0.0025
        m_stage.r2p.tuner.width = 9
        a_stage.r2p.tuner.width = 5
        ms_stage.rp.tuner.width = 3
        as_stage.rp.tuner.width = 3
        minstep = user_override.pick("usaxs_minstep", 0.000035)
        logger.info("Setting minstep to %s", minstep)
        yield from bps.mv(terms.USAXS.usaxs_minstep, minstep)

    elif 12.99 <= monochromator.dcm.energy.position < 18.1:   # Si 220 crystals
        m_stage.r.tuner.width = 0.005
        a_stage.r.tuner.width = 0.0022
        m_stage.r2p.tuner.width = 8
        a_stage.r2p.tuner.width = 5
        ms_stage.rp.tuner.width = 3
        as_stage.rp.tuner.width = 3
        minstep = user_override.pick("usaxs_minstep", 0.000025)
        logger.info("Setting minstep to %s", minstep)
        yield from bps.mv(terms.USAXS.usaxs_minstep, minstep)

    elif 18.1 <= monochromator.dcm.energy.position < 20.8:   # Si 220 crystals
        m_stage.r.tuner.width = 0.005
        a_stage.r.tuner.width = 0.002
        m_stage.r2p.tuner.width = 8
        a_stage.r2p.tuner.width = 6
        ms_stage.rp.tuner.width = 3
        as_stage.rp.tuner.width = 3
        minstep = user_override.pick("usaxs_minstep", 0.000025)
        logger.info("Setting minstep to %s", minstep)
        yield from bps.mv(terms.USAXS.usaxs_minstep, minstep)

    elif 20.8 <= monochromator.dcm.energy.position:   # Si 220 or 440 crystals
        if 11 <= m_stage.r.user_readback.value :
            #Si 440 crystals
            m_stage.r.tuner.width = 0.005
            a_stage.r.tuner.width = 0.0006
            m_stage.r2p.tuner.width = 8
            a_stage.r2p.tuner.width = 1.5
            ms_stage.rp.tuner.width = 3
            as_stage.rp.tuner.width = 3
            minstep = user_override.pick("usaxs_minstep", 0.000006)
            logger.info("Setting minstep to %s", minstep)
            yield from bps.mv(terms.USAXS.usaxs_minstep, minstep)

        else:
            #Si 220 crystals
            m_stage.r.tuner.width = 0.005
            a_stage.r.tuner.width = 0.0018
            m_stage.r2p.tuner.width = 8
            a_stage.r2p.tuner.width = 5
            ms_stage.rp.tuner.width = 3
            as_stage.rp.tuner.width = 3
            minstep = user_override.pick("usaxs_minstep", 0.00002)
            logger.info("Setting minstep to %s", minstep)
            yield from bps.mv(terms.USAXS.usaxs_minstep, minstep)


def update_EPICS_tuning_widths():
    """
    plan: update the tuning widths in EPICS PVs from local settings
    """
    yield from bps.mv(
        axis_tune_range.mr,     m_stage.r.tuner.width,
        axis_tune_range.ar,     a_stage.r.tuner.width,
        axis_tune_range.m2rp,   m_stage.r2p.tuner.width,
        axis_tune_range.a2rp,   a_stage.r2p.tuner.width,
        axis_tune_range.msrp,   ms_stage.rp.tuner.width,
        axis_tune_range.asrp,   as_stage.rp.tuner.width,
        axis_tune_range.dx,     d_stage.x.tuner.width,
        axis_tune_range.dy,     d_stage.y.tuner.width,
        )


def user_defined_settings():
    """
    plan: users may redefine this function to override any instrument defaults

    This is called from beforePlan() (in 50-plans.py) at the start of
    every batch set of measurements.  Among the many things a user might
    override could be the default ranges for tuning various optical axes.
    Such as::

        a_stage.r.tuner.width = 0.01

    NOTE:  Don't use blocking calls here

        It is important that the user not use any blocking calls
        such as setting or getting PVs in EPICS.  Blocking calls
        will *block* the python interpreter for long periods
        (such as ``time.sleep()``) or make direct calls
        for EPICS or file I/O that interrupt how the Bluesky
        RunEngine operates.

        It is OK to set local python variables since these do not block.

        Write this routine like any other bluesky plan code,
        using ``yield from bps.mv(...)``,  ``yield from bps.sleep(...)``, ...
    """
    yield from bps.null()
