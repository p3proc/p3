from nipype import Workflow
from .nodedefs import definednodes
from ..base import workflowgenerator

class reconallworkflow(workflowgenerator):
    """ Defines the freesurfer reconall workflow

        TODO

    """

    def __init__(self,name,settings):
        # call base constructor
        super().__init__(name,settings)

        # crete node definitions from settings
        self.dn = definednodes(settings)

        # connect the workflow
        self.workflow.connect([ # connect nodes
            ### Recon-all
            (self.dn.inputnode,self.dn.t1names,[
                ('T1','T1')
            ]),
            (self.dn.t1names,self.dn.recon1,[
                ('T1name','subject_id')
            ]),
            (self.dn.inputnode,self.dn.recon1,[
                ('T1','T1_files')
            ]),

            # Convert orig and brainmask
            (self.dn.recon1,self.dn.orig_convert,[
                ('orig','in_file')
            ]),
            (self.dn.recon1,self.dn.brainmask_convert,[
                ('brainmask','in_file')
            ]),

            # output to output node
            (self.dn.orig_convert,self.dn.outputnode,[
                ('out_file','orig')
            ]),
            (self.dn.brainmask_convert,self.dn.outputnode,[
                ('out_file','brainmask')
            ]),
        ])

        # run recon-all
        if settings['run_recon_all']:
            self.workflow.connect([ # connect recon-all node
                (self.dn.inputnode,self.dn.reconall,[
                    ('T1','T1_files')
                ])
            ])
