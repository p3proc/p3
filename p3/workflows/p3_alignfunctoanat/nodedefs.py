"""Define Nodes for time shift and despike workflow

TODO

"""
from p3.base import basenodedefs
from nipype import Node
from nipype.interfaces import afni,fsl,ants
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
        self.set_input(['refimg','T1_skullstrip'])
        self.set_output(['affine_func_2_anat','warp_func_2_anat'])

        # define datasink substitutions
        self.set_subs([
            ('_calc_calc_calc_calc_calc',''),
            ('_roi','_reference'),
            ('_unwarped_Warped','_unwarped'),
            ('_masked_calc','_skullstrip'),
            ('_Warped','_anat'),
        ])

        # Skullstrip the EPI image
        self.epi_skullstrip = Node(
            fsl.BET(),
            name='epi_skullstrip'
        )
        self.epi_automask = Node(
            afni.Automask(
                args='-overwrite',
                outputtype='NIFTI_GZ'
            ),
            name='epi_automask'
        )
        self.epi_3dcalc = Node(
            afni.Calc(
                expr='c*or(a,b)',
                overwrite=True,
                outputtype='NIFTI_GZ'
            ),
            name='epi_3dcalc'
        )

        # create the output name for the registration
        self.create_prefix = Node(
            Function(
                input_names=['filename'],
                output_names=['basename'],
                function=get_prefix
            ),
            name='create_prefix'
        )

        # align func to anat
        self.align_func_2_anat = Node(
            ants.Registration(
                num_threads=settings['num_threads'],
                collapse_output_transforms=False,
                initial_moving_transform_com=1,
                write_composite_transform=True,
                initialize_transforms_per_stage=True,
                transforms=['Rigid','Affine'],
                transform_parameters=[(0.1,),(0.1,)],
                metric=['MI','MI'],
                metric_weight=[1,1],
                radius_or_number_of_bins=[32,32],
                sampling_strategy=['Regular','Regular'],
                sampling_percentage=[0.25,0.25],
                convergence_threshold=[1.e-6,1.e-8],
                convergence_window_size=[10,10],
                smoothing_sigmas=[[3,2,1,0],[2,1,0]],
                sigma_units=['vox','vox'],
                shrink_factors=[[8,4,2,1],[4,2,1]],
                number_of_iterations=[[1000,500,250,100],[500,250,100]],
                use_estimate_learning_rate_once=[False,True],
                use_histogram_matching=False,
                verbose=True,
                output_warped_image=True
            ),
            name='align_func_2_anat'
        )
        self.align_func_2_anat.n_procs = settings['num_threads']
