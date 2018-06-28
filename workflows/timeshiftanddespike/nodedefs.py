"""Define Nodes for time shift and despike workflow

TODO

"""
import os
from ..base import basenodedefs
from .custom import *
from nipype import Node,MapNode
from nipype.interfaces import afni,fsl
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
                fields=['epi']
            ),
            name='input'
        )

        # extract slice timing so we can pass it to slice time correction
        self.extract_stc = MapNode(
            Function(
                input_names=['epi','bids_dir'],
                output_names=['slicetiming','TR'],
                function=extract_slicetime
            ),
            iterfield=['epi'],
            name='extract_slicetime'
        )
        self.extract_stc.inputs.bids_dir = os.path.join(self.BASE_DIR,self.DATA_DIR)

        # Despike epi data (create 2 for permutations with slice time correction)
        self.despike = MapNode(
            ExtendedDespike(
                args="-ignore {} -NEW -nomask".format(
                    self.IGNOREFRAMES
                ),
                outputtype="NIFTI_GZ"
            ),
            iterfield=['in_file'],
            name='despike'
        )

        # timeshift data (create 2 for permutations with despiking)
        self.tshift = MapNode(
            afni.TShift(
                args="-heptic",
                ignore=self.IGNOREFRAMES,
                tzero=0,
                outputtype="NIFTI_GZ"
            ),
            iterfield=['in_file','tpattern','tr'],
            name='tshift'
        )

        # Setup basefile for volreg
        self.firstrunonly = Node( # this will create a list of the first run to feed as a basefile
            Function(
                input_names=['epi'],
                output_names=['epi'],
                function=lambda epi: epi[0]
            ),
            name='retrievefirstrun'
        )

        self.extractroi = Node( # get reference frame of first run
            fsl.ExtractROI(
                t_min=self.IGNOREFRAMES,
                t_size=1,
                output_type='NIFTI_GZ'
            ),
            name='extractroi'
        )

        # Create Named Output for first frame alignment (first run only)
        self.firstframefirstrun = Node(
            IdentityInterface(
                fields=['refimg']
            ),
            name='firstframefirstrun'
        )

        # Motion correction (create 10 nodes for different permutations of inputs)
        self.volreg = MapNode(
            afni.Volreg(
                args="-heptic -maxite {}".format(
                    25
                ),
                verbose=True,
                zpad=10,
                outputtype="NIFTI_GZ"
            ),
            iterfield=['in_file'],
            name='volreg'
        )

        # define output node
        self.outputnode = Node(
            IdentityInterface(
                fields=['epi2epi1','refimg','tcat']
            ),
            name='output'
        )
