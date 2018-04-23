print(__file__)

"""other signals"""

aps_current = EpicsSignalRO("S:SRcurrentAI", name="aps_current")

FE_shutter = MyApsPssShutter("9ida:rShtrA", name="FE_shutter")
mono_shutter = MyApsPssShutter("9ida:rShtrB", name="mono_shutter")
usaxs_shutter = InOutShutter("9idb:BioEnc2B3", name="usaxs_shutter")
ccd_shutter = InOutShutter("9idcRIO:Galil2Bo0_CMD", name="ccd_shutter")

mono_energy = EpicsSignal('9ida:BraggERdbkAO', name='mono_energy', write_pv="9ida:BraggEAO")
und_us_energy = EpicsSignal('ID09us:Energy', name='und_us_energy', write_pv="ID09us:EnergySet")
und_ds_energy = EpicsSignal('ID09ds:Energy', name='und_ds_energy', write_pv="ID09ds:EnergySet")


userCalcs_lax = userCalcsDevice("9idcLAX:", name="userCalcs_lax")

usaxs_q_calc = swaitRecord("9idcLAX:USAXS:Q", name="usaxs_q_calc")
usaxs_q = usaxs_q_calc.val

mr_val_center = EpicsSignal("9idcLAX:USAXS:MRcenter", name="mr_val_center")
msr_val_center = EpicsSignal("9idcLAX:USAXS:MSRcenter", name="msr_val_center")
ar_val_center = EpicsSignal("9idcLAX:USAXS:ARcenter", name="ar_val_center")
asr_val_center = EpicsSignal("9idcLAX:USAXS:ASRcenter", name="asr_val_center")
