from nipype import Workflow
from .nodedefs import definednodes
from ppp.base import workflowgenerator

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
           # Create Atlas-Registered BOLD Data
           (dn.inputnode,dn.applytransforms,[
               ('func_stc_despike','in_file')
           ]),
           (dn.inputnode,dn.applytransforms,[
               ('refimg','reference')
           ]),
           (dn.inputnode,dn.applytransforms,[
               ('warp_func_2_refimg','warp_func_2_refimg')
           ]),
           (dn.inputnode,dn.applytransforms,[
               ('affine_fmc','affine_fmc')
           ]),
           (dn.inputnode,dn.applytransforms,[
               ('warp_fmc','warp_fmc')
           ]),
           (dn.inputnode,dn.applytransforms,[
               ('affine_func_2_anat','affine_func_2_anat')
           ]),
           (dn.inputnode,dn.applytransforms,[
               ('warp_func_2_anat','warp_func_2_anat')
           ]),
           (dn.inputnode,dn.applytransforms,[
               ('affine_anat_2_atlas','affine_anat_2_atlas')
           ]),
           (dn.inputnode,dn.applytransforms,[
               ('warp_anat_2_atlas','warp_anat_2_atlas')
           ]),

           # output to output node
           (dn.applytransforms,dn.outputnode,[
               ('out_file','func_aligned')
           ]),

           # output to datasink
           (dn.applytransforms,dn.datasink,[
               ('out_file','p3.@func_aligned')
           ])
        ])

        # return workflow
        return cls.workflow
