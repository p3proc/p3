"""Define Nodes for time shift and despike workflow

TODO

"""
import os
from p3.base import basenodedefs
from .custom import *
from nipype import Node,MapNode
from nipype.interfaces import afni,fsl
from nipype.interfaces.utility import Function,IdentityInterface

class definednodes(basenodedefs):
    """Class initializing all nodes in workflow

        TODO

    """

    def __init__(self,settings):
        # call base constructor
        super().__init__(settings)

        # set threads to 1 if multiproc set
        if settings['multiproc']:
            settings['num_threads'] = 1

        # define input/output node
        self.set_input(['func'])
        self.set_output(['refimg','func_stc_despike','warp_func_2_refimg','func_aligned'])

        # define datasink substitutions
        self.set_subs([
            ('MOCOparams','_moco')
        ])

         # define datasink regular expression substitutions
        self.set_resubs([
            (r'_moco_before\d{1,3}','')
        ])

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
        self.extract_stc.inputs.bids_dir = settings['bids_dir']

        # Despike epi data (create 2 for permutations with slice time correction)
        self.despike = MapNode(
            ExtendedDespike(
                args="-ignore {} -NEW -nomask".format(
                    settings['func_reference_frame']
                ),
                outputtype="NIFTI_GZ"
            ),
            iterfield=['in_file'],
            name='despike'
        )

        # skip despike node
        self.skip_despike = MapNode(
            IdentityInterface(
                fields=['epi']
            ),
            iterfield=['epi'],
            name='skip_despike'
        )

        # despike pool node
        self.despike_pool = MapNode(
            IdentityInterface(
                fields=['epi']
            ),
            iterfield=['epi'],
            name='despike_pool'
        )

        # timeshift data
        self.tshift = MapNode(
            afni.TShift(
                args="-heptic",
                ignore=settings['func_reference_frame'],
                tzero=0,
                outputtype="NIFTI_GZ"
            ),
            iterfield=['in_file','tpattern','tr'],
            name='tshift'
        )

        # skip stc node
        self.skip_stc = MapNode(
            IdentityInterface(
                fields=['epi']
            ),
            iterfield=['epi'],
            name='skip_stc'
        )

        # despike/stc pool node
        self.stc_despike_pool = MapNode(
            IdentityInterface(
                fields=['epi']
            ),
            iterfield=['epi'],
            name='stc_despike_pool'
        )

        # Setup basefile for volreg (pre slice time correction/despike)
        self.refrunonly = Node( # this will grab only the first run to feed as a basefile
            Function(
                input_names=['epi','run'],
                output_names=['epi'],
                function=lambda epi,run: epi[run]
            ),
            name='refrunonly'
        )
        self.refrunonly.inputs.run = settings['func_reference_run']
        self.extractroi = Node( # get reference frame of first run
            fsl.ExtractROI(
                t_min=settings['func_reference_frame'],
                t_size=1,
                output_type='NIFTI_GZ'
            ),
            name='extractroi'
        )

        # Setup basefile for volreg (post slice time correction/despike)
        self.refrunonly_post = Node( # this will grab only the first run to feed as a basefile
            Function(
                input_names=['epi','run'],
                output_names=['epi'],
                function=lambda epi,run: epi[run]
            ),
            name='refrunonly_post'
        )
        self.refrunonly_post.inputs.run = settings['func_reference_run']
        self.extractroi_post = Node( # get reference frame of first run
            fsl.ExtractROI(
                t_min=settings['func_reference_frame'],
                t_size=1,
                output_type='NIFTI_GZ'
            ),
            name='extractroi_post'
        )

        # Moco (after)
        self.moco = MapNode(
            Function(
                input_names=['fixed_image','moving_image','transform','writewarp','threads'],
                output_names=['warp','mocoparams','warped_img'],
                function=antsMotionCorr
            ),
            iterfield=['moving_image'],
            name='moco'
        )
        self.moco.inputs.transform = 'Rigid'
        self.moco.inputs.writewarp = True
        self.moco.inputs.threads = settings['num_threads']

        # Moco (before)
        self.moco_before = MapNode(
            afni.Volreg(
                args="-heptic -maxite {}".format(
                    25
                ),
                verbose=True,
                zpad=10,
                outputtype="NIFTI_GZ"
            ),
            iterfield=['in_file'],
            name='moco_before'
        )

        # Calc FD
        self.calcFD = MapNode(
            Function(
                input_names=['moco_params','brain_radius','threshold'],
                output_names=['FD','tmask'],
                function=calcFD
            ),
            iterfield=['moco_params'],
            name='calcFD'
        )
        self.calcFD.inputs.brain_radius = settings['brain_radius']
        self.calcFD.inputs.threshold = settings['FD_threshold']
