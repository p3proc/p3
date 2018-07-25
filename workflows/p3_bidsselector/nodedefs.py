"""Define Nodes for time shift and despike workflow

TODO

"""
import os
from ppp.base import basenodedefs
from .custom import *
from nipype.interfaces import afni
from nipype.interfaces.io import BIDSDataGrabber
from nipype.interfaces.utility import Merge,Function
from nipype import Node,MapNode

class definednodes(basenodedefs):
    """Class initializing all nodes in workflow

        TODO

    """

    def __init__(self,settings):
        # call base constructor
        super().__init__(settings)

        # define output node
        self.set_input(['subject'])
        self.set_output(['T1','epi','subject'])

        # define datasink substitutions
        self.set_resubs([
            ('_alignT1toT1\d{1,3}','')
        ])

        # parametrize subject for multiple subject processing
        self.inputnode.iterables = ('subject',settings['subject'])

        # Get BIDs dataset and organize data for input
        self.bidsselection = Node(
            BIDSDataGrabber(
                base_dir=settings['bids_dir'],
                output_query=settings['bids_query']
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
