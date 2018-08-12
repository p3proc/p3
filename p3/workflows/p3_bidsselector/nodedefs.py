"""Define Nodes for time shift and despike workflow

TODO

"""
import os
from p3.base import basenodedefs
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

        # check files being processed
        check_query(settings['bids_query'],settings['bids_dir'])

        # define output node
        self.set_input(['subject'])
        self.set_output(['anat','func','subject'])

        # define datasink substitutions
        self.set_resubs([
            ('_alignanattoanat\d{1,3}',''),
            ('bidsselector/sub-(?P<subject>\w+)_','bidsselector/sub-\g<subject>/sub-\g<subject>_') # put raw files under subject
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

        # select anat to align to
        self.selectanat = Node(
            Function(
                input_names=['anat','refnum'],
                output_names=['anat_reference','anat_align'],
                function=lambda anat,refnum: (anat[refnum],[img for idx,img in enumerate(anat) if idx!=refnum])
            ),
            name='selectanat'
        )
        self.selectanat.inputs.refnum = settings['anat_reference']

        # create node for aligning multiple T1 images to T1 reference
        self.alignanattoanat = MapNode(
            afni.Allineate(
                outputtype='NIFTI_GZ',
            ),
            iterfield=['in_file'],
            name='alignanattoanat'
        )

        # merge anats into single list
        self.mergeanatlist = Node(
            Merge(
                numinputs=2,
                ravel_inputs=True
            ),
            name='mergeanatlist'
        )

        # avg all anats
        self.avganat = Node(
            Function(
                input_names=['anat_list'],
                output_names=['avg_anat'],
                function=avganats
            ),
            name='avganat'
        )
