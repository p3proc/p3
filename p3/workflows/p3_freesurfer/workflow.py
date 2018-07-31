from nipype import Workflow
from .nodedefs import definednodes
from p3.base import workflowgenerator

class freesurferworkflow(workflowgenerator):
    """ Defines the freesurfer  workflow

        TODO

    """

    def __new__(cls,name,settings):
        # call base constructor
        super().__new__(cls,name,settings)

        # create node definitions from settings
        dn = definednodes(settings)

        # connect the workflow
        cls.workflow.connect([ # connect nodes
            ### Recon-all
            (dn.inputnode,dn.t1names,[
                ('T1','T1')
            ]),
            (dn.t1names,dn.recon1,[
                ('T1name','subject_id')
            ]),
            (dn.inputnode,dn.recon1,[
                ('T1','T1_files')
            ]),

            # Convert orig and brainmask
            (dn.recon1,dn.orig_convert,[
                ('orig','in_file')
            ]),
            (dn.recon1,dn.brainmask_convert,[
                ('brainmask','in_file')
            ]),

            # output to output node
            (dn.orig_convert,dn.outputnode,[
                ('out_file','orig')
            ]),
            (dn.brainmask_convert,dn.outputnode,[
                ('out_file','brainmask')
            ]),
        ])

        # run recon-all
        if settings['run_recon_all']:
            cls.workflow.connect([ # connect recon-all node
                (dn.inputnode,dn.reconall,[
                    ('T1','T1_files'),
                    ('subject','subject_id')
                ]),
                (dn.reconall,dn.outputnode,[
                    ('aparc_aseg','aparc_aseg')
                ])
            ])

        # return workflow
        return cls.workflow
