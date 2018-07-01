"""Define Nodes for time shift and despike workflow

TODO

"""
import os
from p3.base import basenodedefs
from .custom import *
from nipype.interfaces import afni
from nipype.interfaces.io import BIDSDataGrabber
from nipype.interfaces.utility import IdentityInterface,Merge,Function
from nipype import Node,MapNode

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

        # select T1 to align to
        self.selectT1 = Node(
            Function(
                input_names=['T1','refnum'],
                output_names=['T1_reference','T1_align'],
                function=lambda T1,refnum: (T1[refnum],[img for idx,img in enumerate(T1) if idx!=refnum])
            ),
            name='selectT1'
        )
        self.selectT1.inputs.refnum = settings['T1_reference']

        # create node for aligning multiple T1 images to T1 reference
        self.alignT1toT1 = MapNode(
            afni.Allineate(
                outputtype='NIFTI_GZ',
            ),
            iterfield=['in_file'],
            name='alignT1toT1'
        )

        # merge T1s into single list
        self.mergeT1list = Node(
            Merge(
                numinputs=2,
                ravel_inputs=True
            ),
            name='mergeT1list'
        )

        # avg all T1s
        self.avgT1 = Node(
            Function(
                input_names=['T1_list'],
                output_names=['avg_T1'],
                function=avgT1s
            ),
            name='avgT1'
        )

        # define output node
        self.outputnode = Node(
            IdentityInterface(
                fields=['T1','epi']
            ),
            name='output'
        )
