"""Define Nodes for time shift and despike workflow

TODO

"""
import os
from ppp.base import basenodedefs
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
        self.set_output(['affine_fmc','warp_fmc','refimg'])

        # define datasink substitutions
        # self.set_subs([])

        # define datasink regular expression substitutions
        #self.set_resubs([
        #    (r'_warp_epi\d{1,3}','')
        #])

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

        # get the values to warp the refimg (the refimg is indexed at 0)
        self.get_refimg_files = Node(
            Function(
                input_names=['dwell_time','fmap_in_file','mask_file','ped'],
                output_names=['dwell_time','fmap_in_file','mask_file','ped'],
                function=lambda dwell_time,fmap_in_file,mask_file,ped: (dwell_time[0],fmap_in_file[0],mask_file[0],ped[0])
            ),
            name='get_refimg_files'
        )

        # Warp reference image with fieldmap
        self.warp_refimg = Node(
            fsl.FUGUE(
                save_shift=True,
                output_type='NIFTI_GZ'
            ),
            name='warp_refimg'
        )

        # align the (NOTE: I'm not sure if this is valid, but it was the only way I could get a ANTS warp compatible FMC)
        self.ants_fmc = Node(
            ants.RegistrationSynQuick(
                num_threads=settings['num_threads']
            ),
            name='ants_fmc'
        )
