print(__file__)

"""
detectors, amplifiers, and related support

========  =================  ====================  ===================  ===========
detector  scaler             amplifier             sequence             Femto model
========  =================  ====================  ===================  ===========
UPD       9idcLAX:vsc:c0.S4  9idcLAX:fem01:seq01:  9idcLAX:pd01:seq01:  DLPCA200
UPD       9idcLAX:vsc:c0.S4  9idcLAX:fem09:seq02:  9idcLAX:pd01:seq02:  DDPCA300
I0        9idcLAX:vsc:c0.S2  9idcRIO:fem02:seq01:  9idcLAX:pd02:seq01:
I00       9idcLAX:vsc:c0.S3  9idcRIO:fem03:seq01:  9idcLAX:pd03:seq01:
I000      9idcLAX:vsc:c0.S6  9idcRIO:fem04:seq01:  None
TRD       9idcLAX:vsc:c0.S5  9idcRIO:fem05:seq01:  9idcLAX:pd05:seq01:
========  =================  ====================  ===================  ===========

A PV (``9idcLAX:femto:model``) tells which UPD amplifier and sequence 
programs we're using now.  This PV is read-only since it is set when 
IOC boots, based on a soft link that configures the IOC.  The soft 
link may be changed using the ``use200pd``  or  ``use300pd`` script.

We only need to get this once, get it via one-time call with PyEpics
and then use it with inline dictionaries use_EPICS_scaler_channels(scaler0)to pick the right PVs.
"""


logger = logging.getLogger(os.path.split(__file__)[-1])


NUM_AUTORANGE_GAINS = 5     # common to all autorange sequence programs
AMPLIFIER_MINIMUM_SETTLING_TIME = 0.01    # reasonable?


def _gain_to_str_(gain):    # convenience function
    return ("%.0e" % gain).replace("+", "").replace("e0", "e")


class AutorangeSettings(object):
    """values allowed for sequence program's ``reqrange`` PV"""
    automatic = "automatic"
    auto_background = "auto+background"
    manual = "manual"


class CurrentAmplifierDevice(Device):
    gain = Component(EpicsSignalRO, "gain")


class FemtoAmplifierDevice(CurrentAmplifierDevice):
    gainindex = Component(EpicsSignal, "gainidx")
    description = Component(EpicsSignal, "femtodesc")
    
    # gain settling time for the device is <150ms
    settling_time = Component(Signal, value=0.08)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._gain_info_known = False
        self.num_gains = 0
        self.acceptable_gain_values = ()
        
    def __init_gains__(self, enum_strs):
        """
        learn range (gain) values from EPICS database
        
        provide a list of acceptable gain values for later use
        """
        acceptable = [s for s in enum_strs if s != 'UNDEF']
        num_gains = len(acceptable)
        # assume labels are ALWAYS formatted: "{float} V/A"
        acceptable += [float(s.split()[0]) for s in acceptable]
        acceptable += range(num_gains)
        self.num_gains = num_gains
        self.acceptable_range_values = acceptable

        # assume gain labels are formatted "{float} {other_text}"
        s = acceptable[0]
        self.gain_suffix = s[s.find(" "):]
        for i, s in enumerate(acceptable[:num_gains]):
            # verify all gains use same suffix text
            msg = "gainindex[{}] = {}, expected ending '{}'".format(i, s, self.gain_suffix)
            assert s[s.find(" "):] == self.gain_suffix
        
        self._gain_info_known = True

    def setGain(self, target):
        """
        set the gain on the amplifier
        
        Since the gain values are available from EPICS, 
        we use that to provide a method that can set the 
        gain by any of these values:
        
        * gain text value (from EPICS)
        * integer index number
        * desired gain floating-point value
        
        Assumptions:
        
        * gain label (from EPICS) is ALWAYS: "{float} V/A"
        * float mantissa is always one digit
        """
        if not self._gain_info_known:
            self.__init_gains__(self.gainindex.enum_strs)
        if target in self.acceptable_gain_values:
            if isinstance(target, (int, float)) and target > self.num_gains:
                # gain value specified, rewrite as str
                # assume mantissa is only 1 digit
                target = _gain_to_str_(target) + self.gain_suffix
            self.gainindex.put(target)
        else:
            msg = "could not set gain to {}, ".format(target)
            msg += "must be one of these: {}".format(self.acceptable_gain_values)
            raise ValueError(msg)


class AmplfierGainDevice(Device):
    _default_configuration_attrs = ()
    _default_read_attrs = ('gain', 'background', 'background_error')

    gain = FormattedComponent(EpicsSignal, '{self.prefix}gain{self._ch_num}')
    background = FormattedComponent(EpicsSignal, '{self.prefix}bkg{self._ch_num}')
    background_error = FormattedComponent(EpicsSignal, '{self.prefix}bkgErr{self._ch_num}')

    def __init__(self, prefix, ch_num=None, **kwargs):
        assert ch_num is not None, "Must provide `ch_num=` keyword argument."
        self._ch_num = ch_num
        super().__init__(prefix, **kwargs)


def _gains_subgroup_(cls, nm, gains, **kwargs):
    """internal: used in AmplifierAutoDevice"""
    defn = OrderedDict()
    for i in gains:
        key = '{}{}'.format(nm, i)
        defn[key] = (cls, '', dict(ch_num=i))

    return defn


class AmplifierAutoDevice(CurrentAmplifierDevice):
    """
    Ophyd support for amplifier sequence program
    """
    reqrange = Component(EpicsSignal, "reqrange")
    mode = Component(EpicsSignal, "mode")
    selected = Component(EpicsSignal, "selected")
    gainU = Component(EpicsSignal, "gainU")
    gainD = Component(EpicsSignal, "gainD")
    ranges = DynamicDeviceComponent(
        _gains_subgroup_(
            AmplfierGainDevice, 'gain', range(NUM_AUTORANGE_GAINS)))
    counts_per_volt = Component(EpicsSignal, "vfc")
    status = Component(EpicsSignalRO, "updating")
    lurange = Component(EpicsSignalRO, "lurange")
    lucounts = Component(EpicsSignalRO, "lucounts")
    lurate = Component(EpicsSignalRO, "lurate")
    lucurrent = Component(EpicsSignalRO, "lucurrent")
    updating = Component(EpicsSignalRO, "updating")
    
    max_count_rate = Component(Signal, value=950000)

    def __init__(self, prefix, **kwargs):
        self.scaler = None
        super().__init__(prefix, **kwargs)

        self._gain_info_known = False
        self.num_gains = 0
        self.acceptable_gain_values = ()

    def __init_gains__(self, enum_strs):
        """
        learn range (gain) values from EPICS database
        
        provide a list of acceptable gain values for later use
        """
        acceptable = list(enum_strs)
        num_gains = len(acceptable)
        # assume labels are ALWAYS formatted: "{float} V/A"
        acceptable += [float(s.split()[0]) for s in acceptable]
        acceptable += range(num_gains)
        self.num_gains = num_gains
        self.acceptable_gain_values = acceptable
        
        # assume gain labels are formatted "{float} {other_text}"
        s = acceptable[0]
        self.gain_suffix = s[s.find(" "):]
        for i, s in enumerate(acceptable[:num_gains]):
            # verify all gains use same suffix text
            msg = "reqrange[{}] = {}, expected ending: '{}'".format(i, s, self.gain_suffix)
            assert s[s.find(" "):] == self.gain_suffix
        
        self._gain_info_known = True

    def setAutoMode(self):
        """use "automatic" operations mode"""
        self.mode.put(AutorangeSettings.automatic)

    def setBAutoMode(self):
        """use "auto+background" operations mode"""
        self.mode.put(AutorangeSettings.auto_background)

    def setManualMode(self):
        """use "manual" operations mode"""
        self.mode.put(AutorangeSettings.manual)

    def setGain(self, target):
        """
        request the gain on the autorange controls
        
        Since the gain values are available from EPICS, 
        we use that to provide a method that can request the 
        gain by any of these values:
        
        * gain text value (from EPICS)
        * integer index number
        * desired gain floating-point value
        
        Assumptions:
        
        * gain label (from EPICS) is ALWAYS: "{float} {self.gain_suffix}"
        * float mantissa is always one digit
        """
        if not self._gain_info_known:
            self.__init_gains__(self.reqrange.enum_strs)
        if target in self.acceptable_gain_values:
            if isinstance(target, (int, float)) and target > self.num_gains:
                # gain value specified, rewrite as str
                # assume mantissa is only 1 digit
                target = _gain_to_str_(target) + self.gain_suffix
            if isinstance(target, str) and str(target) in self.reqrange.enum_strs:
                # must set reqrange by index number, rewrite as int
                target = self.reqrange.enum_strs.index(target)
            self.reqrange.put(target)
        else:
            msg = "could not set gain to {}, ".format(target)
            msg += "must be one of these: {}".format(self.acceptable_gain_values)
            raise ValueError(msg)

    @property
    def isUpdating(self):
        v = self.mode.value in (1, AutorangeSettings.auto_background)
        if v:
            v = self.updating.value in (1, "Updating")
        return v


class DetectorAmplifierAutorangeDevice(Device):
    """
    Coordinate the different objects that control a diode or ion chamber
    
    This is a convenience intended to simplify tasks such
    as measuring simultaneously the backgrounds of all channels.
    """

    def __init__(self, nickname, scaler, signal, amplifier, auto, **kwargs):
        assert isinstance(nickname, str)
        assert isinstance(scaler, (EpicsScaler, ScalerCH))
        assert isinstance(signal, EpicsSignalRO)
        assert isinstance(amplifier, FemtoAmplifierDevice)
        assert isinstance(auto, AmplifierAutoDevice)
        self.nickname = nickname
        self.scaler = scaler
        self.signal = signal
        self.femto = amplifier
        self.auto = auto
        super().__init__("", **kwargs)


def group_controls_by_scaler(controls):
    """
    return dictionary of [controls] keyed by common scaler support
    
    controls [obj]
        list (or tuple) of ``DetectorAmplifierAutorangeDevice``
    """
    assert isinstance(controls, (tuple, list)), "controls must be a list"
    scaler_dict = OrderedDefaultDict(list)    # sort the list of controls by scaler
    for i, control in enumerate(controls):
        # each item in list MUST be instance of DetectorAmplifierAutorangeDevice
        msg = "controls[{}] must be".format(i)
        msg += " instance of 'DetectorAmplifierAutorangeDevice'"
        msg += ", provided: {}".format(control)
        assert isinstance(control, DetectorAmplifierAutorangeDevice), msg

        k = control.scaler.name       # key by scaler's ophyd device name
        scaler_dict[k].append(control)  # group controls by scaler
    return scaler_dict


def _scaler_background_measurement_(control_list, count_time=1.0, num_readings=8):
    """internal, blocking: measure amplifier backgrounds for signals sharing a common scaler"""
    scaler = control_list[0].scaler
    signals = [c.signal for c in control_list]
    
    stage_sigs = {}
    stage_sigs["scaler"] = scaler.stage_sigs
    scaler.stage_sigs["preset_time"] = count_time

    for control in control_list:
        control.auto.setManualMode()

    for n in range(NUM_AUTORANGE_GAINS-1, 0, -1):  # reverse order
        # set gains
        settling_time = AMPLIFIER_MINIMUM_SETTLING_TIME
        for control in control_list:
            control.auto.setGain(n)
            settling_time = max(settling_time, control.femto.settling_time.value)
        time.sleep(settling_time)

        readings = {s.pvname: [] for s in signals}
        
        for m in range(num_readings):
            # count and wait to complete
            counting = scaler.trigger()
            ophyd.status.wait(counting, timeout=count_time+1.0)
            
            for s in signals:
                readings[s.pvname].append(s.value)
    
        s_range_name = "gain{}".format(n)
        for control in control_list:
            g = control.auto.ranges.__getattr__(s_range_name)
            g.background.put(np.mean(readings[control.signal.pvname]))
            g.background_error.put(np.std(readings[control.signal.pvname]))
            msg = "{} range={} gain={}  bkg={}  +/- {}".format(
                control.nickname, 
                n,
                _gain_to_str_(control.auto.gain.value), 
                g.background.value, 
                g.background_error.value)
            logger.info(msg)

    scaler.stage_sigs = stage_sigs["scaler"]


def measure_background(controls, shutter=None, count_time=1.0, num_readings=8):
    """
    interactive function to measure detector backgrounds simultaneously
    
    controls [obj]
        list (or tuple) of ``DetectorAmplifierAutorangeDevice``
    """
    assert isinstance(controls, (tuple, list)), "controls must be a list"
    scaler_dict = group_controls_by_scaler(controls)
    
    if shutter is not None:
        shutter.close()

    for control_list in scaler_dict.values():
        # do these in sequence, just in case same hardware used multiple times
        if len(control_list) > 0:
            msg = "Measuring background for: " + control_list[0].nickname
            logger.info(msg)
            _scaler_background_measurement_(control_list, count_time, num_readings)


_last_autorange_gain_ = OrderedDefaultDict(dict)

def _scaler_autoscale_(controls, count_time=1.0, max_iterations=9):
    """internal, blocking: autoscale amplifiers for signals sharing a common scaler"""
    global _last_autorange_gain_

    scaler = controls[0].scaler
    stage_sigs = {}
    stage_sigs["scaler"] = scaler.stage_sigs

    scaler.stage_sigs["preset_time"] = count_time
    scaler.stage_sigs["delay"] = 0.02
    scaler.stage_sigs["count_mode"] = "OneShot"

    last_gain_dict = _last_autorange_gain_[scaler.name]

    settling_time = AMPLIFIER_MINIMUM_SETTLING_TIME
    for control in controls:
        control.auto.setBAutoMode()
        # faster if we start from last known autoscale gain
        gain = last_gain_dict.get(control.auto.gain.name)
        if gain is not None:    # be cautious, might be unknown
            control.auto.reqrange.put(gain)
        last_gain_dict[control.auto.gain.name] = control.auto.gain.value
        settling_time = max(settling_time, control.femto.settling_time.value)
    
    time.sleep(settling_time)

    # How many times to let autoscale work?
    # Number of possible gains is one choice - NUM_AUTORANGE_GAINS
    # consider: could start on one extreme, end on the other
    max_iterations = min(max_iterations, NUM_AUTORANGE_GAINS)

    # Better to let caller set a higher possible number
    # Converge if no gains change
    # Also, make sure no detector count rates are stuck at max
    
    for iteration in range(max_iterations):
        converged = []      # append True is convergence criteria is satisfied
        counting = scaler.trigger()    # start counting
        ophyd.status.wait(counting, timeout=count_time+1.0)
        # amplifier sequence program (in IOC) will adjust the gain now
        
        for control in controls:
            # any gains changed?
            gain_now = control.auto.gain.value
            gain_previous = last_gain_dict[control.auto.gain.name]
            converged.append(gain_now == gain_previous)
            last_gain_dict[control.auto.gain.name] = gain_now
        
            # are we topped up on any detector?
            max_rate = control.auto.max_count_rate.value
            actual_rate = control.signal.value
            converged.append(actual_rate <= max_rate)
        
        if False not in converged:      # all True?
            complete = True
            break   # no changes
        logger.debug("converged: {}".format(converged))

    scaler.stage_sigs = stage_sigs["scaler"]

    if not complete:        # bailed out early from loop
        fmt = "FAILED TO FIND CORRECT GAIN IN {} AUTOSCALE ITERATIONS"
        raise RuntimeError(fmt.format(max_iterations))


def autoscale_amplifiers(controls, shutter=None, count_time=1.0, max_iterations=9):
    """
    interactive function to autoscale detector amplifiers simultaneously
    
    controls [obj]
        list (or tuple) of ``DetectorAmplifierAutorangeDevice``
    """
    assert isinstance(controls, (tuple, list)), "controls must be a list"
    scaler_dict = group_controls_by_scaler(controls)
    
    if shutter is not None:
        shutter.open()

    for control_list in scaler_dict.values():
        # do these in sequence, just in case same hardware used multiple times
        if len(control_list) > 0:
            msg = "Autoscaling amplifier for: " + control_list[0].nickname
            logger.info(msg)
            _scaler_autoscale_(
                control_list, 
                count_time=count_time, 
                max_iterations=max_iterations)


# ------------

_amplifier_id_upd = epics.caget("9idcLAX:femto:model", as_string=True)

if _amplifier_id_upd == "DLCPA200":
    _upd_femto_prefix = "9idcLAX:fem01:seq01:"
    _upd_auto_prefix  = "9idcLAX:pd01:seq01:"
elif _amplifier_id_upd == "DDPCA300":
    _upd_femto_prefix = "9idcLAX:fem09:seq02:"
    _upd_auto_prefix  = "9idcLAX:pd01:seq02:"

upd_femto_amplifier  = FemtoAmplifierDevice(_upd_femto_prefix, name="upd_femto_amplifier")
trd_femto_amplifier  = FemtoAmplifierDevice("9idcRIO:fem05:seq01:", name="trd_femto_amplifier")
I0_femto_amplifier   = FemtoAmplifierDevice("9idcRIO:fem02:seq01:", name="I0_femto_amplifier")
I00_femto_amplifier  = FemtoAmplifierDevice("9idcRIO:fem03:seq01:", name="I00_femto_amplifier")
I000_femto_amplifier = FemtoAmplifierDevice("9idcRIO:fem04:seq01:", name="I000_femto_amplifier")

upd_autorange_controls = AmplifierAutoDevice(_upd_auto_prefix, name="upd_autorange_controls")
trd_autorange_controls = AmplifierAutoDevice("9idcLAX:pd05:seq01:", name="trd_autorange_controls")
I0_autorange_controls = AmplifierAutoDevice("9idcLAX:pd02:seq01:", name="I0_autorange_controls")
I00_autorange_controls = AmplifierAutoDevice("9idcLAX:pd03:seq01:", name="I00_autorange_controls")

upd_controls = DetectorAmplifierAutorangeDevice(
    "PD_USAXS",
    scaler0,
    UPD_SIGNAL,
    upd_femto_amplifier,
    upd_autorange_controls,
    name="upd_controls",
)

trd_controls = DetectorAmplifierAutorangeDevice(
    "TR diode",
    scaler0,
    TRD_SIGNAL,
    trd_femto_amplifier,
    trd_autorange_controls,
    name="trd_controls",
)

I0_controls = DetectorAmplifierAutorangeDevice(
    "I0_USAXS",
    scaler0,
    I0_SIGNAL,
    I0_femto_amplifier,
    I0_autorange_controls,
    name="I0_controls",
)

I00_controls = DetectorAmplifierAutorangeDevice(
    "I0_USAXS",
    scaler0,
    I00_SIGNAL,
    I00_femto_amplifier,
    I00_autorange_controls,
    name="I00_controls",
)

controls_list_I0_I00_TRD = [I0_controls, I00_controls, trd_controls]
controls_list_UPD_I0_I00_TRD = [upd_controls] + controls_list_I0_I00_TRD