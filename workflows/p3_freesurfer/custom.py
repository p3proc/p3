"""Define Custom Functions and Interfaces
"""
from nipype.interfaces.utility import Function

def gett1name(T1):
    from ppp.base import get_basename
    return get_basename(T1)
