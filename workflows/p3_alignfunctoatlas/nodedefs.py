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
        self.set_input([
            'func_stc_despike',
            'warp_func_2_refimg',
            'affine_fmc',
            'warp_fmc',
            'refimg',
            'affine_func_2_anat',
            'warp_func_2_anat',
            'affine_anat_2_atlas',
            'warp_anat_2_atlas'
            ])
        self.set_output(['func_aligned'])

        # define datasink substitutions
        self.set_resubs([])

        # apply nonlinear transform
        self.applytransforms = MapNode(
           Function(
               input_names=[
                    'in_file',
                    'reference',
                    'warp_func_2_refimg',
                    'affine_func_2_anat',
                    'warp_func_2_anat',
                    'affine_anat_2_atlas',
                    'warp_anat_2_atlas',
                    'affine_fmc',
                    'warp_fmc'
                    ],
               output_names=['out_file'],
               function=applytransforms
           ),
           iterfield=['in_file','warp_func_2_refimg'],
           name='applytransforms'
        )
