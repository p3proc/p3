from nipype import Workflow
from .nodedefs import definednodes

class alignboldtot1workflow(workflowgenerator):
    """ Defines the time shift and despike workflow

        TODO

    """

    def __init__(name,settings):
        # call base constructor
        super().__init__(name,settings)

        # crete node definitions from settings
        self.dn = definednodes(settings)

        # connect the workflow
        self.workflow.connect([ # connect nodes
            # Create Atlas-Registered BOLD Data
            (p3.skullstripped_atlas_mprage,p3.transformepi2epi2mpr2atl,[
                ('noskull_at','in_file')
            ]),
            (p3.noskull_obla2e,p3.transformepi2epi2mpr2atl,[
                ('noskull_obla2e_mat','tfm1')
            ]),
            (p3.registert12tcat,p3.transformepi2epi2mpr2atl,[
                ('out_matrix','tfm2')
            ]),
            (p3.volreg,p3.transformepi2epi2mpr2atl,[
                ('oned_matrix_save','tfm3')
            ]),
            (p3.tshift,p3.alignepi2atl,[
                ('out_file','in_file')
            ]),
            (p3.transformepi2epi2mpr2atl,p3.alignepi2atl,[
                ('master_transform','in_matrix')
            ]),
            (p3.skullstripped_atlas_mprage,p3.alignepi2atl,[
                ('noskull_at','reference')
            ]),

            (p3.skullstripped_atlas_mprage,p3.output[0],[
                ('noskull_at','output')
            ])
        ])
