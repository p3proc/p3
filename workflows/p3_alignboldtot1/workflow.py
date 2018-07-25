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

            # align epi 2 anat
            (dn.epi_3dcalc,dn.align_epi_2_anat,[ # skullstripped epi
                ('out_file','in_file')
            ]),
            #(dn.inputnode,dn.align_epi_2_anat,[ # unskullstripped epi
            #    ('refimg','in_file')
            #]),
            (dn.inputnode,dn.align_epi_2_anat,[ # skullstripped T1
                ('T1_0','anat')
            ]),

            # output to output node
            (dn.align_epi_2_anat,dn.outputnode,[
                ('epi_al_mat','epi_2_t1')
            ]),

            # output to QC datasink
            (dn.epi_3dcalc,dn.datasink,[
                ('out_file','p3_QC.@epi_skullstrip')
            ]),
            (dn.align_epi_2_anat,dn.datasink,[
                ('epi_al_mat','p3_QC.@epi_2_t1')
            ]),
            (dn.align_epi_2_anat,dn.datasink,[
                ('epi_al_orig','p3_QC.@epi_2_t1_img')
            ])
        ])

        # return workflow
        return cls.workflow
