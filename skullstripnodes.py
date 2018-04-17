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

        # Define settings
        self.SUBJECT_ID = settings['subject_id']
        self.INPUT_T1 = settings['input_t1']
        self.INPUT_DIR = settings['input_dir']
        self.BASE_DIR = settings['output_dir']
        self.SUBJECTS_DIR = os.path.join(self.BASE_DIR,'output','freesurfer_output')
        self.ENV = {}
        if settings['fs_license']:
            self.ENV['FS_LICENSE'] = os.path.join(self.INPUT_DIR,settings['fs_license'])

        # make directories if not exist
        os.makedirs(self.SUBJECTS_DIR,exist_ok=True)

        # Select epis and T1s (and their sidecars)
        self.fileselection = Node(
            SelectFiles(
                {
                    'T1': os.path.join(self.INPUT_DIR,self.INPUT_T1),
                }
            ),
            name='selectfiles'
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
                subject_id=self.SUBJECT_ID,
                directive='all',
                environ=self.ENV,
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

        # Output
        self.output = []
        for n in range(1):
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
