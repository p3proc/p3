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
            (dn.inputnode,dn.transformepi2mpr2atl,[
                ('noskull_at','in_file')
            ]),
            (dn.inputnode,dn.transformepi2mpr2atl,[
                ('oblique_transform','tfm1')
            ]),
            (dn.inputnode,dn.transformepi2mpr2atl,[
                ('t1_2_epi','tfm2')
            ]),
            (dn.inputnode,dn.transformepi2mpr2atl,[
                ('epi2epi1','tfm3')
            ]),
            (dn.inputnode,dn.alignepi2atl,[
                ('tcat','in_file')
            ]),
            (dn.transformepi2mpr2atl,dn.alignepi2atl,[
                ('master_transform','in_matrix')
            ]),
            (dn.inputnode,dn.alignepi2atl,[
                ('noskull_at','reference')
            ]),

            # output to output node
            (dn.alignepi2atl,dn.outputnode,[
                ('out_file','epi_at')
            ]),

            # output to datasink
            (dn.alignepi2atl,dn.datasink,[
                ('out_file','p3.@epi')
            ])
        ])

        # if nonlinear transform set
        if settings['nonlinear_atlas']:
            cls.workflow.connect([
                # apply nonlinear transform
                (dn.alignepi2atl,dn.applyQwarptransform,[
                    ('out_file','in_file')
                ]),
                (dn.inputnode,dn.applyQwarptransform,[
                    ('nonlin_warp','warped_file')
                ]),

                # output to output node
                (dn.applyQwarptransform,dn.outputnode,[
                    ('out_file','epi_Qwarp')
                ]),

                # output to datasink
                (dn.outputnode,dn.datasink,[
                    ('epi_Qwarp','p3.@epi_Qwarp')
                ])
            ])

        # return workflow
        return cls.workflow
