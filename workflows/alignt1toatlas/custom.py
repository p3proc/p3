"""
    Define Custom Functions and Interfaces
"""

# define custom register to atlas function (the afni interface in nipype sucks...)
def register_atlas(in_file,atlas):
    import os
    import shutil

    # copy file to cwd
    input_file = os.path.basename(shutil.copy2(in_file,os.getcwd()))

    # spawn the auto_tlrc process with os.system
    os.system(
        '@auto_tlrc -no_ss -base {} -input {} -pad_input 60'.format(
            atlas,
            input_file
        )
    )

    # split extension of input file
    name,ext = os.path.splitext(input_file)
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

    # copy file to cwd
    input_file = os.path.basename(shutil.copy2(in_file,cwd))

    # split extension of input file
    name,ext = os.path.splitext(input_file)
    while(ext != ''):
        name,ext = os.path.splitext(name)
    out_file = os.path.join(cwd,'{}_Qwarp.nii.gz'.format(name))
    warp_file = os.path.join(cwd,'{}_Qwarp_WARP.nii.gz'.format(name))

    # check if the base_file does not exist in the directory given
    if not os.path.exists(base_file):
        # assume the base_file is in the afni directory
        afni_loc = subprocess.run(['which','afni'],stdout=subprocess.PIPE).stdout.decode('utf-8').rstrip()
        afni_dir = os.path.dirname(afni_loc)
        base_file = os.path.join(afni_dir,base_file)

    # spawn the 3dQwarp process TODO: use subprocess run so we can raise error if fail
    os.system('3dQwarp -prefix {} -base {} -source {}'.format(
        out_file,
        base_file,
        input_file
    ))

    # return nonlinear transformed file
    return (out_file,warp_file)
