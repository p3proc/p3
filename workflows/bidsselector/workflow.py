from nipype import Workflow
from .nodedefs import definednodes
from p3.base import workflowgenerator

class bidsselectorworkflow(workflowgenerator):
    """ Defines the bids selector workflow

        TODO

    """

    def __new__(cls,name,settings):
        # call base constructor
        super().__new__(cls,name,settings)

        # crete node definitions from settings
        dn = definednodes(settings)

        # avg over all T1s if enabled
        if settings['avgT1s']:
            # connect the workflow
            cls.workflow.connect([ # connect nodes
                # select T1 to reference to
                (dn.bidsselection,dn.selectT1,[
                    ('T1','T1')
                ]),

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
                (dn.bidsselection,dn.outputnode,[
                    ('epi','epi')
                ]),

                # output QC
                (dn.alignT1toT1,dn.datasink,[
                    ('out_file','QC.alignT1toT1.@T1align')
                ]),
                (dn.avgT1,dn.datasink,[
                    ('avg_T1','QC.alignT1toT1.@T1avg')
                ])
            ])
        else: # use only the selected reference frame
            # connect the workflow
            cls.workflow.connect([ # connect nodes
                # select T1 to reference to
                (dn.bidsselection,dn.selectT1,[
                    ('T1','T1')
                ]),

                # output to output node
                (dn.selectT1,dn.outputnode,[
                    ('T1_reference','T1')
                ]),
                (dn.bidsselection,dn.outputnode,[
                    ('epi','epi')
                ]),
            ])

        # return workflow
        return cls.workflow
