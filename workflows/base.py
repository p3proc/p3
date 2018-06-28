"""Define Nodes for nipype workflow

TODO

"""
import os
from nipype import Workflow

class basenodedefs:
    """Base class for initializing nodes in workflow

        TODO

    """
    def __init__(self,settings):
        # Define several directories to use
        self.BASE_DIR = settings['BASE_DIR']
        self.SUBJECTS_DIR = os.path.join(self.BASE_DIR,'output','freesurfer_output')
        self.TMP_DIR = os.path.join(self.BASE_DIR,'tmp')
        self.REF_IMGS = os.path.join(self.BASE_DIR,'refimgs')
        self.DATA_DIR = 'MSC_BIDS'
        self.SUBJECT = 'MSC01'

        # make directories if not exist
        os.makedirs(self.SUBJECTS_DIR,exist_ok=True)
        os.makedirs(self.TMP_DIR,exist_ok=True)

        # set number of initial frames to ignore
        self.IGNOREFRAMES = settings['ignoreframes']

class workflowgenerator:
    """ Base class defining a workflow

        TODO

    """
    def __init__(self,name,settings):
        # define workflow name and path
        self.workflow = Workflow(name=name,base_dir=os.path.join(settings['BASE_DIR'],'tmp'))
