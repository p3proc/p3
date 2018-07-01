"""Define Nodes for freesurfer workflow

TODO

"""
import os
from p3.base import basenodedefs
from .custom import *
from nipype import Node,MapNode
from nipype.interfaces import freesurfer
from nipype.interfaces.utility import IdentityInterface

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
                fields=['T1']
            ),
            name='input'
        )

        # get names of t1
        self.t1names = MapNode(
            Function(
                input_names=['T1'],
                output_names=['T1name'],
                function=gett1name
            ),
            iterfield=['T1'],
            name='t1names'
        )

        # Recon-all
        self.recon1 = MapNode( # for T1 mask
            freesurfer.ReconAll(
                directive='autorecon1',
                subjects_dir=os.path.join(self.SUBJECTS_DIR,'skullstrip'),
                parallel=True,
                openmp=4
            ),
            iterfield=['T1_files','subject_id'],
            name='recon1'
        )
        self.reconall = Node(
            freesurfer.ReconAll(
                directive='all',
                subjects_dir=self.SUBJECTS_DIR,
                parallel=True,
                openmp=4
            ),
            name='reconall'
        )
        self.reconall.inputs.subject_id = self.SUBJECT
        # MRIConvert
        self.orig_convert = MapNode(
            freesurfer.MRIConvert(
                in_type='mgz',
                out_type='niigz'
            ),
            iterfield=['in_file'],
            name='orig_mriconvert'
        )
        self.brainmask_convert = MapNode(
            freesurfer.MRIConvert(
                in_type='mgz',
                out_type='niigz'
            ),
            iterfield=['in_file'],
            name='brainmask_mriconvert'
        )

        # define output node
        self.outputnode = Node(
            IdentityInterface(
                fields=['orig','brainmask']
            ),
            name='output'
        )
