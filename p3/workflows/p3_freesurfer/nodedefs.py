"""Define Nodes for freesurfer workflow

TODO

"""
import os
from p3 import base
from p3.base import basenodedefs
from .custom import *
from nipype import Node,MapNode
from nipype.interfaces import freesurfer

class definednodes(basenodedefs):
    """Class initializing all nodes in workflow

        TODO

    """
    def __init__(self,settings):
        # call base constructor
        super().__init__(settings)

        # Set freesurfer license variable
        wfs_dir = os.path.dirname(base.__file__)
        os.environ['FS_LICENSE'] = os.path.join(wfs_dir,'license.txt')
        # This is to actually verify that the freesurfer license is at this location
        assert os.path.exists(os.path.join(wfs_dir,'license.txt')), "Could not find freesurfer license at {}".format(wfs_dir)

        # Define freesurfer directory
        self.freesurfer_dir = os.path.join(settings['output_dir'],'freesurfer')
        os.makedirs(self.freesurfer_dir,exist_ok=True)
        os.makedirs(os.path.join(self.freesurfer_dir,'skullstrip'),exist_ok=True)

        # define input/output node
        self.set_input(['T1','subject'])
        self.set_output(['orig','brainmask','aparc_aseg'])

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
                subjects_dir=os.path.join(self.freesurfer_dir,'skullstrip'),
                parallel=True,
                openmp=4
            ),
            iterfield=['T1_files','subject_id'],
            name='recon1'
        )
        self.reconall = Node(
            freesurfer.ReconAll(
                directive='all',
                subjects_dir=self.freesurfer_dir,
                parallel=True,
                openmp=4
            ),
            name='reconall'
        )

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
