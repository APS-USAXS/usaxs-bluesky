print(__file__)

"""more signals"""
# TODO: eventually merge with 21-signals.py

# these are the global settings PVs for various parts of the instrument

# NOTE: avoid using any PV more than once!

"""
from: https://subversion.xray.aps.anl.gov/spec/beamlines/USAXS/trunk/macros/local/usaxs_commands.mac



#And these functions make the pinhole globals work...

	PIN_ZIn		9idcLAX:USAXS_Pin:Pin_z_in	
	PIN_ZOut		9idcLAX:USAXS_Pin:Pin_z_out	
	PIN_ZLimOffset		9idcLAX:USAXS_Pin:Pin_z_limit_offset	
	PIN_YIn		9idcLAX:USAXS_Pin:Pin_y_in	
	PIN_YOut		9idcLAX:USAXS_Pin:Pin_y_out	
	PIN_YLimOffset		9idcLAX:USAXS_Pin:Pin_y_limit_offset	
	AX_In		9idcLAX:USAXS_Pin:ax_in	
	AX_Out		9idcLAX:USAXS_Pin:ax_out	
	AX_LimOffset		9idcLAX:USAXS_Pin:ax_limit_offset	
	DX_In		9idcLAX:USAXS:Diode_dx	
	DX_Out		9idcLAX:USAXS_Pin:dx_out	
	DX_LimOffset		9idcLAX:USAXS_Pin:dx_limit_offset	
	USAXS_HSlit		9idcLAX:USAXS_Pin:USAXS_hslit_ap	
	USAXS_VSlit		9idcLAX:USAXS_Pin:USAXS_vslit_ap	
	SAXS_VSlit 		9idcLAX:USAXS_Pin:Pin_vslit_ap	
	SAXS_HSlit		9idcLAX:USAXS_Pin:Pin_hslit_ap	

	USAXS_HGSlit		9idcLAX:USAXS_Pin:USAXS_hgslit_ap	
	USAXS_VGSlit		9idcLAX:USAXS_Pin:USAXS_vgslit_ap	
	SAXS_VGSlit 		9idcLAX:USAXS_Pin:Pin_vgslit_ap	
	SAXS_HGSlit		9idcLAX:USAXS_Pin:Pin_hgslit_ap	


	PIN_AL_FILTER		9idcLAX:USAXS_Pin:Exp_Al_Filter	
	PIN_TI_FILTER		9idcLAX:USAXS_Pin:Exp_Ti_Filter	

	PIN_TRPD		9idcLAX:USAXS_Pin:Pin_TrPD	
	PIN_TRI0		9idcLAX:USAXS_Pin:Pin_TrI0	
	PIN_TRPDGain		9idcLAX:USAXS_Pin:Pin_TrPDgain	
	PIN_TRI0Gain		9idcLAX:USAXS_Pin:Pin_TrI0gain	

	PIN_IMAGE_BASEDIR		9idcLAX:USAXS_Pin:directory	

	USAXSSAXSMODE		9idcLAX:USAXS_Pin:USAXSSAXSMode	
	PIN_NumImages		9idcLAX:USAXS_Pin:NumImages	
	PIN_AcquireTime		9idcLAX:USAXS_Pin:AcquireTime	
	PIN_EXP_TIME		9idcLAX:USAXS_Pin:AcquireTime	

	USAXS_MEASURE_PIN_TRANS		9idcLAX:USAXS:TR_MeasurePinTrans	             # measure transmission in USAXS using pin diode
	USAXSPinT_AyPosition		9idcLAX:USAXS:TR_AyPosition	      		# Ay to hit pin diode
	USAXSPinT_MeasurementTime		9idcLAX:USAXS:TR_MeasurementTime		        # How long to count
	USAXSPinT_pinCounts		9idcLAX:USAXS:TR_pinCounts			        # How many counts were on pin diode
	USAXSPinT_pinGain		9idcLAX:USAXS:TR_pinGain					# gain of pin diode (note, we are using I00 amplifier here)
	USAXSPinT_I0Counts		9idcLAX:USAXS:TR_I0Counts					# How many counts were on I0 
	USAXSPinT_I0Gain		9idcLAX:USAXS:TR_I0Gain					# gain of I0

	
# this is Io value from gates scalar in LAX for Nexus file
	PIN_I0		9idcLAX:USAXS_Pin:I0	
# WAXS
	WAXS_XIn		9idcLAX:USAXS_Pin:waxs_x_in	
	WAXS_Xout		9idcLAX:USAXS_Pin:waxs_x_out	
	WAXS_XLimOffset		9idcLAX:USAXS_Pin:waxs_x_limit_offset	
	WEXP_AL_FILTER		9idcLAX:USAXS_WAXS:Exp_Al_Filter	
	WEXP_TI_FILTER		9idcLAX:USAXS_WAXS:Exp_Ti_Filter	
	WAXS_IMAGE_BASEDIR		9idcLAX:USAXS_WAXS:directory	
	WAXS_NumImages		9idcLAX:USAXS_WAXS:NumImages	
	WAXS_AcquireTime		9idcLAX:USAXS_WAXS:AcquireTime	
	WAXS_EXP_TIME		9idcLAX:USAXS_WAXS:AcquireTime	

# USAXS Imaging
	UImg_ImageKey		9idcLAX:USAXS_Img:ImageKey	 
##  UImg_ImageKey: "0-image, 1-flat field, 2-dark field")
	UImg_ExposureTime		9idcLAX:USAXS_Img:ExposureTime	

	UImg_Tomo_Rot_Angle		9idcLAX:USAXS_Img:Tomo_Rot_Angle	
	UImg_Img_I0_value		9idcLAX:USAXS_Img:Img_I0_value	
	UImg_Img_I0_gain		9idcLAX:USAXS_Img:Img_I0_gain	

	UImg_AxPosition		9idcLAX:USAXS_Img:ax_in	
	UImg_WaxsXPosition		9idcLAX:USAXS_Img:waxs_x_in	

	UImg_FlatFieldImage		9idcLAX:USAXS_Img:FlatFieldImage	
	UImg_DarkFieldImage		9idcLAX:USAXS_Img:DarkFieldImage	
	UImg_ExperimentTitle		9idcLAX:USAXS_Img:ExperimentTitle	

	UImg_ImgHorApperture		9idcLAX:USAXS_Img:ImgHorApperture	 
	UImg_ImgVertApperture		9idcLAX:USAXS_Img:ImgVertApperture	 
	UImg_ImgGuardHorApperture		9idcLAX:USAXS_Img:ImgGuardHorApperture	 
	UImg_ImgGuardVertApperture		9idcLAX:USAXS_Img:ImgGuardVertApperture	 
	UImg_Img_Al_Filters		9idcLAX:USAXS_Img:Img_Al_Filters	
	UImg_Img_Ti_Filters		9idcLAX:USAXS_Img:Img_Ti_Filters	
	UImg_FilterTransmision	epics_get(9idcLAX:USAXS_Img:Img_FilterTransmission	


# set commands 

## USAXS Imaging set commands:
	set_UImg_ImageKey		9idcLAX:USAXS_Img:ImageKey	 
##  "0-image, 1-flat field, 2-dark field")
	set_UImg_ExposureTime		9idcLAX:USAXS_Img:ExposureTime	

	set_UImg_Tomo_Rot_Angle		9idcLAX:USAXS_Img:Tomo_Rot_Angle	
	set_UImg_Img_I0_value		9idcLAX:USAXS_Img:Img_I0_value	
	set_UImg_Img_I0_gain		9idcLAX:USAXS_Img:Img_I0_gain	

	set_UImg_AxPosition		9idcLAX:USAXS_Img:ax_in"v)'
	set_UImg_WaxsXPosition		9idcLAX:USAXS_Img:waxs_x_in	

	set_UImg_FlatFieldImage		9idcLAX:USAXS_Img:FlatFieldImage
	set_UImg_DarkFieldImage		9idcLAX:USAXS_Img:DarkFieldImage
	set_UImg_ExperimentTitle		9idcLAX:USAXS_Img:ExperimentTitle

	set_UImg_ImgHorApperture		9idcLAX:USAXS_Img:ImgHorApperture	 
	set_UImg_ImgVertApperture		9idcLAX:USAXS_Img:ImgVertApperture	 
	set_UImg_ImgVertApperture		9idcLAX:USAXS_Img:ImgVertApperture	 
	set_UImg_ImgGuardVertApperture		9idcLAX:USAXS_Img:ImgGuardVertApperture	 
	set_UImg_Img_Al_Filters		9idcLAX:USAXS_Img:Img_Al_Filters	
	set_UImg_Img_Ti_Filters		9idcLAX:USAXS_Img:Img_Ti_Filters	
	set_UImg_FilterTransmision		9idcLAX:USAXS_Img:Img_FilterTransmission	


## standard set commands... 

	set_PIN_ZIn		9idcLAX:USAXS_Pin:Pin_z_in	
	set_PIN_ZOut		9idcLAX:USAXS_Pin:Pin_z_out	
	set_PIN_ZLimOffset		9idcLAX:USAXS_Pin:Pin_z_limit_offset	
	set_PIN_YIn		9idcLAX:USAXS_Pin:Pin_y_in	
	set_PIN_YOut		9idcLAX:USAXS_Pin:Pin_y_out	
	set_PIN_YLimOffset		9idcLAX:USAXS_Pin:Pin_y_limit_offset	
	set_AX_In		9idcLAX:USAXS_Pin:ax_in	
	set_AX_Out		9idcLAX:USAXS_Pin:ax_out	
	set_AX_LimOffset		9idcLAX:USAXS_Pin:ax_limit_offset	
	set_DX_In		9idcLAX:USAXS:Diode_dx	
	set_DX_Out		9idcLAX:USAXS_Pin:dx_out	
	set_DX_LimOffset		9idcLAX:USAXS_Pin:dx_limit_offset	
	set_USAXS_HSlit		9idcLAX:USAXS_Pin:USAXS_hslit_ap	
	set_USAXS_VSlit		9idcLAX:USAXS_Pin:USAXS_vslit_ap	
	set_SAXS_VSlit 		9idcLAX:USAXS_Pin:Pin_vslit_ap	
	set_SAXS_HSlit		9idcLAX:USAXS_Pin:Pin_hslit_ap	

	set_USAXS_HGSlit		9idcLAX:USAXS_Pin:USAXS_hgslit_ap	
	set_USAXS_VGSlit		9idcLAX:USAXS_Pin:USAXS_vgslit_ap	
	set_SAXS_VGSlit 		9idcLAX:USAXS_Pin:Pin_vgslit_ap	
	set_SAXS_HGSlit		9idcLAX:USAXS_Pin:Pin_hgslit_ap	

	set_PIN_AL_FILTER		9idcLAX:USAXS_Pin:Exp_Al_Filter	
	set_PIN_TI_FILTER		9idcLAX:USAXS_Pin:Exp_Ti_Filter	
	set_PIN_NumImages		9idcLAX:USAXS_Pin:NumImages	

	set_PIN_AcquireTime		9idcLAX:USAXS_Pin:AcquireTime	
	set_PIN_EXP_TIME		9idcLAX:USAXS_Pin:AcquireTime	
	set_PIN_TRPD		9idcLAX:USAXS_Pin:Pin_TrPD	
	set_PIN_TRI0		9idcLAX:USAXS_Pin:Pin_TrI0	
	set_PIN_TRPDGain		9idcLAX:USAXS_Pin:Pin_TrPDgain	
	set_PIN_TRI0Gain		9idcLAX:USAXS_Pin:Pin_TrI0gain	

	set_PIN_IMAGE_BASEDIR		9idcLAX:USAXS_Pin:directory	


# WAXS
	set_WAXS_IMAGE_BASEDIR		9idcLAX:USAXS_WAXS:directory	

	set_WAXS_XIn		9idcLAX:USAXS_Pin:waxs_x_in	
	set_WAXS_Xout		9idcLAX:USAXS_Pin:waxs_x_out	
	set_WAXS_XLimOffset		9idcLAX:USAXS_Pin:waxs_x_limit_offset	
	set_WEXP_AL_FILTER		9idcLAX:USAXS_WAXS:Exp_Al_Filter	
	set_WEXP_TI_FILTER		9idcLAX:USAXS_WAXS:Exp_Ti_Filter	
	set_WAXS_AcquireTime		9idcLAX:USAXS_WAXS:AcquireTime	
	set_WAXS_EXP_TIME		9idcLAX:USAXS_WAXS:AcquireTime	
	set_WAXS_NumImages		9idcLAX:USAXS_WAXS:NumImages	

#transmission
 	set_USAXS_MEASURE_PIN_TRANS		9idcLAX:USAXS:TR_MeasurePinTrans	      # measure transmission in USAXS using pin diode
 	set_USAXSPinT_AyPosition		9idcLAX:USAXS:TR_AyPosition	      		 # Ay to hit pin diode
 	set_USAXSPinT_MeasurementTime		9idcLAX:USAXS:TR_MeasurementTime		# How long to count
 	set_USAXSPinT_pinCounts		9idcLAX:USAXS:TR_pinCounts				# How many counts were on pin diode
 	set_USAXSPinT_pinGain		9idcLAX:USAXS:TR_pinGain					# gain of pin diode (note, we are using I00 amplifier here)
 	set_USAXSPinT_I0Counts		9idcLAX:USAXS:TR_I0Counts				# How many counts were on I0
 	set_USAXSPinT_I0Gain		9idcLAX:USAXS:TR_I0Gain					# gain of I0
"""


# TODO: this belongs somewhere else, but where?
is2DUSAXSscan = EpicsSignal("9idcLAX:USAXS:is2DUSAXSscan", name="is2DUSAXSscan")


class FlyScanParameters(Device):
    """FlyScan values"""
    number_points = Component(EpicsSignal, "9idcLAX:USAXS:FS_NumberOfPoints")
    scan_time = Component(EpicsSignal, "9idcLAX:USAXS:FS_ScanTime")
    use_flyscan = Component(EpicsSignal, "9idcLAX:USAXS:UseFlyscan")
    asrp_calc_SCAN = Component(EpicsSignal, "9idcLAX:userStringCalc2.SCAN")
    order_number = Component(EpicsSignal, "9idcLAX:USAXS:FS_OrderNumber")
    
    def enable_ASRP(self):
        if is2DUSAXSscan.value: # TODO: check return value here
            self.asrp_calc_SCAN.put(9)
    
    def disable_ASRP(self):
        self.asrp_calc_SCAN.put(0)
    
    def increment_order_number(self):
        self.order_number.put(self.order_number.value+1)


class PreUsaxsTuneParameters(Device):
    """preUSAXStune handling"""
    num_scans_last_tune = Component(EpicsSignal, "9idcLAX:USAXS:NumScansFromLastTune")
    epoch_last_tune = Component(EpicsSignal, "9idcLAX:USAXS:EPOCHTimeOfLastTune")
    req_num_scans_between_tune = Component(EpicsSignal, "9idcLAX:USAXS:ReqNumScansBetweenTune")
    req_time_between_tune = Component(EpicsSignal, "9idcLAX:USAXS:ReqTimeBetweenTune")
    run_tune_on_qdo = Component(EpicsSignal, "9idcLAX:USAXS:RunPreUSAXStuneOnQdo")
    run_tune_next = Component(EpicsSignal, "9idcLAX:USAXS:RunPreUSAXStuneNext")


class GeneralParametersCCD(Device):
    "part of GeneralParameters Device"
    dx = Component(EpicsSignal, "dx")
    dy = Component(EpicsSignal, "dy")


class GeneralUsaxsParametersDiode(Device):
    "part of GeneralParameters Device"
    dx = Component(EpicsSignal, "Diode_dx")
    dy = Component(EpicsSignal, "DY0")


class GeneralUsaxsParametersCenters(Device):
    "part of GeneralParameters Device"
    AR = Component(EpicsSignal,  "ARcenter")
    ASR = Component(EpicsSignal, "ASRcenter")
    MR = Component(EpicsSignal,  "MRcenter")
    MSR = Component(EpicsSignal, "MSRcenter")


class GeneralUsaxsParametersFilters(Device):
    "part of GeneralParameters Device"
    Al = Component(EpicsSignal,  "Al_Filter")
    Ti = Component(EpicsSignal,  "Ti_Filter")


class GeneralUsaxsParameters(Device):
    """internal values shared with EPICS"""
    AY0 = Component(EpicsSignal,                      "9idcLAX:USAXS:AY0")
    DY0 = Component(EpicsSignal,                      "9idcLAX:USAXS:DY0")
    ASRP0 = Component(EpicsSignal,                    "9idcLAX:USAXS:ASRP0")
    SAD = Component(EpicsSignal,                      "9idcLAX:USAXS:SAD")
    SDD = Component(EpicsSignal,                      "9idcLAX:USAXS:SDD")
    center = Component(GeneralUsaxsParametersCenters,      "9idcLAX:USAXS:")
    ccd = Component(GeneralUsaxsParametersCCD,             "9idcLAX:USAXS:CCD_")
    diode = Component(GeneralUsaxsParametersDiode,         "9idcLAX:USAXS:")
    img_filter = Component(GeneralUsaxsParametersCenters,  "9idcLAX:USAXS:Img_")
    finish = Component(EpicsSignal,                   "9idcLAX:USAXS:Finish")
    motor_prescaler_wait = Component(EpicsSignal,     "9idcLAX:USAXS:Prescaler_Wait")
    num_points = Component(EpicsSignal,               "9idcLAX:USAXS:NumPoints")
    sample_y_step = Component(EpicsSignal,            "9idcLAX:USAXS:Sample_Y_Step")
    scan_filter = Component(GeneralUsaxsParametersCenters, "9idcLAX:USAXS:Scan_")
    start_offset = Component(EpicsSignal,             "9idcLAX:USAXS:StartOffset")
    uaterm = Component(EpicsSignal,                   "9idcLAX:USAXS:UATerm")
    usaxs_minstep = Component(EpicsSignal,            "9idcLAX:USAXS:MinStep")
    usaxs_time = Component(EpicsSignal,               "9idcLAX:USAXS:CountTime")
    
    def UPDRange(self):
        return upd_controls.auto.lurange.value  # TODO: check return value is int


class Parameters_USAXS(Device):
    pass


class Parameters_SBUSAXS(Device):
    pass


class Parameters_SAXS(Device):
    pass


class Parameters_WAXS(Device):
    pass


class Parameters_Radiography(Device):
    pass


class Parameters_Imaging(Device):
    pass


class Parameters_OutOfBeam(Device):
    pass


class GeneralParameters(Device):
    """
    cache of program parameters to share with/from EPICS
    """
    USAXS = Component(Parameters_USAXS)
    SBUSAXS = Component(Parameters_SBUSAXS)
    SAXS = Component(Parameters_SAXS)
    WAXS = Component(Parameters_WAXS)
    Radiography = Component(Parameters_Radiography)
    Imaging = Component(Parameters_Imaging)
    OutOfBeam = Component(Parameters_OutOfBeam)
    
    # consider refactoring
    usaxs = Component(GeneralUsaxsParameters)
    FlyScan = Component(FlyScanParameters)
    preUSAXStune = Component(PreUsaxsTuneParameters)

terms = GeneralParameters(name="terms")
