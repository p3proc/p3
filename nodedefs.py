"""
    Define Nodes for nipype workflow
"""
import os
from nipype import Node,MapNode,IdentityInterface
from nipype.interfaces import afni,fsl,freesurfer
from nipype.interfaces.io import SelectFiles,DataSink
from nipype.interfaces.utility import Function
from custom import * # import our custom functions/interfaces

class definednodes:
    """
        Class initializing all nodes in workflow
    """

    def __init__(self,settings):
        """
            Initialize settings and define nodes
        """

        # Define several directoris to use
        self.BASE_DIR = settings['BASE_DIR']
        self.SUBJECTS_DIR = os.path.join(self.BASE_DIR,'output','freesurfer_output')
        self.TMP_DIR = os.path.join(self.BASE_DIR,'tmp')
        self.REF_IMGS = os.path.join(self.BASE_DIR,'refimgs')

        # make directories if not exist
        os.makedirs(self.SUBJECTS_DIR,exist_ok=True)
        os.makedirs(self.TMP_DIR,exist_ok=True)

        # set number of initial frames to ignore
        self.IGNOREFRAMES = settings['ignoreframes']

        # Create an Identity interface to select subjects
        self.infosource = Node(
            IdentityInterface(
                fields=['subject_id']
            ),
            iterables = [('subject_id',['sub-CTS200'])],
            name='infosource'
        )

        # Select epis and T1s (and their sidecars)
        self.fileselection = Node(
            SelectFiles(
                {
                    'epi': os.path.join(self.BASE_DIR,'dataset','{subject_id}','func','*baseline*.nii.gz'),
                    'epi_sidecar': os.path.join(self.BASE_DIR,'dataset','{subject_id}','func','*baseline*.json'),
                    'T1': os.path.join(self.BASE_DIR,'dataset','{subject_id}','anat','*T1w*.nii.gz'),
                    'T1_sidecar': os.path.join(self.BASE_DIR,'dataset','{subject_id}','anat','*T1w*.json')
                }
            ),
            name='selectfiles'
        )

        # Do QC on all files
        self.QC = MapNode(
            Function(
                input_names=['epi','epi_sidecar'],
                output_names=['QClist'],
                function=qualitycheck
            ),
            iterfield=['epi','epi_sidecar'],
            name='QC'
        )

        # Reduce set based on QC check
        self.QCreduce = Node(
            Function(
                input_names=['QClist'],
                output_names=['epi','epi_sidecar'],
                function=QCreduceset
            ),
            name='QCreduce'
        )

        # Despike epi data (create 2 for permutations with slice time correction)
        self.despike = []
        for n in range(2):
            self.despike.append(MapNode(
                ExtendedDespike(
                    args="-ignore {} -NEW -nomask".format(
                        self.IGNOREFRAMES
                    ),
                    outputtype="NIFTI_GZ"
                ),
                iterfield=['in_file'],
                name='despike{}'.format(n)
            ))

        # extract slice timing so we can pass it to slice time correction
        extract_slicetime = extract_slicetime_func(self.TMP_DIR) # create object
        self.extract_stc = MapNode(
            Function(
                input_names=['epi_sidecar'],
                output_names=['slicetiming','TR'],
                function=extract_slicetime
            ),
            iterfield=['epi_sidecar'],
            name='extract_slicetime'
        )

        # timeshift data (create 2 for permutations with despiking)
        self.tshift = []
        for n in range(2):
            self.tshift.append(MapNode(
                afni.TShift(
                    args="-heptic",
                    ignore=self.IGNOREFRAMES,
                    tzero=0,
                    outputtype="NIFTI_GZ"
                ),
                iterfield=['in_file','tpattern','tr'],
                name='tshift{}'.format(n)
            ))

        # Setup basefile for volreg
        self.firstrunonly = Node( # this will create a list of the first run to feed as a basefile
            Function(
                input_names=['epi'],
                output_names=['epi'],
                function=lambda epi: [epi[0] for item in epi]
            ),
            name='retrievefirstrun'
        )

        self.extractroi = []
        for n in range(2): # create 2 nodes to align to first run and each run
            self.extractroi.append(MapNode(
                fsl.ExtractROI(
                    t_min=self.IGNOREFRAMES,
                    t_size=1,
                    output_type='NIFTI_GZ'
                ),
                iterfield=['in_file'],
                name='extractroi{}'.format(n)
            ))

        # Motion correction (create 10 nodes for different permutations of inputs)
        self.volreg = []
        for n in range(10):
            self.volreg.append(MapNode(
                afni.Volreg(
                    args="-heptic -maxite {}".format(
                        25
                    ),
                    verbose=True,
                    zpad=10,
                    outputtype="NIFTI_GZ"
                ),
                iterfield=['basefile','in_file'],
                name='volreg{}'.format(n)
            ))

        # Skullstrip
        # skullstrip mprage (afni)
        self.afni_skullstrip = Node(
            afni.SkullStrip(
                args="-orig_vol",
                outputtype="NIFTI_GZ"
            ),
            name='afni_skullstrip'
        )
        # skullstrip mprage (fsl)
        self.fsl_skullstrip = Node(
            fsl.BET(),
            name='fsl_skullstrip'
        )

        # Recon-all
        self.reconall = Node(
            freesurfer.ReconAll(
                directive='all',
                subjects_dir=self.SUBJECTS_DIR,
                parallel=True,
                openmp=4
            ),
            name='reconall'
        )

        # MRIConvert
        self.orig_convert = Node(
            freesurfer.MRIConvert(
                in_type='mgz',
                out_type='niigz'
            ),
            name='orig_mriconvert'
        )
        self.brainmask_convert = Node(
            freesurfer.MRIConvert(
                in_type='mgz',
                out_type='niigz'
            ),
            name='brainmask_mriconvert'
        )

        # 3dAllineate (FSorig)
        self.allineate_orig = Node(
            afni.Allineate(
                out_matrix='FSorig.XFM.FS2MPR.aff12.1D',
                overwrite=True,
                outputtype='NIFTI_GZ'
            ),
            name='3dallineate_orig'
        )

        # Inline function for setting up to copy IJK_TO_DICOM_REAL file attribute
        self.refit_setup = Node(
            Function(
                input_names=['noskull_T1'],
                output_names=['refit_input'],
                function=lambda noskull_T1: (noskull_T1,'IJK_TO_DICOM_REAL')
            ),
            name='refitsetup'
        )

        # 3dRefit (Create 2, one for FSorig and one for FSbrainmask)
        self.refit = []
        for n in range(2):
            self.refit.append(Node(
                afni.Refit(),
                name='3drefit{}'.format(n)
            ))
        
        # 3dAllineate (FSbrainmask)
        self.allineate_bm = Node(
            afni.Allineate(
                overwrite=True,
                no_pad=True,
                outputtype='NIFTI_GZ'
            ),
            name='3dallineate_brainmask'
        )

        # 3dcalc for uniform intensity
        self.uniform = Node(
            afni.Calc(
                expr='a*and(b,b)',
                overwrite=True,
                outputtype='NIFTI_GZ'
            ),
            name='uniformintensity'
        )

        # 3dcalc operations for achieving final mask
        self.maskop1 = Node(
            afni.Calc(
                expr='step(a)',
                overwrite=True,
                outputtype='NIFTI_GZ'
            ),
            name='maskop1'
        )
        self.maskop2 = []
        for n in range(3):
            self.maskop2.append(Node(
                afni.Calc(
                    args='-b a+i -c a-i -d a+j -e a-j -f a+k -g a-k',
                    expr='ispositive(a+b+c+d+e+f+g)',
                    overwrite=True,
                    outputtype='NIFTI_GZ'
                ),
                name='maskop2_{}'.format(n)
            ))
        self.maskop3 = Node(
            afni.Calc(
                expr='and(a,or(b,c))',
                overwrite=True,
                outputtype='NIFTI_GZ'
            ),
            name='maskop3'
        )
        self.maskop4 = Node(
            afni.Calc(
                expr='a*b',
                overwrite=True,
                outputtype='NIFTI_GZ'
            ),
            name='maskop4'
        )
        self.maskop5 = Node(
            afni.Calc(
                expr='or(a,b,c)',
                overwrite=True,
                outputtype='NIFTI_GZ'
            ),
            name='maskop5'
        )
        self.maskop6 = Node(
            afni.Calc(
                expr='c*and(a,b)',
                overwrite=True,
                outputtype='NIFTI_GZ'
            ),
            name='maskop6'
        )

        # Register to Atlas
        self.register = Node(
            afni.AutoTLRC(
                base='TT_N27+tlrc',
                no_ss=True,
                args='-pad_input 60',
                outputtype='NIFTI_GZ'
            ),
            name='atlasregister'
        )

        # 3dAllineate (for un-skull stripped T1)
        self.allineate_unstrip = Node(
            afni.Allineate(
                out_file=os.path.join(self.TMP_DIR,'unstrip_out_allineate.nii.gz'), # bug in nipype, it doesn't produce output without setting this parameter... we write this to our own tmp dir for now...
                reference=os.path.join(self.REF_IMGS,'TT_N27.nii.gz'),
                overwrite=True,
                outputtype='NIFTI_GZ'
            ),
            name='3dallineate_unstrip'
        )

        # Output
        self.output = []
        for n in range(2):
            self.output.append(Node(
                DataSink(
                    base_directory=self.BASE_DIR,
                    substitutions=[
                        ('_subject_id_',''),
                        ('_calc_calc_calc_calc_calc','')
                    ]
                ),
                name='output{}'.format(n)
            ))
