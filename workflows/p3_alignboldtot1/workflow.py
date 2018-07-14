from nipype import Workflow
from .nodedefs import definednodes
from ppp.base import workflowgenerator

class alignboldtot1workflow(workflowgenerator):
    """ Defines the time shift and despike workflow

        TODO

    """

    def __new__(cls,name,settings):
        # call base constructor
        super().__new__(cls,name,settings)

        # create node definitions from settings
        dn = definednodes(settings)

        # connect the workflow
        cls.workflow.connect([ # connect nodes
            # Skullstrip the EPI image
            (dn.inputnode,dn.epi_skullstrip,[
                ('refimg','in_file')
            ]),
            (dn.inputnode,dn.epi_automask,[
                ('refimg','in_file')
            ]),
            (dn.epi_automask,dn.epi_3dcalc,[
                ('brain_file','in_file_a')
            ]),
            (dn.epi_skullstrip,dn.epi_3dcalc,[
                ('out_file','in_file_b')
            ]),
            (dn.inputnode,dn.epi_3dcalc,[
                ('refimg','in_file_c')
            ]),

            # deoblique
            (dn.epi_3dcalc,dn.warp,[
                ('out_file','card2oblique')
            ]),
            (dn.inputnode,dn.warp,[
                ('T1_0','in_file')
            ]),

            # resample the EPIREF to MPRAGE
            (dn.warp,dn.resample,[
                ('out_file','master')
            ]),
            (dn.epi_3dcalc,dn.resample,[
                ('out_file','in_file')
            ]),

            # create weightmask
            (dn.resample,dn.weightmask,[
                ('out_file','in_file')
            ]),
            (dn.epi_3dcalc,dn.weightmask,[
                ('out_file','no_skull')
            ]),

            # register mprage to tcat
            (dn.weightmask,dn.registert12tcat,[
                ('out_file','weight')
            ]),
            (dn.resample,dn.registert12tcat,[
                ('out_file','reference')
            ]),
            (dn.warp,dn.registert12tcat,[
                ('out_file','in_file')
            ]),

            # output to output node
            (dn.registert12tcat,dn.outputnode,[
                ('out_matrix','t1_2_epi')
            ]),
            (dn.warp,dn.outputnode,[
                ('ob_transform','oblique_transform')
            ]),

            # output to QC datasink
            (dn.resample,dn.datasink,[
                ('out_file','p3_QC.@epi_skullstrip_resample')
            ]),
            (dn.registert12tcat,dn.datasink,[
                ('out_matrix','p3_QC.@t1_2_epi')
            ]),
            (dn.warp,dn.datasink,[
                ('ob_transform','p3_QC.@oblique_transform')
            ])
        ])

        # return workflow
        return cls.workflow
