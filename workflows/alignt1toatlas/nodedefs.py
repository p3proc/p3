"""Define Nodes for time shift and despike workflow

TODO

"""
from ..nodedefs import basenodedefs

class definednodes(basenodedefs):
    """Class initializing all nodes in workflow

        TODO

    """

    # call base constructor
    super().__init__(settings)

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
    self.skullstripped_atlas_mprage = Node(
        IdentityInterface(
            fields=['noskull_at','transform']
        ),
        name='skullstripped_atlas_mprage'
    )
