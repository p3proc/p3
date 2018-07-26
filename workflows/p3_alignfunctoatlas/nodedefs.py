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
            'func', # I pass this in so I can get the TR info from BIDS
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

        # format the reference image
        self.format_reference = MapNode(
            Function(
                input_names=['func','reference','bids_dir'],
                output_names=['formatted_reference','dim4','TR'],
                function=format_reference
            ),
            iterfield=['func'],
            name='format_reference'
        )
        self.format_reference.inputs.bids_dir = settings['bids_dir']

        # combine 3D transforms and replicate to 4D
        self.combinetransforms = Node(
           Function(
               input_names=[
                    'func',
                    'reference',
                    'dim4',
                    'TR',
                    'affine_func_2_anat',
                    'warp_func_2_anat',
                    'affine_anat_2_atlas',
                    'warp_anat_2_atlas',
                    'affine_fmc',
                    'warp_fmc'
                    ],
               output_names=['combined_transforms4D'],
               function=combinetransforms
           ),
           iterfield=['dim4','TR'],
           name='combinetransforms'
        )

        # apply nonlinear transform
        self.applytransforms = MapNode(
           Function(
               input_names=['in_file','reference4D','combined_transforms4D','warp_func_2_refimg'],
               output_names=['out_file'],
               function=applytransforms
           ),
           iterfield=['in_file','warp_func_2_refimg'],
           name='applytransforms'
        )
