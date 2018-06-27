from nipype import Workflow
from .nodedefs import definednodes

class alignt1toatlasworkflow(workflowgenerator):
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
            # Register the (1st) final skullstripped mprage to atlas
            (p3.skullstripped_mprage,p3.select0T1,[
                ('noskull','T1_list')
            ]),
            (p3.select0T1,p3.register,[
                ('T1_0','in_file')
            ]),
            (p3.register,p3.skullstripped_atlas_mprage,[
                ('out_file','noskull_at'),
                ('transform_file','transform')
            ]),
        ])
