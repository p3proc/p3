"""
    Define Custom Functions and Interfaces
"""

def avganats(anat_list):
    import os

    # get current path
    path = os.getcwd()

    # join list into string
    filelist = ' '.join(anat_list)

    # get filename of first file
    name,ext = os.path.splitext(os.path.basename(anat_list[0]))
    while(ext != ''):
        name,ext = os.path.splitext(os.path.basename(name))
    outfile = '{}_avg.nii.gz'.format(name)

    os.system('3dMean -prefix {} {}'.format(
        outfile,
        filelist
    ))

    # return avg anat
    return os.path.join(path,outfile)
