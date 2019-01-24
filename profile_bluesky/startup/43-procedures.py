print(__file__)

"""
USAXS mode change procedures

see: https://subversion.xray.aps.anl.gov/spec/beamlines/USAXS/trunk/macros/local/usaxs_commands.mac
"""


logger = logging.getLogger(os.path.split(__file__)[-1])


def DCMfeedbackON():
    """plan: could send email"""
    yield from bps.mv(monochromator.feedback.on, 1)
    monochromator.feedback.check_position()


def insertScanFilters():
    """plan: insert the EPICS-specified filters"""
    yield from bps.mv(
        pf4_AlTi.fPosA, terms.USAXS.scan_filters.Al.value,    # Bank A: Al
        pf4_AlTi.fPosB, terms.USAXS.scan_filters.Ti.value,    # Bank B: Ti
    )


def confirm_instrument_mode(mode_name):
    """
    True if instrument is in the named mode
    
    Parameter
    
    mode_name (str) :
        One of the strings defined in ``UsaxsSaxsModes``
    """
    expected_mode = UsaxsSaxsModes[mode_name]
    return terms.SAXS.UsaxsSaxsMode.value == expected_mode


def mode_USAXS():
    # plc_protect.stop_if_tripped()
    yield from user_data.set_state_plan("Moving USAXS to USAXS mode")
    yield from bps.mv(
        ccd_shutter,        "close",
        ti_filter_shutter,  "close",
    )
    yield from DCMfeedbackON() 
    retune_needed = False

    if not confirm_instrument_mode("USAXS in beam"):
        mode_now = terms.SAXS.UsaxsSaxsMode.get(as_string=True)
        logger.info("Found UsaxsSaxsMode = {}".format(mode_now))
        logger.info("Moving to proper USAXS mode")
        yield from move_WAXSOut()
        yield from move_SAXSOut()
        yield from move_USAXSIn()
        retune_needed = True

    logger.info("Preparing for USAXS mode ... please wait ...")
    yield from bps.mv(
        # set scalar to autocount mode for USAXS
        scaler0, SCALER_AUTOCOUNT_MODE,

        # put detector stage in position
        # TODO: redundant with move_USAXSIn() above?
        d_stage.x, terms.USAXS.diode.dx.value,
        d_stage.y, terms.USAXS.diode.dy.value,
    )
    yield from bps.sleep(0.1)   # TODO: still needed?

    if not ccd_shutter.is_closed:
        logger.info("!!!CCD shutter failed to close!!!")
        # TODO: logging?
    else:
        # mono_shutter.open()

        # print("Change TV input selector to show image in hutch")
        # print("Turn off BLUE switch on CCD controller")
        yield from insertScanFilters()
        yield from bps.mv(ccd_shutter, "close")

        logger.info("Prepared for USAXS mode")
        yield from user_data.set_state_plan("USAXS Mode")
        ts = str(datetime.datetime.now())
        yield from bps.mv(
            user_data.time_stamp, ts,
            user_data.macro_file_time, ts,
            user_data.scanning, 0,
        )

    if retune_needed:
        # don't tune here
        # Instead, set a signal to be caught by the plan in the RunEngine
        yield from bps.mv(terms.USAXS.retune_needed, True)


def mode_SBUSAXS():
    pass


def mode_SAXS():
    # plc_protect.stop_if_tripped()
    yield from user_data.set_state_plan("Moving USAXS to SAXS mode")
    yield from bps.mv(
        ccd_shutter,        "close",
        ti_filter_shutter,  "close",
    )

    if not confirm_instrument_mode("SAXS in beam"):
        mode_now = terms.SAXS.UsaxsSaxsMode.get(as_string=True)
        logger.info("Found UsaxsSaxsMode = {}".format(mode_now))
        logger.info("Moving to proper SAXS mode")
        yield from move_WAXSOut()
        yield from move_USAXSOut()
        yield from move_SAXSIn()
        
    logger.info("Prepared for SAXS mode")
    #insertScanFilters
    yield from user_data.set_state_plan("SAXS Mode")
    ts = str(datetime.datetime.now())
    yield from bps.mv(
        user_data.time_stamp, ts,
        user_data.macro_file_time, ts,
        user_data.scanning, 0,
    )


def mode_WAXS():
    # plc_protect.stop_if_tripped()
    yield from user_data.set_state_plan("Moving USAXS to WAXS mode")
    yield from bps.mv(
        ccd_shutter,        "close",
        ti_filter_shutter,  "close",
    )

    if confirm_instrument_mode("WAXS in beam"):
        logger.debug("WAXS is in beam")
    else:
        mode_now = terms.SAXS.UsaxsSaxsMode.get(as_string=True)
        logger.info("Found UsaxsSaxsMode = {}".format(mode_now))
        logger.info("Moving to proper WAXS mode")
        yield from move_SAXSOut()
        yield from move_USAXSOut()
        yield from move_WAXSIn()

    # move SAXS slits in, used for WAXS mode also
    v_diff = abs(guard_slit.v_size.value - terms.SAXS.guard_v_size.value)
    h_diff = abs(guard_slit.h_size.value - terms.SAXS.guard_h_size.value)
    logger.debug("guard slits horizontal difference = %g" % h_diff)
    logger.debug("guard slits vertical difference = %g" % v_diff)

    if max(v_diff, h_diff) > 0.03:
        logger.info("changing Guard slits")
        yield from bps.mv(
            guard_slit.h_size, terms.SAXS.guard_h_size.value,
            guard_slit.v_size, terms.SAXS.guard_v_size.value,
        )
        yield from bps.sleep(0.5)           # FIXME: needed now?
        # while max(v_diff, h_diff) > 0.02:   # FIXME: What good is this loop?
        #     logger.debug("waiting for guard slits to finish their move")
        #     yield from bps.sleep(0.5)
        #     v_diff = abs((guard_slit.top.position  - guard_slit.bot.position) - terms.SAXS.guard_v_size.value)
        #     h_diff = abs((guard_slit.outb.position - guard_slit.inb.position) - terms.SAXS.guard_h_size.value)
        #     logger.debug("guard slits horizontal difference = %g" % h_diff)
        #     logger.debug("guard slits vertical difference = %g" % v_diff)

    v_diff = abs(usaxs_slit.v_size.position - terms.SAXS.v_size.value)
    h_diff = abs(usaxs_slit.h_size.position - terms.SAXS.h_size.value)
    logger.debug("USAXS slits horizontal difference = %g" % h_diff)
    logger.debug("USAXS slits vertical difference = %g" % v_diff)

    if max(v_diff, h_diff) > 0.02:
       logger.info("Moving Beam defining slits")
       yield from bps.mv(
           usaxs_slit.h_size, terms.SAXS.h_size.value,
           usaxs_slit.v_size, terms.SAXS.v_size.value,
       )
       yield from bps.sleep(2)     # wait for backlash, seems these motors are slow and spec gets ahead of them?

    logger.info("Prepared for WAXS mode")
    #insertScanFilters
    yield from user_data.set_state_plan("WAXS Mode")
    ts = str(datetime.datetime.now())
    yield from bps.mv(
        user_data.time_stamp, ts,
        user_data.macro_file_time, ts,
        user_data.scanning, 0,
    )


def mode_radiography():
    pass


def mode_imaging():
    pass


def mode_pinSAXS():
    pass


def mode_OpenBeamPath():
    # plc_protect.stop_if_tripped()
    yield from user_data.set_state_plan("Moving USAXS to OpenBeamPath mode")
    yield from bps.mv(
        ccd_shutter,        "close",
        ti_filter_shutter,  "close",
    )

    if not confirm_instrument_mode("out of beam"):
        mode_now = terms.SAXS.UsaxsSaxsMode.get(as_string=True)
        logger.info("Found UsaxsSaxsMode = {}".format(mode_now))
        logger.info("Opening the beam path, moving all components out")
        yield from move_SAXSOut()
        yield from move_WAXSOut()
        yield from move_USAXSOut()
        yield from user_data.set_state_plan("USAXS moved to OpenBeamPath mode")
