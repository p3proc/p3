from nipype import Workflow
from .nodedefs import definednodes
from p3.base import workflowgenerator

class fieldmapcorrectionworkflow(workflowgenerator):
    """ Defines the field map correction workflow

        TODO

    """

    def __new__(cls,name,settings):
        # call base constructor
        super().__new__(cls,name,settings)

        # create node definitions from settings
        dn = definednodes(settings)

        # do field map correction if enabled
        if settings['field_map_correction']:
            # connect the workflow
            cls.workflow.connect([ # connect nodes
                # get the magnitude and phase images
                (dn.inputnode,dn.get_metadata,[
                    ('func','epi_file')
                ]),

                # skullstrip the magnitude image
                (dn.get_metadata,dn.skullstrip_magnitude,[
                    ('magnitude','in_file')
                ]),

                # erode the magnitude image
                (dn.skullstrip_magnitude,dn.erode_magnitude[0],[
                    ('out_file','in_file')
                ]),
                (dn.erode_magnitude[0],dn.erode_magnitude[1],[
                    ('out_file','in_file')
                ]),
                (dn.erode_magnitude[1],dn.erode_magnitude[2],[
                    ('out_file','in_file')
                ]),

                # create mask from eroded mag image
                (dn.erode_magnitude[2],dn.create_mask,[
                    ('out_file','in_file')
                ]),

                # create fieldmap image
                (dn.get_metadata,dn.calculate_fieldmap,[
                    ('phasediff','phasediff'),
                    ('TE','TE')
                ]),
                (dn.erode_magnitude[2],dn.calculate_fieldmap,[
                    ('out_file','magnitude')
                ]),

                # apply mask to fieldmap image
                (dn.calculate_fieldmap,dn.apply_mask,[
                    ('out_file','in_file')
                ]),
                (dn.create_mask,dn.apply_mask,[
                    ('out_file','mask_file')
                ]),

                # unmask fieldmap image through interpolation
                (dn.apply_mask,dn.unmask,[
                    ('out_file','fmap_in_file')
                ]),
                (dn.create_mask,dn.unmask,[
                    ('out_file','mask_file')
                ]),

                # avg epi image and skullstrip
                (dn.inputnode,dn.avg_epi,[
                    ('func_aligned','in_file')
                ]),
                (dn.avg_epi,dn.skullstrip_avg_epi,[
                    ('out_file','in_file')
                ]),

                # register fieldmap outputs to avg epi
                (dn.erode_magnitude[2],dn.register_magnitude,[ # magnitude image
                    ('out_file','in_file')
                ]),
                (dn.skullstrip_avg_epi,dn.register_magnitude,[
                    ('out_file','reference')
                ]),
                (dn.unmask,dn.register_fieldmap,[ # fieldmap image
                    ('fmap_out_file','in_file')
                ]),
                (dn.register_magnitude,dn.register_fieldmap,[
                    ('out_matrix_file','in_matrix_file')
                ]),
                (dn.skullstrip_avg_epi,dn.register_fieldmap,[
                    ('out_file','reference')
                ]),
                (dn.create_mask,dn.register_mask,[ # mask image
                    ('out_file','in_file')
                ]),
                (dn.register_magnitude,dn.register_mask,[
                    ('out_matrix_file','in_matrix_file')
                ]),
                (dn.skullstrip_avg_epi,dn.register_mask,[
                    ('out_file','reference')
                ]),

                # Warp the refimg with fieldmap
                (dn.avg_epi,dn.unwarp_epis,[
                    ('out_file','in_file')
                ]),
                (dn.get_metadata,dn.unwarp_epis,[
                    ('echospacing','dwell_time')
                ]),
                (dn.register_fieldmap,dn.unwarp_epis,[
                    ('out_file','fmap_in_file')
                ]),
                (dn.register_mask,dn.unwarp_epis,[
                    ('out_file','mask_file')
                ]),
                (dn.get_metadata,dn.unwarp_epis,[
                    ('ped','unwarp_direction')
                ]),

                # convert to ants warp
                (dn.get_metadata,dn.convertvsm2antswarp,[
                    ('ped','ped')
                ]),
                (dn.unwarp_epis,dn.convertvsm2antswarp,[
                    ('shift_out_file','in_file')
                ]),

                # apply ants unwarp warp
                (dn.avg_epi,dn.applyantsunwarp,[
                    ('out_file','input_image')
                ]),
                (dn.avg_epi,dn.applyantsunwarp,[
                    ('out_file','reference_image')
                ]),
                (dn.convertvsm2antswarp,dn.applyantsunwarp,[
                    ('out_file','transforms')
                ]),

                # get refimg transform
                (dn.convertvsm2antswarp,dn.get_refimg_transform,[
                    ('out_file','transforms')
                ]),

                # apply unwarp to refimg
                (dn.inputnode,dn.applyantsunwarprefimg,[
                    ('refimg','input_image')
                ]),
                (dn.inputnode,dn.applyantsunwarprefimg,[
                    ('refimg','reference_image')
                ]),
                (dn.get_refimg_transform,dn.applyantsunwarprefimg,[
                    ('transform','transforms')
                ]),

                # create the basename
                (dn.applyantsunwarp,dn.create_prefix,[
                    ('output_image','filename')
                ]),

                # realign images to the unwarped reference image
                (dn.create_prefix,dn.realign,[
                    ('basename','output_prefix')
                ]),
                (dn.applyantsunwarprefimg,dn.realign,[
                    ('output_image','fixed_image')
                ]),
                (dn.applyantsunwarp,dn.realign,[
                    ('output_image','moving_image')
                ]),

                # combine the unwarp and realign into one transform
                (dn.avg_epi,dn.combine_transforms,[
                    ('out_file','avgepi')
                ]),
                (dn.applyantsunwarp,dn.combine_transforms,[
                    ('output_image','reference')
                ]),
                (dn.convertvsm2antswarp,dn.combine_transforms,[
                    ('out_file','unwarp')
                ]),
                (dn.realign,dn.combine_transforms,[
                    ('out_matrix','realign')
                ]),

                # output to datasink
                (dn.realign,dn.datasink,[
                    ('warped_image','p3_QC.fieldmapcorrection.@unwarped_realigned')
                ]),
                (dn.applyantsunwarprefimg,dn.datasink,[
                    ('output_image','p3_QC.fieldmapcorrection.@unwarped_refimg')
                ]),
                (dn.applyantsunwarp,dn.datasink,[
                    ('output_image','p3_QC.fieldmapcorrection.@unwarped')
                ]),
                (dn.avg_epi,dn.datasink,[
                    ('out_file','p3_QC.fieldmapcorrection.@avgimg')
                ]),
                (dn.inputnode,dn.datasink,[
                    ('refimg','p3_QC.fieldmapcorrection.@refimg')
                ]),

                # Output unwarp outputs for fmc to output node
                (dn.applyantsunwarprefimg,dn.outputnode,[
                    ('output_image','refimg')
                ]),
                (dn.combine_transforms,dn.outputnode,[
                    ('fmc_warp','warp_fmc')
                ])
            ])
        else:
            # connect the workflow
            cls.workflow.connect([ # connect nodes
                # skip field map correction
                (dn.inputnode,dn.outputnode,[
                    ('func_aligned','func_aligned'),
                    ('refimg','refimg'),
                ])
            ])

        # return workflow
        return cls.workflow
