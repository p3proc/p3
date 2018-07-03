from nipype import Workflow
from .nodedefs import definednodes
from ppp.base import workflowgenerator

class alignboldtoatlasworkflow(workflowgenerator):
    """ Defines the align bold to atlas workflow

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
            (dn.inputnode,dn.transformepi2epi2mpr2atl,[
                ('noskull_at','in_file')
            ]),
            (dn.inputnode,dn.transformepi2epi2mpr2atl,[
                ('oblique_transform','tfm1')
            ]),
            (dn.inputnode,dn.transformepi2epi2mpr2atl,[
                ('t1_2_epi','tfm2')
            ]),
            (dn.inputnode,dn.transformepi2epi2mpr2atl,[
                ('epi2epi1','tfm3')
            ]),
            (dn.inputnode,dn.alignepi2atl,[
                ('tcat','in_file')
            ]),
            (dn.transformepi2epi2mpr2atl,dn.alignepi2atl,[
                ('master_transform','in_matrix')
            ]),
            (dn.inputnode,dn.alignepi2atl,[
                ('noskull_at','reference')
            ]),

            # output to output node
            (dn.alignepi2atl,dn.outputnode,[
                ('out_file','epi_at')
            ])
        ])

        # return workflow
        return cls.workflow
