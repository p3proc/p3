from nipype import Workflow
from .nodedefs import definednodes
from ..base import workflowgenerator

class skullstripworkflow(workflowgenerator):
    """ Defines the skullstrip workflow

        TODO

    """

    def __init__(self,name,settings):
        # call base constructor
        super().__init__(name,settings)

        # crete node definitions from settings
        self.dn = definednodes(settings)

        # connect the workflow
        self.workflow.connect([ # connect nodes
            ### Skullstrip
            # AFNI skull stripped images are missing edge of cortical ribbon often
            # FSL has more of the ribbon often but can have weird neck stuff too
            # Freesurfer rarely clips and is the most lenient of the skullstrips
            (self.dn.inputnode,self.dn.afni_skullstrip,[
                ('T1','in_file')
            ]),
            (self.dn.inputnode,self.dn.fsl_skullstrip,[
                ('T1','in_file')
            ]),

            ### REGISTER THE MPRAGE TO THE ATLAS
            # Create transformation of FSorig to T1
            (self.dn.inputnode,self.dn.allineate_orig,[
                ('orig','in_file')
            ]),
            (self.dn.inputnode,self.dn.allineate_orig,[
                ('T1','reference')
            ]),
            (self.dn.afni_skullstrip,self.dn.refit_setup,[
                ('out_file','noskull_T1')
            ]),

            # create atlas-aligned skull stripped brainmask
            (self.dn.inputnode,self.dn.allineate_bm,[
                ('brainmask','in_file')
            ]),
            (self.dn.inputnode,self.dn.allineate_bm,[
                ('T1','reference')
            ]),
            (self.dn.allineate_orig,self.dn.allineate_bm,[
                ('out_matrix','in_matrix')
            ]),
            (self.dn.refit_setup,self.dn.refit,[
                ('refit_input','atrcopy')
            ]),
            (self.dn.allineate_bm,self.dn.refit,[
                ('out_file','in_file')
            ]),

            # intensities are differently scaled in FS image, replace with native intensities for uniformity
            (self.dn.inputnode,self.dn.uniform,[
                ('T1','in_file_a')
            ]),
            (self.dn.refit,self.dn.uniform,[
                ('out_file','in_file_b')
            ]),

            # Use OR of AFNI, FSL, and FS skullstrips within a 3-shell expanded AFNI mask as final
            (self.dn.afni_skullstrip,self.dn.maskop1,[
                ('out_file','in_file_a')
            ]),
            (self.dn.maskop1,self.dn.maskop2[0],[
                ('out_file','in_file_a')
            ]),
            (self.dn.maskop2[0],self.dn.maskop2[1],[
                ('out_file','in_file_a')
            ]),
            (self.dn.maskop2[1],self.dn.maskop2[2],[
                ('out_file','in_file_a')
            ]),
            (self.dn.fsl_skullstrip,self.dn.maskop3,[
                ('out_file','in_file_a')
            ]),
            (self.dn.afni_skullstrip,self.dn.maskop3,[
                ('out_file','in_file_b')
            ]),
            (self.dn.uniform,self.dn.maskop3,[
                ('out_file','in_file_c')
            ]),
            (self.dn.maskop2[2],self.dn.maskop4,[
                ('out_file','in_file_a')
            ]),
            (self.dn.maskop3,self.dn.maskop4,[
                ('out_file','in_file_b')
            ]),
            (self.dn.inputnode,self.dn.maskop4,[
                ('T1','in_file_c')
            ]),

            # output to output node
            (self.dn.maskop4,self.dn.outputnode,[
                ('out_file','T1_skullstrip')
            ]),
        ])
