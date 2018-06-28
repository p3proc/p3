from nipype import Workflow
from .nodedefs import definednodes
from ..base import workflowgenerator

class alignt1toatlasworkflow(workflowgenerator):
    """ Defines the align t1 to atlas workflow

        TODO

    """

    def __init__(self,name,settings):
        # call base constructor
        super().__init__(name,settings)

        # crete node definitions from settings
        self.dn = definednodes(settings)

        # connect the workflow
        self.workflow.connect([ # connect nodes
            # Register the (1st) final skullstripped mprage to atlas
            (self.dn.inputnode,self.dn.select0T1,[
                ('T1','T1_list')
            ]),
            (self.dn.select0T1,self.dn.register,[
                ('T1_0','in_file')
            ]),

            # output to output node
            (self.dn.register,self.dn.outputnode,[
                ('out_file','noskull_at'),
                ('transform_file','t1_2_atlas_transform')
            ]),
            (self.dn.select0T1,self.dn.outputnode,[
                ('T1_0','T1_0')
            ])
        ])
