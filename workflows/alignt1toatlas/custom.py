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
    out_file = os.path.join(os.getcwd(),'{}_at.nii.gz'.format(filename))
    transform_file = os.path.join(os.getcwd(),'{}_at.nii.Xaff12.1D'.format(filename))

    # return the out_file
    return (out_file,transform_file)

# Qwarp is weird in nipype, writing my own custom function instead
def nonlinear_register(in_file,base_file):
    import os
    import shutil

    # get cwd
    cwd = os.getcwd()

    # copy file to cwd
    input_file = os.path.basename(shutil.copy2(in_file,cwd))

    # split extension of input file
    name,ext = os.path.splitext(input_file)
    while(ext != ''):
        name,ext = os.path.splitext(name)
    out_file = os.path.join(cwd,'{}_Qwarp.nii.gz'.format(name))

    # spawn the 3dQwarp process
    os.system('3dQwarp -prefix {} -base {} -source {}'.format(
        out_file,
        base_file,
        input_file
    ))

    # return nonlinear transformed file
    return out_file
