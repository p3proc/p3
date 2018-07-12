from nipype import Workflow
from .nodedefs import definednodes
from ppp.base import workflowgenerator

class alignt1toatlasworkflow(workflowgenerator):
    """ Defines the align t1 to atlas workflow

        TODO

    """

    def __new__(cls,name,settings):
        # call base constructor
        super().__new__(cls,name,settings)

        # create node definitions from settings
        dn = definednodes(settings)

        # connect the workflow
        cls.workflow.connect([ # connect nodes
            # Register the (1st) final skullstripped mprage to atlas
            (dn.inputnode,dn.select0T1,[
                ('T1_skullstrip','T1_list')
            ]),
            (dn.select0T1,dn.register,[
                ('T1_0','in_file')
            ]),

            # output to output node
            (dn.select0T1,dn.outputnode,[
                ('T1_0','T1_0')
            ]),
            (dn.register,dn.outputnode,[
                ('out_file','noskull_at'),
                ('transform_file','t1_2_atlas_transform')
            ]),

            # output T1 atlas alignment to p3 output
            (dn.register,dn.datasink,[
                ('out_file','p3.@T1_at')
            ])
        ])

        # do nonlinear alignement
        if settings['nonlinear_atlas']:
            cls.workflow.connect([
                # do nonlinear transform
                (dn.register,dn.Qwarp,[
                    ('out_file','in_file')
                ]),

                # output to output node
                (dn.Qwarp,dn.outputnode,[
                    ('out_file','noskull_Qwarp'),
                    ('warp_file','nonlin_warp'),
                ]),

                # output T1 atlas nonlinear alignment to p3 output
                (dn.Qwarp,dn.datasink,[
                    ('out_file','p3.@T1_Qwarp')
                ])
            ])

        # return workflow
        return cls.workflow
