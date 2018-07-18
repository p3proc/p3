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

def get_atlas_image(base_file,subject):
    import os
    import subprocess

    # check if the base_file does not exist in the directory given
    if not os.path.exists(base_file):
        # assume the base_file is in the afni directory
        afni_loc = subprocess.run(['which','afni'],stdout=subprocess.PIPE).stdout.decode('utf-8').rstrip()
        afni_dir = os.path.dirname(afni_loc)
        base_file = os.path.join(afni_dir,base_file)

        # check if atlas is in afni dir
        if not os.path.exists('{}.HEAD'.format(base_file)):
            raise IOError("Could not find atlas image provided!")

    # return location of atlas image
    return base_file
