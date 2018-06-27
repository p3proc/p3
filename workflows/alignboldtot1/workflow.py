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
            # Skullstrip the EPI image
            (p3.firstframefirstrun,p3.epi_skullstrip,[
                ('refimg','in_file')
            ]),
            (p3.firstframefirstrun,p3.epi_automask,[
                ('refimg','in_file')
            ]),
            (p3.epi_automask,p3.epi_3dcalc,[
                ('brain_file','in_file_a')
            ]),
            (p3.epi_skullstrip,p3.epi_3dcalc,[
                ('out_file','in_file_b')
            ]),
            (p3.firstframefirstrun,p3.epi_3dcalc,[
                ('refimg','in_file_c')
            ]),

            # deoblique
            (p3.epi_3dcalc,p3.warp,[
                ('out_file','card2oblique')
            ]),
            (p3.select0T1,p3.warp,[
                ('T1_0','in_file')
            ]),
            (p3.warp,p3.noskull_obla2e,[
                ('out_file','noskull_ob'),
                ('ob_transform','noskull_obla2e_mat')
            ]),

            # resample the EPIREF to MPRAGE
            (p3.noskull_obla2e,p3.resample,[
                ('noskull_ob','master')
            ]),
            (p3.epi_3dcalc,p3.resample,[
                ('out_file','in_file')
            ]),

            # create weightmask
            (p3.resample,p3.weightmask,[
                ('out_file','in_file')
            ]),
            (p3.epi_3dcalc,p3.weightmask,[
                ('out_file','no_skull')
            ]),

            # register mprage to tcat
            (p3.weightmask,p3.registert12tcat,[
                ('out_file','weight')
            ]),
            (p3.resample,p3.registert12tcat,[
                ('out_file','reference')
            ]),
            (p3.noskull_obla2e,p3.registert12tcat,[
                ('noskull_ob','in_file')
            ]),
        ])
