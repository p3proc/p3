"""Define Nodes for time shift and despike workflow

TODO

"""
import os
from ppp.base import basenodedefs
from .custom import *
from nipype import Node,MapNode
from nipype.interfaces import afni,fsl
from nipype.interfaces.utility import Function,IdentityInterface

class definednodes(basenodedefs):
    """Class initializing all nodes in workflow

        TODO

    """

    def __init__(self,settings):
        # call base constructor
        super().__init__(settings)

        # define input/output node
        self.set_input(['epi','epi_aligned'])
        self.set_output(['epi'])

        # define datasink substitutions
        # self.set_subs([])

        # define datasink regular expression substitutions
        self.set_resubs([
            (r'_warp_epi\d{1,3}','')
        ])

        # get magnitude and phase
        self.getmagandphase = MapNode(
            Function(
                input_names=['epi_file','bids_dir'],
                output_names=['magnitude','phasediff','TE','echospacing'],
                function=get_magnitude_phase_TE
            ),
            iterfield=['epi_file'],
            name='getmagandphase'
        )
        self.getmagandphase.inputs.bids_dir = settings['bids_dir']

        # get skullstrip of magnitude image
        self.skullstrip_magnitude = MapNode(
            fsl.BET(
                robust=True,
                output_type='NIFTI_GZ'
            ),
            iterfield=['in_file'],
            name='skullstrip_magnitude'
        )

        # erode skullstripped magnitude image (3x)
        self.erode_magnitude = []
        for n in range(3):
            self.erode_magnitude.append(MapNode(
                fsl.ErodeImage(
                    output_type='NIFTI_GZ',
                ),
                iterfield=['in_file'],
                name='erode_magnitude{}'.format(n)
            ))

        # create mask from eroded magnitude image
        self.create_mask = MapNode(
            fsl.maths.MathsCommand(
                args='-bin',
                output_type='NIFTI_GZ'
            ),
            iterfield=['in_file'],
            name='create_mask'
        )

        # calculate fieldmap image (rad/s)
        self.calculate_fieldmap = MapNode(
            Function(
                input_names=['phasediff','magnitude','TE'],
                output_names=['out_file'],
                function=fsl_prepare_fieldmap
            ),
            iterfield=['phasediff','magnitude','TE'],
            name='calculate_fieldmap'
        )

        # apply mask to fieldmap image
        self.apply_mask = MapNode(
            fsl.ApplyMask(
                output_type='NIFTI_GZ'
            ),
            iterfield=['in_file','mask_file'],
            name='apply_mask'
        )

        # unmask fieldmap image through interpolation
        self.unmask = MapNode(
            fsl.FUGUE(
                save_unmasked_fmap=True,
                output_type='NIFTI_GZ'
            ),
            iterfield=['fmap_in_file','mask_file'],
            name='unmask'
        )

        # average epi image
        self.avg_epi = MapNode(
            fsl.MeanImage(
                output_type='NIFTI_GZ'
            ),
            iterfield=['in_file'],
            name='avg_epi'
        )

        # skullstrip average epi image
        self.skullstrip_avg_epi = MapNode(
            fsl.BET(
                robust=True,
                output_type="NIFTI_GZ",
            ),
            iterfield=['in_file'],
            name='skullstrip_avg_epi'
        )

        # register field map images to the averaged epi image
        self.register_magnitude = MapNode(
            fsl.FLIRT(
                output_type='NIFTI_GZ',
                dof=6
            ),
            iterfield=['in_file','reference'],
            name='register_magnitude'
        )
        self.register_fieldmap = MapNode(
            fsl.FLIRT(
                output_type='NIFTI_GZ',
                apply_xfm=True
            ),
            iterfield=['in_file','reference','in_matrix_file'],
            name='register_fieldmap'
        )
        self.register_mask = MapNode(
            fsl.FLIRT(
                output_type='NIFTI_GZ',
                apply_xfm=True,
                interp='nearestneighbour'
            ),
            iterfield=['in_file','reference','in_matrix_file'],
            name='register_mask'
        )

        # Warp average epi image with fieldmap
        self.warp_epi = MapNode(
            fsl.FUGUE(
                save_unmasked_shift=True,
                output_type='NIFTI_GZ'
            ),
            iterfield=['in_file','dwell_time','fmap_in_file','mask_file'],
            name='warp_epi'
        )

        # Make a warp image from field map
        self.make_warp_image = MapNode(
            fsl.FUGUE(
                output_type='NIFTI_GZ'
            ),
            iterfield=['in_file','dwell_time','fmap_in_file','mask_file'],
            name='make_warp_image'
        )

        self.convert_warp = MapNode(
            fsl.ConvertWarp(
                output_type='NIFTI_GZ'
            ),
            iterfield=['reference','shift_in_file'],
            name='convert_warp'
        )
