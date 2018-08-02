from nipype import Workflow
from .nodedefs import definednodes
from p3.base import workflowgenerator

class newworkflow(workflowgenerator):
    """ newworkflow

        Description goes here

    """

    def __new__(cls,name,settings):
        # call base constructor
        super().__new__(cls,name,settings)

        # create node definitions from settings
        dn = definednodes(settings)

        # connect the workflow
        cls.workflow.connect([
            # node connections go here
        ])

        # return workflow
        return cls.workflow
