"""Define Nodes for time shift and despike workflow

TODO

"""
from p3.base import basenodedefs
from p3.utility import set_atlas_path,get_basename
from .custom import *
from nipype import Node,MapNode
from nipype.interfaces import afni,fsl
from nipype.interfaces.utility import Function
import os

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
            'warp_fmc',
            'refimg',
            'affine_func_2_anat',
            'warp_func_2_anat',
            'affine_anat_2_atlas',
            'warp_anat_2_atlas'
            ])
        self.set_output(['func_atlas'])

        # define datasink substitutions
        atlas_base = get_basename(settings['atlas']) # get atlas basename
        self.set_subs([
            ('_flirt','_funcres'),
            (atlas_base,'atlas/{}'.format(atlas_base)) # save resampled atlas to atlas folder
        ])
        self.set_resubs([
            ('sub-(?P<subject>\w+_)','func/sub-\g<subject>'), # place file under anat folder
            ('func/sub-(?P<subject>\w+)_ses-(?P<session>\w+)_','func/ses-\g<session>/sub-\g<subject>_ses-\g<session>_') # add session folders if they exist
        ])

        # grab the resolution of the refimg
        self.get_resolution = Node(
            Function(
                input_names=['reference'],
                output_names=['resolution'],
                function=get_resolution
            ),
            name='get_resolution'
        )

        # resample atlas to epi space so we can use it as a reference
        self.resample = Node(
            fsl.FLIRT(
                no_search=True
            ),
            name='resample'
        )
        self.resample.inputs.in_file = set_atlas_path(settings['atlas'])
        self.resample.inputs.reference = set_atlas_path(settings['atlas'])

        # format the reference image (which should be the resampled atlas)
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
        self.combinetransforms = MapNode(
           Function(
               input_names=[
                    'func',
                    'reference',
                    'dim4',
                    'TR',
                    'affine_func_2_anat',
                    'affine_anat_2_atlas',
                    'warp_anat_2_atlas',
                    'warp_fmc'
                    ],
               output_names=['combined_transforms4D'],
               function=combinetransforms
           ),
           iterfield=['func','dim4','TR','warp_fmc'],
           name='combinetransforms'
        )
        self.combinetransforms.n_procs = settings['num_threads']

        # align the reference image to atlas and create a dfnd mask from it
        self.create_dfnd_mask = Node(
            Function(
                input_names=[
                    'refimg',
                    'affine_func_2_anat',
                    'affine_anat_2_atlas',
                    'warp_anat_2_atlas',
                    'reference'
                ],
                output_names=['mask_file'],
                function=create_dfnd_mask
            ),
            name='create_dfnd_mask'
        )
        self.create_dfnd_mask.n_procs = settings['num_threads']

        # apply nonlinear transform
        self.applytransforms = MapNode(
           Function(
               input_names=['in_file','reference4D','combined_transforms4D','warp_func_2_refimg','dfnd_mask'],
               output_names=['out_file'],
               function=applytransforms
           ),
           iterfield=['in_file','reference4D','combined_transforms4D','warp_func_2_refimg'],
           name='applytransforms'
        )
        self.applytransforms.n_procs = settings['num_threads']
