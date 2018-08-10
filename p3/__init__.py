# get version
import os
__version__ = open(os.path.join(os.path.dirname(os.path.realpath(__file__)),'version')).read().rstrip()
