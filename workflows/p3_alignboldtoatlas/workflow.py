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
        #cls.workflow.connect([ # connect nodes
        #    # Create Atlas-Registered BOLD Data
        #    (dn.inputnode,dn.applymastertransform,[
        #        ('tcat','in_file')
        #    ]),
        #    (dn.inputnode,dn.applymastertransform,[
        #        ('noskull_at','reference')
        #    ]),
        #    (dn.inputnode,dn.applymastertransform,[
        #        ('nonlin_warp','tfm0')
        #    ]),
        #    (dn.inputnode,dn.applymastertransform,[
        #        ('t1_2_atlas_transform','tfm1')
        #    ]),
        #    (dn.inputnode,dn.applymastertransform,[
        #        ('epi_2_t1','tfm2')
        #    ]),
        #    (dn.inputnode,dn.applymastertransform,[
        #        ('fmc','tfm3')
        #    ]),
        #    (dn.inputnode,dn.applymastertransform,[
        #        ('epi2epi1','tfm4')
        #    ]),
        #
        #    # output to output node
        #    (dn.applymastertransform,dn.outputnode,[
        #        ('out_file','epi_at')
        #    ]),
        #
        #    # output to datasink
        #    (dn.applymastertransform,dn.datasink,[
        #        ('out_file','p3.@epi')
        #    ])
        #])

        # return workflow
        return cls.workflow
