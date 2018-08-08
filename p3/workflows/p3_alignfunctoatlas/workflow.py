from nipype import Workflow
from .nodedefs import definednodes
from p3.base import workflowgenerator

class alignfunctoatlasworkflow(workflowgenerator):
    """ Defines the align functional image to atlas workflow

        TODO

    """

    def __new__(cls,name,settings):
        # call base constructor
        super().__new__(cls,name,settings)

        # create node definitions from settings
        dn = definednodes(settings)

        # connect the workflow
        cls.workflow.connect([ # connect nodes
            # get the resolution of the refimg
            (dn.inputnode,dn.get_resolution,[
                ('refimg','reference')
            ]),

            # resample the atlas
            (dn.get_resolution,dn.resample,[
                ('resolution','apply_isoxfm')
            ]),

            # format the reference
            (dn.inputnode,dn.format_reference,[
                ('func','func')
            ]),
            (dn.resample,dn.format_reference,[
                ('out_file','reference')
            ]),

            # combine transforms
            (dn.inputnode,dn.combinetransforms,[
                ('func','func')
            ]),
            (dn.resample,dn.combinetransforms,[
                ('out_file','reference')
            ]),
            (dn.format_reference,dn.combinetransforms,[
                ('dim4','dim4')
            ]),
            (dn.format_reference,dn.combinetransforms,[
                ('TR','TR')
            ]),
            (dn.inputnode,dn.combinetransforms,[
                ('warp_fmc','warp_fmc')
            ]),
            (dn.inputnode,dn.combinetransforms,[
                ('affine_func_2_anat','affine_func_2_anat')
            ]),
            (dn.inputnode,dn.combinetransforms,[
                ('affine_anat_2_atlas','affine_anat_2_atlas')
            ]),
            (dn.inputnode,dn.combinetransforms,[
                ('warp_anat_2_atlas','warp_anat_2_atlas')
            ]),

            # create dfnd mask
            (dn.inputnode,dn.create_dfnd_mask,[
                ('refimg','refimg')
            ]),
            (dn.inputnode,dn.create_dfnd_mask,[
                ('affine_func_2_anat','affine_func_2_anat')
            ]),
            (dn.inputnode,dn.create_dfnd_mask,[
                ('affine_anat_2_atlas','affine_anat_2_atlas')
            ]),
            (dn.inputnode,dn.create_dfnd_mask,[
                ('warp_anat_2_atlas','warp_anat_2_atlas')
            ]),
            (dn.resample,dn.create_dfnd_mask,[
                ('out_file','reference')
            ]),

            # Create Atlas-Registered BOLD Data
            (dn.inputnode,dn.applytransforms,[
               ('func_stc_despike','in_file')
            ]),
            (dn.format_reference,dn.applytransforms,[
               ('formatted_reference','reference4D')
            ]),
            (dn.combinetransforms,dn.applytransforms,[
               ('combined_transforms4D','combined_transforms4D')
            ]),
            (dn.inputnode,dn.applytransforms,[
                ('warp_func_2_refimg','warp_func_2_refimg')
            ]),
            (dn.create_dfnd_mask,dn.applytransforms,[
                ('mask_file','dfnd_mask')
            ]),

            # output to output node
            (dn.applytransforms,dn.outputnode,[
               ('out_file','func_atlas')
            ]),

            # output to datasink
            (dn.applytransforms,dn.datasink,[
               ('out_file','p3.@func_atlas')
            ]),
            (dn.resample,dn.datasink,[
               ('out_file','p3.@atlas_resampled')
            ])
        ])

        # return workflow
        return cls.workflow
