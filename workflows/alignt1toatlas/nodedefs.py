"""Define Nodes for time shift and despike workflow

TODO

"""
from p3.base import basenodedefs
from .custom import *
from nipype import Node
from nipype.interfaces.utility import Function

class definednodes(basenodedefs):
    """Class initializing all nodes in workflow

        TODO

    """

    def __init__(self,settings):
        # call base constructor
        super().__init__(settings)

        # define input/output node
        self.set_input(['T1_skullstrip'])
        self.set_output(['noskull_at','t1_2_atlas_transform','T1_0'])

        # Convert from list to string input
        self.select0T1 = Node(
            Function(
                input_names=['T1_list'],
                output_names=['T1_0'],
                function=lambda T1_list: T1_list[0]
            ),
            name='select0T1'
        )

        # Register to Atlas
        self.register = Node(
            Function(
                input_names=['in_file'],
                output_names=['out_file','transform_file'],
                function=register_atlas
            ),
            name='atlasregister'
        )
