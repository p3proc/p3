from nipype import Workflow
from .nodedefs import definednodes
from ..base import workflowgenerator

class alignboldtoatlasworkflow(workflowgenerator):
    """ Defines the align bold to atlas workflow

        TODO

    """

    def __init__(self,name,settings):
        # call base constructor
        super().__init__(name,settings)

        # crete node definitions from settings
        self.dn = definednodes(settings)

        # connect the workflow
        self.workflow.connect([ # connect nodes
            # Create Atlas-Registered BOLD Data
            (self.dn.inputnode,self.dn.transformepi2epi2mpr2atl,[
                ('noskull_at','in_file')
            ]),
            (self.dn.inputnode,self.dn.transformepi2epi2mpr2atl,[
                ('oblique_transform','tfm1')
            ]),
            (self.dn.inputnode,self.dn.transformepi2epi2mpr2atl,[
                ('t1_2_epi','tfm2')
            ]),
            (self.dn.inputnode,self.dn.transformepi2epi2mpr2atl,[
                ('epi2epi1','tfm3')
            ]),
            (self.dn.inputnode,self.dn.alignepi2atl,[
                ('tcat','in_file')
            ]),
            (self.dn.transformepi2epi2mpr2atl,self.dn.alignepi2atl,[
                ('master_transform','in_matrix')
            ]),
            (self.dn.inputnode,self.dn.alignepi2atl,[
                ('noskull_at','reference')
            ]),

            # output to output node
            (self.dn.alignepi2atl,self.dn.outputnode,[
                ('out_file','epi_at')
            ])
        ])
