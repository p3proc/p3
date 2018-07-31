from nipype import Workflow
from .nodedefs import definednodes
from p3.base import workflowgenerator

class alignanattoatlasworkflow(workflowgenerator):
    """ Defines the align anatomy image to atlas workflow

        TODO

    """

    def __new__(cls,name,settings):
        # call base constructor
        super().__new__(cls,name,settings)

        # create node definitions from settings
        dn = definednodes(settings)

        # connect the workflow
        cls.workflow.connect([ # connect nodes
            # Register the (1st) final skullstripped mprage to atlas
            (dn.inputnode,dn.create_prefix,[
                ('T1_skullstrip','filename')
            ]),
            (dn.create_prefix,dn.register,[
                ('basename','output_prefix')
            ]),
            (dn.inputnode,dn.register,[
                ('T1_skullstrip','moving_image')
            ]),

            # output to output node
            (dn.register,dn.outputnode,[
                ('out_matrix','affine_anat_2_atlas')
            ]),
            (dn.register,dn.outputnode,[
                ('forward_warp_field','warp_anat_2_atlas')
            ]),
            (dn.register,dn.outputnode,[
                ('warped_image','anat_atlas')
            ]),

            # output T1 atlas alignment to p3 output
            (dn.register,dn.datasink,[
                ('warped_image','p3.@T1_at')
            ])
        ])

        # return workflow
        return cls.workflow
