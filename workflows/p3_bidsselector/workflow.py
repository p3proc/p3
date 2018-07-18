from nipype import Workflow
from .nodedefs import definednodes
from ppp.base import workflowgenerator

class bidsselectorworkflow(workflowgenerator):
    """ Defines the bids selector workflow

        TODO

    """

    def __new__(cls,name,settings):
        # call base constructor
        super().__new__(cls,name,settings)

        # create node definitions from settings
        dn = definednodes(settings)

        # avg over all T1s if enabled
        if settings['avgT1s']:
            # connect the workflow
            cls.workflow.connect([ # connect nodes
                # align T1s to each other
                (dn.selectT1,dn.alignT1toT1,[
                    ('T1_reference','reference'),
                    ('T1_align','in_file')
                ]),
                (dn.selectT1,dn.mergeT1list,[
                    ('T1_reference','in1'),
                ]),
                (dn.alignT1toT1,dn.mergeT1list,[
                    ('out_file','in2'),
                ]),
                (dn.mergeT1list,dn.avgT1,[
                    ('out','T1_list'),
                ]),

                # output to output node
                (dn.avgT1,dn.outputnode,[
                    ('avg_T1','T1')
                ]),

                # output QC
                (dn.alignT1toT1,dn.datasink,[
                    ('out_file','p3_QC.@alignT1toT1')
                ]),
                (dn.avgT1,dn.datasink,[
                    ('avg_T1','p3_QC.@avgT1')
                ])
            ])
        else: # use only the selected reference frame
            # connect the workflow
            cls.workflow.connect([ # connect nodes
                # output to output node
                (dn.selectT1,dn.outputnode,[
                    ('T1_reference','T1')
                ])
            ])

        # connect nodes common to both options
        cls.workflow.connect([
            # specify subject to process
            (dn.inputnode,dn.bidsselection,[
                ('subject','subject')
            ]),
            (dn.inputnode,dn.get_atlas,[
                ('subject','subject')
            ]),

            # select T1 to reference to
            (dn.bidsselection,dn.selectT1,[
                ('T1','T1')
            ]),

            # set outputs
            (dn.bidsselection,dn.outputnode,[
                ('epi','epi')
            ]),
            (dn.inputnode,dn.outputnode,[
                ('subject','subject')
            ]),
            (dn.get_atlas,dn.outputnode,[
                ('base_file','atlas')
            ])
        ])

        # return workflow
        return cls.workflow
