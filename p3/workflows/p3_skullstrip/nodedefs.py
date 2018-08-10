"""Define Nodes for skullstrip workflow

TODO

"""
from p3.base import basenodedefs
from nipype import Node,MapNode
from nipype.interfaces import afni,fsl,ants
from nipype.interfaces.utility import Function

class definednodes(basenodedefs):
    """Class initializing all nodes in workflow

        TODO

    """

    def __init__(self,settings):
        # call base constructor
        super().__init__(settings)

        # define input/output node
        self.set_input(['T1','orig','brainmask'])
        self.set_output(['T1_skullstrip','allineate_freesurfer2anat'])

        # define datasink substitutions
        self.set_subs([
            ('_maskop40',''),
            ('_calc_calc_calc_calc_calc','')
        ])

        # 3dAllineate (FSorig)
        self.allineate_orig = MapNode(
            afni.Allineate(
                out_matrix='FSorig2MPR.aff12.1D',
                overwrite=True,
                outputtype='NIFTI_GZ'
            ),
            iterfield=['in_file','reference'],
            name='3dallineate_orig'
        )
        # 3dAllineate (FSbrainmask)
        self.allineate_bm = MapNode(
            afni.Allineate(
                overwrite=True,
                no_pad=True,
                outputtype='NIFTI_GZ'
            ),
            iterfield=['in_file','reference','in_matrix'],
            name='3dallineate_brainmask'
        )

        # skullstrip mprage (afni)
        self.afni_skullstrip = MapNode(
            afni.SkullStrip(
                args="-orig_vol",
                outputtype="NIFTI_GZ"
            ),
            iterfield=['in_file'],
            name='afni_skullstrip'
        )
        # 3dcalc operations for achieving final mask
        self.maskop1 = MapNode(
            afni.Calc(
                expr='step(a)',
                overwrite=True,
                outputtype='NIFTI_GZ'
            ),
            iterfield=['in_file_a'],
            name='maskop1'
        )
        self.maskop2 = []
        for n in range(3):
            self.maskop2.append(MapNode(
                afni.Calc(
                    args='-b a+i -c a-i -d a+j -e a-j -f a+k -g a-k',
                    expr='ispositive(a+b+c+d+e+f+g)',
                    overwrite=True,
                    outputtype='NIFTI_GZ'
                ),
                iterfield=['in_file_a'],
                name='maskop2_{}'.format(n)
            ))
        # Inline function for setting up to copy IJK_TO_DICOM_REAL file attribute
        self.refit_setup = MapNode(
            Function(
                input_names=['noskull_T1'],
                output_names=['refit_input'],
                function=lambda noskull_T1: (noskull_T1,'IJK_TO_DICOM_REAL')
            ),
            iterfield=['noskull_T1'],
            name='refitsetup'
        )
        # 3dRefit
        self.refit = MapNode(
            afni.Refit(),
            iterfield=['in_file','atrcopy'],
            name='3drefit'
        )
        # 3dcalc for uniform intensity
        self.uniform = MapNode(
            afni.Calc(
                expr='a*and(b,b)',
                overwrite=True,
                outputtype='NIFTI_GZ'
            ),
            iterfield=['in_file_a','in_file_b'],
            name='uniformintensity'
        )

        # skullstrip mprage (fsl)
        self.fsl_skullstrip = MapNode(
            fsl.BET(),
            iterfield=['in_file'],
            name='fsl_skullstrip'
        )
        self.maskop3 = MapNode(
            afni.Calc(
                expr='or(a,b,c)',
                overwrite=True,
                outputtype='NIFTI_GZ'
            ),
            iterfield=['in_file_a','in_file_b','in_file_c'],
            name='maskop3'
        )
        self.maskop4 = MapNode(
            afni.Calc(
                expr='c*and(a,b)',
                overwrite=True,
                outputtype='NIFTI_GZ'
            ),
            iterfield=['in_file_a','in_file_b','in_file_c'],
            name='maskop4'
        )

        # Convert from list to string input
        self.select0T1 = Node(
            Function(
                input_names=['T1_list'],
                output_names=['T1_0'],
                function=lambda T1_list: T1_list[0]
            ),
            name='select0T1'
        )

        # apply bias field correction
        self.biasfieldcorrect = Node(
            ants.N4BiasFieldCorrection(
                num_threads=settings['num_threads'],
                copy_header=True
            ),
            name='biasfieldcorrect'
        )
