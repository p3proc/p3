"""Define Nodes for time shift and despike workflow

TODO

"""
from ..base import basenodedefs
from .custom import *
from nipype import Node
from nipype.interfaces import afni,fsl
from nipype.interfaces.utility import IdentityInterface,Function

class definednodes(basenodedefs):
    """Class initializing all nodes in workflow

        TODO

    """

    def __init__(self,settings):
        # call base constructor
        super().__init__(settings)

        # define input node
        self.inputnode = Node(
            IdentityInterface(
                fields=['refimg']
            ),
            name='input'
        )

        # Skullstrip the EPI image
        self.epi_skullstrip = Node(
            fsl.BET(),
            name='epi_skullstrip'
        )
        self.epi_automask = Node(
            afni.Automask(
                args='-overwrite',
                outputtype='NIFTI_GZ'
            ),
            name='epi_automask'
        )
        self.epi_3dcalc = Node(
            afni.Calc(
                expr='c*or(a,b)',
                overwrite=True,
                outputtype='NIFTI_GZ'
            ),
            name='epi_3dcalc'
        )

        # deoblique the MPRAGE and compute the transform between EPIREF and MPRAGE obliquity
        self.warp = Node(
            Function(
                input_names=['in_file','card2oblique','args'],
                output_names=['out_file','ob_transform'],
                function=warp_custom
            ),
            name='3dwarp'
        )
        self.warp.inputs.args = '-newgrid 1.000000'

        # resample the EPIREF to the MPRAGE
        self.resample = Node(
            afni.Resample(
                resample_mode='Cu',
                outputtype='NIFTI_GZ'
            ),
            name='resample'
        )

        # calculate a weight mask for the lpc weighting
        self.weightmask = Node(
            Function(
                input_names=['in_file','no_skull'],
                output_names=['out_file'],
                function=create_weightmask
            ),
            name='weightmask'
        )

        # register the mprage to the tcat (BASE=TARGET, REGISTER TO THIS SPACE; SOURCE=INPUT, LEAVE THIS SPACE)
        # this registration is on images with the same grids, whose obliquity has been accounted for
        self.registert12tcat = Node(
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
            name='registert1totcat'
        )

        # define output node
        self.outputnode = Node(
            IdentityInterface(
                fields=['t1_2_epi','oblique_transform']
            ),
            name='output'
        )
