from nipype import Workflow
from .nodedefs import definednodes
from ppp.base import workflowgenerator

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
                (dn.inputnode,dn.getmagandphase,[
                    ('epi','epi_file')
                ]),

                # skullstrip the magnitude image
                (dn.getmagandphase,dn.skullstrip_magnitude,[
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
                (dn.getmagandphase,dn.calculate_fieldmap,[
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
                    ('epi_aligned','in_file')
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

                # Warp average epi image with fieldmap
                (dn.skullstrip_avg_epi,dn.warp_epi,[
                    ('out_file','in_file')
                ]),
                (dn.getmagandphase,dn.warp_epi,[
                    ('echospacing','dwell_time')
                ]),
                (dn.register_fieldmap,dn.warp_epi,[
                    ('out_file','fmap_in_file')
                ]),
                (dn.register_mask,dn.warp_epi,[
                    ('out_file','mask_file')
                ]),

                # Save out unwarped file
                (dn.warp_epi,dn.datasink,[
                    ('unwarped_file','p3_QC.@unwarped_avg_epi')
                ])
            ])
        else:
            # connect the workflow
            cls.workflow.connect([ # connect nodes
                # skip field map correction
                (dn.inputnode,dn.outputnode,[
                    ('epi','epi')
                ])
            ])

        # return workflow
        return cls.workflow
