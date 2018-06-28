"""
    Define Custom Functions and Interfaces
"""

# define custom register to atlas function (the afni interface in nipype sucks...)
def register_atlas(in_file):
    import os
    import shutil

    # copy file to cwd
    input_file = os.path.basename(shutil.copy2(in_file,os.getcwd()))

    # spawn the auto_tlrc process with os.system
    os.system(
        '@auto_tlrc -no_ss -base TT_N27+tlrc -input {0} -pad_input 60'.format(
            input_file,
        )
    )

    # split extension of input file
    name_nii,_ = os.path.splitext(input_file)
    filename,_ = os.path.splitext(name_nii)

    #  gzip the nifti
    os.system(
        'gzip {}'.format('{}_at.nii'.format(filename))
    )

    # get the out_file
    out_file = os.path.join(os.getcwd(),'{}_at.nii.gz'.format(filename))
    transform_file = os.path.join(os.getcwd(),'{}_at.nii.Xaff12.1D'.format(filename))

    # return the out_file
    return (out_file,transform_file)
