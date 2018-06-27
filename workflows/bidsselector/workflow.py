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

        # connect the workflow
        self.workflow.connect([ # connect nodes
            # output to output node
            (self.dn.bidsselection,self.dn.outputnode,[
                ('T1','T1')
            ]),
            (self.dn.bidsselection,self.dn.outputnode,[
                ('epi','epi')
            ]),
        ])
