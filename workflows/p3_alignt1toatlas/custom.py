"""
    Define Custom Functions and Interfaces
"""

# define custom register to atlas function (the afni interface in nipype sucks...)
def register_atlas(in_file,atlas):
    import os
    import shutil

    # spawn the auto_tlrc process with os.system
    os.system(
        '@auto_tlrc -no_ss -base {} -input {} -pad_input 60'.format(
            atlas,
            in_file
        )
    )

    # split extension of input file
    name,ext = os.path.splitext(os.path.basename(in_file))
    while(ext != ''):
        name,ext = os.path.splitext(name)
    filename = '{}_at.nii'.format(name)

    #  gzip the nifti
    os.system('gzip {}'.format(filename))

    # get the out_file
    out_file = os.path.join(os.getcwd(),'{}.gz'.format(filename))
    transform_file = os.path.join(os.getcwd(),'{}.Xaff12.1D'.format(filename))

    # return the out_file
    return (out_file,transform_file)

# Qwarp is weird in nipype, writing my own custom function instead
def nonlinear_register(in_file,base_file):
    import os
    import shutil
    import subprocess

    # get cwd
    cwd = os.getcwd()

    # split extension of input file
    name,ext = os.path.splitext(os.path.basename(in_file))
    while(ext != ''):
        name,ext = os.path.splitext(name)
    out_file = os.path.join(cwd,'{}_Qwarp.nii.gz'.format(name))
    warp_file = os.path.join(cwd,'{}_Qwarp_WARP.nii.gz'.format(name))

    # check if files already exist and remove them if they do
    if os.path.exists(out_file):
        os.remove(out_file)
    if os.path.exists(warp_file):
        os.remove(warp_file)

    # spawn the 3dQwarp process TODO: use subprocess run so we can raise error if fail
    os.system('3dQwarp -prefix {} -base {} -source {}'.format(
        out_file,
        base_file,
        in_file
    ))

    # return nonlinear transformed file
    return (out_file,warp_file)
