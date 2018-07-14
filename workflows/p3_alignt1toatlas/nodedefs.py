"""Define Nodes for time shift and despike workflow

TODO

"""
from ppp.base import basenodedefs
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
        self.set_output(['noskull_at','nonlin_warp','t1_2_atlas_transform','T1_0'])

        # define datasink substitutions
        self.set_subs([
            ('_calc_calc_calc_calc_calc_at','_atlas')
        ])

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
                input_names=['in_file','atlas'],
                output_names=['out_file','transform_file'],
                function=register_atlas
            ),
            name='atlasregister'
        )
        self.register.inputs.atlas = settings['atlas']

        self.Qwarp = Node(
            Function(
                input_names=['in_file','base_file'],
                output_names=['out_file','warp_file'],
                function=nonlinear_register
            ),
            name='Qwarp'
        )
        self.Qwarp.inputs.base_file = settings['atlas']
