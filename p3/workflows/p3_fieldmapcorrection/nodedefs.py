"""Define Nodes for time shift and despike workflow

TODO

"""
import os
from p3.base import basenodedefs
from .custom import *
from nipype import Node,MapNode
from nipype.interfaces import afni,fsl,ants
from nipype.interfaces.utility import Function,IdentityInterface
from nipype.workflows.dmri.fsl.utils import vsm2warp

class definednodes(basenodedefs):
    """Class initializing all nodes in workflow

        TODO

    """

    def __init__(self,settings):
        # call base constructor
        super().__init__(settings)

        # define input/output node
        self.set_input(['func','refimg','func_aligned'])
        self.set_output(['warp_fmc','refimg'])

        # define datasink substitutions
        self.set_subs([
            ('_roi','_reference'),
            ('_Warped_mean','_moco'),
            ('_Warped','_realign')
        ])

        # define regex substitutions
        self.set_resubs([
            (r'_avg_epi\d{1,3}',''),
            (r'_applyantsunwarp\d{1,3}',''),
            (r'_realign\d{1,3}','')
        ])

        # get magnitude and phase
        self.get_metadata = MapNode(
            Function(
                input_names=['epi_file','bids_dir'],
                output_names=['magnitude','phasediff','TE','echospacing','ped'],
                function=get_metadata
            ),
            iterfield=['epi_file'],
            name='get_metadata'
        )
        self.get_metadata.inputs.bids_dir = settings['bids_dir']

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

        # unwarp epis fieldmap
        self.unwarp_epis = MapNode(
            fsl.FUGUE(
                save_shift=True,
                output_type='NIFTI_GZ'
            ),
            iterfield=['in_file','dwell_time','fmap_in_file','mask_file','unwarp_direction'],
            name='unwarp_epis'
        )

        # Convert vsm to ANTS warp
        self.convertvsm2antswarp = MapNode(
            Function(
                input_names=['in_file','ped'],
                output_names=['out_file'],
                function=convertvsm2ANTSwarp
            ),
            iterfield=['in_file','ped'],
            name='convertvsm2antswarp'
        )

        # apply fmc ant warp
        self.applyantsunwarp = MapNode(
            ants.ApplyTransforms(
                out_postfix='_unwarped',
                num_threads=settings['num_threads']
            ),
            iterfield=['input_image','reference_image','transforms'],
            name='applyantsunwarp'
        )
        self.applyantsunwarp.n_procs = settings['num_threads']

        # get refimg transform
        self.get_refimg_transform = Node(
            Function(
                input_names=['transforms','run'],
                output_names=['transform'],
                function=lambda transforms,run: transforms[run]
            ),
            name='get_refimg_transform'
        )
        self.get_refimg_transform.inputs.run = settings['func_reference_run']

        # apply fmc ant warp to refimg
        self.applyantsunwarprefimg = Node(
            ants.ApplyTransforms(
                out_postfix='_unwarped',
                num_threads=settings['num_threads']
            ),
            name='applyantsunwarprefimg'
        )
        self.applyantsunwarprefimg.n_procs = settings['num_threads']

        # create the output name for the realignment
        self.create_prefix = MapNode(
            Function(
                input_names=['filename'],
                output_names=['basename'],
                function=get_prefix
            ),
            iterfield=['filename'],
            name='create_prefix'
        )

        # realiqn unwarped to refimgs
        self.realign = MapNode(
            ants.RegistrationSynQuick(
                transform_type='a',
                num_threads=settings['num_threads']
            ),
            iterfield=['moving_image','output_prefix'],
            name='realign'
        )
        self.realign.n_procs = settings['num_threads']

        # combine transforms
        self.combine_transforms = MapNode(
            Function(
                input_names=['avgepi','reference','unwarp','realign'],
                output_names=['fmc_warp'],
                function=combinetransforms
            ),
            iterfield=['avgepi','reference','unwarp','realign'],
            name='combine_transforms'
        )
        self.combine_transforms.n_procs = settings['num_threads']
