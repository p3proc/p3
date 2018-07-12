"""Define Custom Functions and Interfaces
"""
from nipype.interfaces.utility import Function

def gett1name(T1):
    import os
    # strip filename extension
    name,ext = os.path.splitext(os.path.basename(T1))
    while(ext != ''):
        name,ext = os.path.splitext(os.path.basename(name))
    return name
