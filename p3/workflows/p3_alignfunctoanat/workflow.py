from nipype import Workflow
from .nodedefs import definednodes
from p3.base import workflowgenerator

class alignfunctoanatworkflow(workflowgenerator):
    """ Defines the functional alignment to anatomy alignment workflow

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

            # align func 2 anat
            (dn.epi_3dcalc,dn.create_prefix,[
                ('out_file','filename')
            ]),
            (dn.create_prefix,dn.align_func_2_anat,[ # set output prefix
                ('basename','output_transform_prefix')
            ]),
            (dn.epi_3dcalc,dn.align_func_2_anat,[ # skullstripped epi
                ('out_file','moving_image')
            ]),
            (dn.inputnode,dn.align_func_2_anat,[ # skullstripped T1
                ('T1_skullstrip','fixed_image')
            ]),

            # output to output node
            (dn.align_func_2_anat,dn.outputnode,[
                ('composite_transform','affine_func_2_anat')
            ]),

            # output to QC datasink
            (dn.epi_3dcalc,dn.datasink,[
                ('out_file','p3_QC.alignfunctoanat.@epi_skullstrip')
            ]),
            (dn.align_func_2_anat,dn.datasink,[
                ('warped_image','p3_QC.alignfunctoanat.@epi_aligned_t1')
            ]),
            (dn.inputnode,dn.datasink,[
                ('T1_skullstrip','p3_QC.alignfunctoanat.@T1')
            ])
        ])

        # return workflow
        return cls.workflow
