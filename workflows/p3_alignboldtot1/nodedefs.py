"""Define Nodes for time shift and despike workflow

TODO

"""
from ppp.base import basenodedefs
from .custom import *
from nipype import Node
from nipype.interfaces import afni,fsl
from nipype.interfaces.utility import Function

class definednodes(basenodedefs):
    """Class initializing all nodes in workflow

        TODO

    """

    def __init__(self,settings):
        # call base constructor
        super().__init__(settings)

        # define input/output node
        self.set_input(['refimg','T1_0'])
        self.set_output(['epi_2_t1'])

        # define datasink substitutions
        self.set_subs([
            ('_despike_tshift_roi_unwarped_masked_calc','_reference_skullstrip'), # name the skullstripped refimg
        ])

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

        # align epi to t1
        self.align_epi_2_anat = Node(
            Function(
                input_names=['in_file','anat'],
                output_names=['epi_al_mat','epi_al_orig'],
                function=alignepi2anat
            ),
            name='align_epi_2_anat'
        )
