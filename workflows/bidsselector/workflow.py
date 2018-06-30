from nipype import Workflow
from .nodedefs import definednodes
from ..base import workflowgenerator

class bidsselectorworkflow(workflowgenerator):
    """ Defines the bids selector workflow

        TODO

    """

    def __init__(self,name,settings):
        # call base constructor
        super().__init__(name,settings)

        # crete node definitions from settings
        self.dn = definednodes(settings)

        # avg over all T1s if enabled
        if settings['avgT1s']:
            # connect the workflow
            self.workflow.connect([ # connect nodes
                # select T1 to reference to
                (self.dn.bidsselection,self.dn.selectT1,[
                    ('T1','T1')
                ]),

                # align T1s to each other
                (self.dn.selectT1,self.dn.alignT1toT1,[
                    ('T1_reference','reference'),
                    ('T1_align','in_file')
                ]),
                (self.dn.selectT1,self.dn.mergeT1list,[
                    ('T1_reference','in1'),
                ]),
                (self.dn.alignT1toT1,self.dn.mergeT1list,[
                    ('out_file','in2'),
                ]),
                (self.dn.mergeT1list,self.dn.avgT1,[
                    ('out','T1_list'),
                ]),

                # output to output node
                (self.dn.avgT1,self.dn.outputnode,[
                    ('avg_T1','T1')
                ]),
                (self.dn.bidsselection,self.dn.outputnode,[
                    ('epi','epi')
                ]),

                # output QC
                (self.dn.alignT1toT1,self.dn.QC,[
                    ('out_file','QC.alignT1toT1.@T1align')
                ]),
                (self.dn.avgT1,self.dn.QC,[
                    ('avg_T1','QC.alignT1toT1.@T1avg')
                ])
            ])
        else: # use only the selected reference frame
            # connect the workflow
            self.workflow.connect([ # connect nodes
                # select T1 to reference to
                (self.dn.bidsselection,self.dn.selectT1,[
                    ('T1','T1')
                ]),

                # output to output node
                (self.dn.selectT1,self.dn.outputnode,[
                    ('T1_reference','T1')
                ]),
                (self.dn.bidsselection,self.dn.outputnode,[
                    ('epi','epi')
                ]),
            ])
