"""
    Define Nodes for nipype workflow
"""
import os
from nipype import Node,MapNode,IdentityInterface
from nipype.interfaces import afni,fsl,freesurfer
from nipype.interfaces.io import SelectFiles,DataSink
from nipype.interfaces.utility import Function,IdentityInterface,Rename,Merge
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
        self.despike = MapNode(
            ExtendedDespike(
                args="-ignore {} -NEW -nomask".format(
                    self.IGNOREFRAMES
                ),
                outputtype="NIFTI_GZ"
            ),
            iterfield=['in_file'],
            name='despike'
        )

        # extract slice timing so we can pass it to slice time correction
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
        self.tshift = MapNode(
            afni.TShift(
                args="-heptic",
                ignore=self.IGNOREFRAMES,
                tzero=0,
                outputtype="NIFTI_GZ"
            ),
            iterfield=['in_file','tpattern','tr'],
            name='tshift'
        )

        # Setup basefile for volreg
        self.firstrunonly = Node( # this will create a list of the first run to feed as a basefile
            Function(
                input_names=['epi'],
                output_names=['epi'],
                function=lambda epi: [epi[0] for item in epi]
            ),
            name='retrievefirstrun'
        )

        self.extractroi = MapNode( # create 2 nodes to obtain ref frame of first run and each run
            fsl.ExtractROI(
                t_min=self.IGNOREFRAMES,
                t_size=1,
                output_type='NIFTI_GZ'
            ),
            iterfield=['in_file'],
            name='extractroi'
        )

        # Create Named Output for first frame alignment (first run only)
        self.firstframefirstrun = Node(
            IdentityInterface(
                fields=['refimg']
            ),
            name='firstframefirstrun'
        )

        # Motion correction (create 10 nodes for different permutations of inputs)
        self.volreg = MapNode(
            afni.Volreg(
                args="-heptic -maxite {}".format(
                    25
                ),
                verbose=True,
                zpad=10,
                outputtype="NIFTI_GZ"
            ),
            iterfield=['basefile','in_file'],
            name='volreg'
        )

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
                expr='or(a,b,c)',
                overwrite=True,
                outputtype='NIFTI_GZ'
            ),
            name='maskop3'
        )
        self.maskop4 = Node(
            afni.Calc(
                expr='c*and(a,b)',
                overwrite=True,
                outputtype='NIFTI_GZ'
            ),
            name='maskop4'
        )
        self.skullstripped_mprage = Node(
            IdentityInterface(
                fields=['noskull']
            ),
            name='skullstripped_mprage'
        )

        # Register to Atlas
        self.register = Node(
            Function(
                input_names=['in_file'],
                output_names=['out_file','transform_file'],
                function=register_atlas
            ),
            name='atlasregister'
        )
        self.skullstripped_atlas_mprage = Node(
            IdentityInterface(
                fields=['noskull_at','transform']
            ),
            name='skullstripped_atlas_mprage'
        )

        # Skullstrip the EPI image
        self.epi_skullstrip = MapNode(
            fsl.BET(),
            iterfield=['in_file'],
            name='epi_skullstrip'
        )
        self.epi_automask = MapNode(
            afni.Automask(
                args='-overwrite',
                outputtype='NIFTI_GZ'
            ),
            iterfield=['in_file'],
            name='epi_automask'
        )
        self.epi_3dcalc = MapNode(
            afni.Calc(
                expr='c*or(a,b)',
                overwrite=True,
                outputtype='NIFTI_GZ'
            ),
            iterfield=['in_file_a','in_file_b','in_file_c'],
            name='epi_3dcalc'
        )

        # deoblique the MPRAGE and compute the transform between EPIREF and MPRAGE obliquity
        self.warp_args = Node(
            IdentityInterface(
                fields=['args']
            ),
            name='warp_args'
        )
        self.warp_args.inputs.args = '-newgrid 1.000000'
        self.warp = MapNode(
            Function(
                input_names=['in_file','card2oblique','args'],
                output_names=['out_file','ob_transform'],
                function=warp_custom
            ),
            iterfield=['in_file','card2oblique'],
            name='3dwarp'
        )
        self.noskull_obla2e = Node( # Transform between EPIREF and MPRAGE obliquity
            IdentityInterface(
                fields=['noskull_ob','noskull_obla2e_mat']
            ),
            name='noskull_obla2e'
        )

        # resample the EPIREF to the MPRAGE
        self.resample = MapNode(
            afni.Resample(
                resample_mode='Cu',
                outputtype='NIFTI_GZ'
            ),
            iterfield=['in_file','master'],
            name='resample'
        )

        # calculate a weight mask for the lpc weighting
        self.weightmask = MapNode(
            Function(
                input_names=['in_file','no_skull'],
                output_names=['out_file'],
                function=create_weightmask
            ),
            iterfield=['in_file','no_skull'],
            name='weightmask'
        )

        # register the mprage to the tcat (BASE=TARGET, REGISTER TO THIS SPACE; SOURCE=INPUT, LEAVE THIS SPACE)
        # this registration is on images with the same grids, whose obliquity has been accounted for
        self.registert12tcat = MapNode(
            afni.Allineate(
                args='-lpc -nocmass -weight_frac 1.0 -master SOURCE',
                maxrot=6,
                maxshf=10,
                verbose=True,
                warp_type='affine_general',
                source_automask=4,
                two_pass=True,
                two_best=11,
                out_matrix='t12tcat_transform_mat.aff12.1D',
                out_weight_file='t12tcat_transform_weight_file.nii.gz',
                outputtype='NIFTI_GZ'
            ),
            iterfield=['in_file','weight','reference'],
            name='registermpragetotcat'
        )

        # there are 3 ways to bring rawEPI into the ATLAS space (all need volreg, epi-mpr, and mpr-atl:
        # use the volreg results with EPI1 as the referent, and the epi-mpr transform for EPI1
        # use the volreg results with INT  as the referent, and the epi-mpr transform for EPI1
        # use the volreg results with INT  as the referent, and the epi-mpr tranfrorm for EPIX
        #
        # only the first and second options will enforce cross-run alignment

        # for run 1, all methods are the same

        # Create transform
        self.transformepi2epi2mpr2atl = MapNode(
            Function(
                input_names=['in_file','tfm1','tfm2','tfm3'],
                output_names=['master_transform'],
                function=concattransform
            ),
            iterfield=['tfm1','tfm2','tfm3'],
            name='transformepi2epi2mpr2atl'
        )

        # align images
        self.alignepi2atl = MapNode(
            afni.Allineate(
                args='-mast_dxyz 3',
                overwrite=True,
                outputtype='NIFTI_GZ'
            ),
            iterfield=['in_matrix','in_file'],
            name='alignepi2atl'
        )


        # Output
        self.output = []
        for n in range(4):
            self.output.append(Node(
                DataSink(
                    base_directory=self.BASE_DIR,
                    substitutions=[
                        ('_subject_id_',''),
                        ('_calc_calc_calc_calc_calc','')
                    ]
                ),
                name='output_{}'.format(n)
            ))
