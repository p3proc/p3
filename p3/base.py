"""Define Nodes for nipype workflow

TODO

"""
import os
from nipype import Workflow
from nipype import Node
from nipype.interfaces.utility import IdentityInterface
from nipype.interfaces.io import DataSink

class basenodedefs:
    """Base class for initializing nodes in workflow

        TODO

    """
    def __init__(self,settings):
        # Define datasink node
        self.datasink = Node(
            DataSink(
                base_directory=os.path.join(settings['output_dir'])
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

class workflowgenerator:
    """ Base class defining a workflow

        TODO

    """
    def __new__(cls,name,settings):
        # define workflow name and path
        cls.workflow = Workflow(name=name,base_dir=settings['tmp_dir'])
