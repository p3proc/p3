"""
    Define Custom Functions and Interfaces
"""

def avganats(anat_list):
    import os
    from ppp.base import get_basename

    # get current path
    path = os.getcwd()

    # join list into string
    filelist = ' '.join(anat_list)

    # get filename of first file
    outfile = '{}_avg.nii.gz'.format(get_basename(anat_list[0]))

    os.system('3dMean -prefix {} {}'.format(
        outfile,
        filelist
    ))

    # return avg anat
    return os.path.join(path,outfile)
