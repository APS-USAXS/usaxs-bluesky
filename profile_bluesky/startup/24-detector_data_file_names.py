print(__file__)

"""
replace BlueSky file name scheme when used with area detector
"""

logger = logging.getLogger(__name__)
DATABROKER_ROOT_PATH = "/"


def _validate_AD_HDF5_path_(path, root_path):
    if not path.startswith(root_path):
        msg = "error in file {}:\n  path '{}' must start with '{}".format(
            __file__,
            path,
            root_path
        )
        raise ValueError(msg)


"""
file systems on some area detectors need more work

saxs:  /mnt/share1/USAXS_data/yyyy-mm/user_working_folder_saxs/
waxs:  /mnt/usaxscontrol/USAXS_data/yyyy-mm/user_working_folder_waxs/

PointGrey BlackFly does not write out to file typically.  No use of HDF5 plugin.

Alta: /mnt/share1/USAXS_data/...
"""


area_detector_EPICS_PV_prefix = {
    'Pilatus 100k' : 'usaxs_pilatus1:',
    'Pilatus 200kw' : 'usaxs_pilatus2:',
    'PointGrey BlackFly' : '9idFLY1:',
    'Alta' : '9idalta:',
    'SimDetector' : '9idcSIM1:',
}


class MyFileStorePluginBase(FileStoreBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stage_sigs.update([('auto_increment', 'Yes'),
                                ('array_counter', 0),
                                ('auto_save', 'Yes'),
                                ('num_capture', 0),
                                ])
        self._fn = None

    def make_filename(self):
        '''Make a filename.

        This is a hook so that the read and write paths can either be modified
        or created on disk prior to configuring the areaDetector plugin.

        Returns
        -------
        filename : str
            The start of the filename
        read_path : str
            Path that ophyd can read from
        write_path : str
            Path that the IOC can write to
        '''
        # These are the instructions as-supplied
        #filename = new_short_uid()
        #formatter = datetime.now().strftime
        #write_path = formatter(self.write_path_template)	# for HDF5 plugin
        #read_path = formatter(self.read_path_template)		# for DataBroker
        
        # trust EPICS to have these right (per #15)
        logger.info("File path: " + self.file_path.value)
        logger.info("File name: " + self.file_name.value)
        logger.info("File template: " + self.file_template.value)
        
        # start of the file name, file number will be appended per template
        filename = self.file_name.value
        
        # this is where the HDF5 plugin will write the image, 
        # relative to the IOC's filesystem
        write_path = self.file_path.value
        
        # this is where the DataBroker will find the image, 
        #on a filesystem accessible to BlueSky
        read_path = write_path.replace("/mnt/", "/").replace("/usaxscontrol/", "/share1/")
        
        msg = "make_filename() filename={}, read_path={}, write_path={}".format(
            filename, read_path, write_path
        )
        logger.info(msg)
        
        return filename, read_path, write_path

    def stage(self):
        # Make a filename.
        filename, read_path, write_path = self.make_filename()

        # Ensure we do not have an old file open.
        set_and_wait(self.capture, 0)
        # These must be set before parent is staged (specifically
        # before capture mode is turned on. They will not be reset
        # on 'unstage' anyway.
        set_and_wait(self.file_path, write_path)
        set_and_wait(self.file_name, filename)
        #set_and_wait(self.file_number, 0)
        super().stage()

        # AD does this same templating in C, but we can't access it
        # so we do it redundantly here in Python.
        self._fn = self.file_template.get() % (read_path,
                                               filename,
                                               self.file_number.get() - 1)
                                               # file_number is *next* iteration
        self._fp = read_path
        if not self.file_path_exists.get():
            raise IOError("Path %s does not exist on IOC."
                          "" % self.file_path.get())


my_hdf5_file_template = "%s%s_%4.4d.hdf"    # what we normally use
my_hdf5_file_template = "%s%s_%6.6d.h5" # re-define so we can see this setup happen


class MyFileStoreHDF5(MyFileStorePluginBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filestore_spec = 'AD_HDF5'  # SPEC name stored in resource doc
        self.stage_sigs.update([
            ('file_template', my_hdf5_file_template),
            ('file_write_mode', 'Stream'),
            ('capture', 1)
        ])

    def get_frames_per_point(self):
        return self.num_capture.get()

    def stage(self):
        super().stage()
        res_kwargs = {'frame_per_point': self.get_frames_per_point()}
        logger.debug("Inserting resource with filename %s", self._fn)
        fn = PurePath(self._fn).relative_to(self.reg_root)
        self._resource = self._reg.register_resource(
            self.filestore_spec,
            str(self.reg_root), str(fn),
            res_kwargs)


class MyFileStoreHDF5IterativeWrite(MyFileStoreHDF5, FileStoreIterativeWrite):
    pass

