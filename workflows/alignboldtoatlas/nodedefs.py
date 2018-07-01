"""Define Nodes for time shift and despike workflow

TODO

"""
from p3.base import basenodedefs
from .custom import *
from nipype import Node,MapNode
from nipype.interfaces import afni
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
                fields=['noskull_at','oblique_transform','t1_2_epi','epi2epi1','tcat']
            ),
            name='input'
        )

        # Create transform
        self.transformepi2epi2mpr2atl = MapNode(
            Function(
                input_names=['in_file','tfm1','tfm2','tfm3'],
                output_names=['master_transform'],
                function=concattransform
            ),
            iterfield=['tfm3'],
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

        # define output node
        self.outputnode = Node(
            IdentityInterface(
                fields=['epi_at']
            ),
            name='output'
        )
