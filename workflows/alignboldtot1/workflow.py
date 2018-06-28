from nipype import Workflow
from .nodedefs import definednodes
from ..base import workflowgenerator

class alignboldtot1workflow(workflowgenerator):
    """ Defines the time shift and despike workflow

        TODO

    """

    def __init__(self,name,settings):
        # call base constructor
        super().__init__(name,settings)

        # crete node definitions from settings
        self.dn = definednodes(settings)

        # connect the workflow
        self.workflow.connect([ # connect nodes
            # Skullstrip the EPI image
            (self.dn.inputnode,self.dn.epi_skullstrip,[
                ('refimg','in_file')
            ]),
            (self.dn.inputnode,self.dn.epi_automask,[
                ('refimg','in_file')
            ]),
            (self.dn.epi_automask,self.dn.epi_3dcalc,[
                ('brain_file','in_file_a')
            ]),
            (self.dn.epi_skullstrip,self.dn.epi_3dcalc,[
                ('out_file','in_file_b')
            ]),
            (self.dn.inputnode,self.dn.epi_3dcalc,[
                ('refimg','in_file_c')
            ]),

            # deoblique
            (self.dn.epi_3dcalc,self.dn.warp,[
                ('out_file','card2oblique')
            ]),
            (self.dn.inputnode,self.dn.warp,[
                ('T1_0','in_file')
            ]),

            # resample the EPIREF to MPRAGE
            (self.dn.warp,self.dn.resample,[
                ('out_file','master')
            ]),
            (self.dn.epi_3dcalc,self.dn.resample,[
                ('out_file','in_file')
            ]),

            # create weightmask
            (self.dn.resample,self.dn.weightmask,[
                ('out_file','in_file')
            ]),
            (self.dn.epi_3dcalc,self.dn.weightmask,[
                ('out_file','no_skull')
            ]),

            # register mprage to tcat
            (self.dn.weightmask,self.dn.registert12tcat,[
                ('out_file','weight')
            ]),
            (self.dn.resample,self.dn.registert12tcat,[
                ('out_file','reference')
            ]),
            (self.dn.warp,self.dn.registert12tcat,[
                ('out_file','in_file')
            ]),

            # output to output node
            (self.dn.registert12tcat,self.dn.outputnode,[
                ('out_matrix','t1_2_epi')
            ]),
            (self.dn.warp,self.dn.outputnode,[
                ('ob_transform','oblique_transform')
            ]),
        ])
