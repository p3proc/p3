"""Define Nodes for time shift and despike workflow

TODO

"""
from ppp.base import basenodedefs
from .custom import *
from nipype import Node,MapNode
from nipype.interfaces import afni
from nipype.interfaces.utility import Function

class definednodes(basenodedefs):
    """Class initializing all nodes in workflow

        TODO

    """

    def __init__(self,settings):
        # call base constructor
        super().__init__(settings)

        # define input/output node
        self.set_input(['noskull_at','nonlin_warp','oblique_transform','t1_2_epi','epi'])
        self.set_output(['epi_at'])

        # define datasink substitutions
        self.set_resubs([
            ('_alignepi2atl\d{1,3}','')
        ])

        # Create transform
        self.transformepi2mpr2atl = Node(
            Function(
                input_names=['in_file','tfm1','tfm2'],
                output_names=['master_transform'],
                function=concattransform
            ),
            name='transformepi2mpr2atl'
        )

        # align images
        self.alignepi2atl = MapNode(
            afni.Allineate(
                args='-mast_dxyz 3',
                overwrite=True,
                outputtype='NIFTI_GZ'
            ),
            iterfield=['in_file'],
            name='alignepi2atl'
        )

        # apply nonlinear transform
        self.applyQwarptransform = MapNode(
            Function(
                input_names=['in_file','warped_file'],
                output_names=['out_file'],
                function=NwarpApply
            ),
            iterfield=['in_file'],
            name='applyQwarptransform'
        )
