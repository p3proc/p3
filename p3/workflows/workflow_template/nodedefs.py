from p3.base import basenodedefs
from .custom import *

class definednodes(basenodedefs):
    """
        Initialize nodes here
    """

    def __init__(self,settings):
        # call base constructor
        super().__init__(settings)

        # define input/output nodes
        # self.setinput([
            # input fields go here
        # ])
        # self.setoutput([
            # output fields go here
        # ])

        # define datasink substitutions
        # self.set_subs([
            # simple substitutions go here
        # ])
        # self.set_resubs([
            # regex substitutions go here
        # ])

        # Any nodes should go under self.[node name]
        # Nodes are called in workflow through the prefix "dn.[node name]"
