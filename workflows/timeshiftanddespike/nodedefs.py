"""Define Nodes for time shift and despike workflow

TODO

"""
import os
from ppp.base import basenodedefs
from .custom import *
from nipype import Node,MapNode
from nipype.interfaces import afni,fsl
from nipype.interfaces.utility import Function

class definednodes(basenodedefs):
    """Class initializing all nodes in workflow

        TODO

    """

    def __init__(self,settings):
        # call base constructor
        super().__init__(settings)

        # define input/output node
        self.set_input(['epi'])
        self.set_output(['epi2epi1','refimg','tcat'])

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
        self.extract_stc.inputs.bids_dir = os.path.join(settings['bids_dir'])

        # Despike epi data (create 2 for permutations with slice time correction)
        self.despike = MapNode(
            ExtendedDespike(
                args="-ignore {} -NEW -nomask".format(
                    settings['epi_reference']
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
                ignore=settings['epi_reference'],
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
                t_min=settings['epi_reference'],
                t_size=1,
                output_type='NIFTI_GZ'
            ),
            name='extractroi'
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
