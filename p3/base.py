"""Define Nodes for nipype workflow

TODO

"""
import os
from nipype import Workflow
from nipype import Node
from nipype.interfaces.io import DataSink

class basenodedefs:
    """Base class for initializing nodes in workflow

        TODO

    """
    def __init__(self,settings):
        #TODO: Use settings directly rather than using intermediary variables
        # Define several directories to use
        self.BASE_DIR = settings['BASE_DIR']
        self.SUBJECTS_DIR = os.path.join(self.BASE_DIR,'output','freesurfer_output')
        self.TMP_DIR = os.path.join(self.BASE_DIR,'tmp')
        self.REF_IMGS = os.path.join(self.BASE_DIR,'refimgs')
        self.DATA_DIR = settings['DATA_DIR']
        self.OUTPUT_DIR = os.path.join(self.BASE_DIR,'output',settings['subject'])
        self.SUBJECT = settings['subject']

        # make directories if not exist
        os.makedirs(self.SUBJECTS_DIR,exist_ok=True)
        os.makedirs(os.path.join(self.SUBJECTS_DIR,'skullstrip'),exist_ok=True)
        os.makedirs(self.OUTPUT_DIR,exist_ok=True)
        os.makedirs(self.TMP_DIR,exist_ok=True)

        # set number of initial frames to ignore
        self.IGNOREFRAMES = settings['ignoreframes']

        # Define datasink node
        self.datasink = Node(
            DataSink(
                base_directory=os.path.join(settings['BASE_DIR'],'output',settings['subject'])
            ),
            name='datasink'
        )

class workflowgenerator:
    """ Base class defining a workflow

        TODO

    """
    def __new__(cls,name,settings):
        # define workflow name and path
        cls.workflow = Workflow(name=name,base_dir=os.path.join(settings['BASE_DIR'],'tmp'))
