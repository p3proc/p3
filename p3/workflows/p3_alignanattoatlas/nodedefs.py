"""Define Nodes for time shift and despike workflow

TODO

"""
from p3.base import basenodedefs
from p3.utility import set_atlas_path
from nipype import Node
from nipype.interfaces import ants
from nipype.interfaces.utility import Function
from .custom import *

class definednodes(basenodedefs):
    """Class initializing all nodes in workflow

        TODO

    """

    def __init__(self,settings):
        # call base constructor
        super().__init__(settings)

        # define input/output node
        self.set_input(['T1_skullstrip'])
        self.set_output(['affine_anat_2_atlas','warp_anat_2_atlas','anat_atlas'])

        # define datasink substitutions
        self.set_subs([
            ('_calc_calc_calc_calc_calc',''),
            ('_Warped','_atlas'),
        ])
        self.set_resubs([
            ('sub-(?P<subject>\w+_)','anat/sub-\g<subject>') # place file under anat folder
        ])

        # create the output name for the registration
        self.create_prefix = Node(
            Function(
                input_names=['filename'],
                output_names=['basename'],
                function=get_prefix
            ),
            name='create_prefix'
        )

        # Register to Atlas
        self.register = Node(
            ants.RegistrationSynQuick(
                num_threads=settings['num_threads']
            ),
            name='atlasregister'
        )
        self.register.inputs.fixed_image = set_atlas_path(settings['atlas']) # get atlas image
        self.register.n_procs = settings['num_threads']
