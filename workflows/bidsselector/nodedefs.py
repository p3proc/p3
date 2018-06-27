"""Define Nodes for time shift and despike workflow

TODO

"""
import os
from ..base import basenodedefs
from nipype.interfaces.io import BIDSDataGrabber
from nipype.interfaces.utility import IdentityInterface
from nipype import Node

class definednodes(basenodedefs):
    """Class initializing all nodes in workflow

        TODO

    """

    def __init__(self,settings):
        # call base constructor
        super().__init__(settings)

        # Get BIDs dataset and organize data for input
        self.bidsselection = Node(
            BIDSDataGrabber(
                base_dir=os.path.join(self.BASE_DIR,self.DATA_DIR),
                subject=self.SUBJECT,
                output_query={
                    'T1':{
                        'type':'T1w'
                        },
                    'epi':{
                        'modality':'func',
                        'task':'rest'
                        }
                    }
            ),
            name='bidsselection'
        )

        # define output node
        self.outputnode = Node(
            IdentityInterface(
                fields=['T1','epi']
            ),
            name='output'
        )
