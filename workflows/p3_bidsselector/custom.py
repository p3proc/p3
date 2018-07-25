"""
    Define Custom Functions and Interfaces
"""

def avgT1s(T1_list):
    import os

    # get current path
    path = os.getcwd()

    # join list into string
    filelist = ' '.join(T1_list)

    # get filename of first file
    name,ext = os.path.splitext(os.path.basename(T1_list[0]))
    while(ext != ''):
        name,ext = os.path.splitext(os.path.basename(name))
    outfile = '{}_avg.nii.gz'.format(name)

    os.system('3dMean -prefix {} {}'.format(
        outfile,
        filelist
    ))

    # return avg T1
    return os.path.join(path,outfile)
