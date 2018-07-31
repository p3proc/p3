"""
    Define Custom Functions and Interfaces
"""

def get_prefix(filename):
    from p3.base import get_basename
    return '{}'.format(get_basename(filename)) 
