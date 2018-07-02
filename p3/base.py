"""Define Nodes for nipype workflow

TODO

"""
import os
import inspect
from nipype import Workflow
from nipype import Node
from nipype.interfaces.utility import IdentityInterface
from nipype.interfaces.io import DataSink

def generate_subworkflows(imported_workflows,settings):
    """
        TODO: document this function
    """

    # create sub-workflows
    subworkflows = {}
    # loop over all imported workflows

    for name,wf in imported_workflows.items():
        # find the class whos base is the workflowgenerator
        for obj in dir(wf):
            if inspect.isclass(getattr(wf,obj)): # check if object is class
                # the object is a workflowgenerator object
                if getattr(wf,obj).__bases__[0] == workflowgenerator:
                    # create and assign the workflow to the dictionary
                    subworkflows[name] = getattr(wf,obj)(name,settings)

    # return subworkflows
    return subworkflows

class basenodedefs:
    """Base class for initializing nodes in workflow

        TODO

    """
    def __init__(self,settings):
        # Define datasink node
        self.datasink = Node(
            DataSink(
                base_directory=os.path.join(settings['output_dir']),
                substitutions=[
                    ('_subject_','sub-')
                ]
            ),
            name='datasink'
        )

    def set_input(self,input_list):
        # assign input list to inputnode fields
        self.inputnode = Node(
            IdentityInterface(
                fields=input_list
            ),
            name='input'
        )

    def set_output(self,output_list):
        # assign output list to outputnode fields
        self.outputnode = Node(
            IdentityInterface(
                fields=output_list
            ),
            name='output'
        )

    def set_subs(self,sub_list):
        # append substitution list to substitutions
        self.datasink.inputs.substitutions.extend(sub_list)

class workflowgenerator:
    """ Base class defining a workflow

        TODO

    """
    def __new__(cls,name,settings):
        # define workflow name and path
        cls.workflow = Workflow(name=name,base_dir=settings['tmp_dir'])
