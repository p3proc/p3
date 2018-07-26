"""Define Nodes for time shift and despike workflow

TODO

"""
from ppp.base import basenodedefs
from .custom import *
from nipype import Node,MapNode
from nipype.interfaces import afni
from nipype.interfaces.utility import Function

class definednodes(basenodedefs):
    """Class initializing all nodes in workflow

        TODO

    """

    def __init__(self,settings):
        # call base constructor
        super().__init__(settings)

        # define input/output node
        self.set_input(['noskull_at','nonlin_warp','t1_2_atlas_transform','epi_2_t1','fmc','epi2epi1','tcat'])
        self.set_output(['epi_at'])

        # define datasink substitutions
        self.set_resubs([])

        # apply nonlinear transform
        #self.applymastertransform = MapNode(
        #    Function(
        #        input_names=['in_file','reference','tfm0','tfm1','tfm2','tfm3','tfm4'],
        #        output_names=['out_file'],
        #        function=NwarpApply
        #    ),
        #    iterfield=['in_file','tfm4'],
        #    name='applymastertransform'
        #)
