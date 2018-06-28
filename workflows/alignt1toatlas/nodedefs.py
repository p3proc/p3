"""Define Nodes for time shift and despike workflow

TODO

"""
from ..base import basenodedefs
from .custom import *
from nipype import Node
from nipype.interfaces.utility import IdentityInterface,Function

class definednodes(basenodedefs):
    """Class initializing all nodes in workflow

        TODO

    """

    def __init__(self,settings):
        # call base constructor
        super().__init__(settings)

        # define input node
        self.inputnode = Node(
            IdentityInterface(
                fields=['T1_skullstrip']
            ),
            name='input'
        )

        # Get only first T1 (TODO: align other T1 images to this first T1)
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

        # define output node
        self.outputnode = Node(
            IdentityInterface(
                fields=['noskull_at','t1_2_atlas_transform','T1_0']
            ),
            name='output'
        )
