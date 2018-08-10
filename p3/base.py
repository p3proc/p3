"""Define Nodes for nipype workflow
TODO
"""
import os
from nipype import Node,Workflow
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

    def set_resubs(self,sub_list):
        # add regular expression substitution to list
        self.datasink.inputs.regexp_substitutions = sub_list

class workflowgenerator:
    """ Base class defining a workflow

        TODO

    """
    def __new__(cls,name,settings):
        # define workflow name and path
        cls.workflow = Workflow(name=name,base_dir=settings['tmp_dir'])
