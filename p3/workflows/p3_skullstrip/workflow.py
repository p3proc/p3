from nipype import Workflow
from .nodedefs import definednodes
from p3.base import workflowgenerator

class skullstripworkflow(workflowgenerator):
    """ Defines the skullstrip workflow

        TODO

    """

    def __new__(cls,name,settings):
        # call base constructor
        super().__new__(cls,name,settings)

        # create node definitions from settings
        dn = definednodes(settings)

        # connect the workflow
        cls.workflow.connect([ # connect nodes
            ### Skullstrip
            # AFNI skull stripped images are missing edge of cortical ribbon often
            # FSL has more of the ribbon often but can have weird neck stuff too
            # Freesurfer rarely clips and is the most lenient of the skullstrips
            (dn.inputnode,dn.afni_skullstrip,[
                ('T1','in_file')
            ]),
            (dn.inputnode,dn.fsl_skullstrip,[
                ('T1','in_file')
            ]),

            ### REGISTER THE MPRAGE TO THE ATLAS
            # Create transformation of FSorig to T1
            (dn.inputnode,dn.allineate_orig,[
                ('orig','in_file')
            ]),
            (dn.inputnode,dn.allineate_orig,[
                ('T1','reference')
            ]),
            (dn.afni_skullstrip,dn.refit_setup,[
                ('out_file','noskull_T1')
            ]),

            # create atlas-aligned skull stripped brainmask
            (dn.inputnode,dn.allineate_bm,[
                ('brainmask','in_file')
            ]),
            (dn.inputnode,dn.allineate_bm,[
                ('T1','reference')
            ]),
            (dn.allineate_orig,dn.allineate_bm,[
                ('out_matrix','in_matrix')
            ]),
            (dn.refit_setup,dn.refit,[
                ('refit_input','atrcopy')
            ]),
            (dn.allineate_bm,dn.refit,[
                ('out_file','in_file')
            ]),

            # intensities are differently scaled in FS image, replace with native intensities for uniformity
            (dn.inputnode,dn.uniform,[
                ('T1','in_file_a')
            ]),
            (dn.refit,dn.uniform,[
                ('out_file','in_file_b')
            ]),

            # Use OR of AFNI, FSL, and FS skullstrips within a 3-shell expanded AFNI mask as final
            (dn.afni_skullstrip,dn.maskop1,[
                ('out_file','in_file_a')
            ]),
            (dn.maskop1,dn.maskop2[0],[
                ('out_file','in_file_a')
            ]),
            (dn.maskop2[0],dn.maskop2[1],[
                ('out_file','in_file_a')
            ]),
            (dn.maskop2[1],dn.maskop2[2],[
                ('out_file','in_file_a')
            ]),
            (dn.fsl_skullstrip,dn.maskop3,[
                ('out_file','in_file_a')
            ]),
            (dn.afni_skullstrip,dn.maskop3,[
                ('out_file','in_file_b')
            ]),
            (dn.uniform,dn.maskop3,[
                ('out_file','in_file_c')
            ]),
            (dn.maskop2[2],dn.maskop4,[
                ('out_file','in_file_a')
            ]),
            (dn.maskop3,dn.maskop4,[
                ('out_file','in_file_b')
            ]),
            (dn.inputnode,dn.maskop4,[
                ('T1','in_file_c')
            ]),

            # convert T1 list to string
            (dn.maskop4,dn.select0T1,[
                ('out_file','T1_list')
            ]),

            # apply n4 bias field correction
            (dn.select0T1,dn.biasfieldcorrect,[
                ('T1_0','input_image')
            ]),

            # output to output node
            (dn.biasfieldcorrect,dn.outputnode,[
                ('output_image','T1_skullstrip')
            ]),

            # save out skullstrip + original
            (dn.inputnode,dn.datasink,[ # original image
                ('T1','p3_QC.skullstrip.@T1')
            ]),
            (dn.select0T1,dn.datasink,[ # skullstriped file
                ('T1_0','p3_QC.skullstrip.@skullstrip')
            ]),
            (dn.biasfieldcorrect,dn.datasink,[ # bias field corrected image
                ('output_image','p3_QC.skullstrip.@biasfieldcorrect')
            ])
        ])

        # return workflow
        return cls.workflow
