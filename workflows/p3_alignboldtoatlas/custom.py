"""
    Define Custom Functions and Interfaces
"""

# concatenate transform
def concattransform(in_file,tfm1,tfm2):
    import os
    import shutil

    # save to node folder (go up 2 directories bc of iterfield)
    cwd = os.path.dirname(os.path.dirname(os.getcwd()))

    # copy files to cwd
    input_file = os.path.abspath(shutil.copy2(in_file,cwd))
    tfm_file1 = os.path.abspath(shutil.copy2(tfm1,cwd))
    tfm_file2 = os.path.abspath(shutil.copy2(tfm2,cwd))

    # strip filename
    filename,ext = os.path.splitext(os.path.basename(tfm_file1))
    while(ext != ''):
        filename,ext = os.path.splitext(filename)

    # format string
    format_string = '-ONELINE {}::WARP_DATA -I {} {} -I'.format(
        in_file,
        tfm_file1,
        tfm_file2
    )

    # run cat_matvec for transform to ATL space
    os.system('cat_matvec {} > {}'.format(
        format_string,
        os.path.join(cwd,'{}_XFM_EPI2MPR2ATL.aff12.1D'.format(filename))
    ))
    master_transform = os.path.join(cwd,'{}_XFM_EPI2MPR2ATL.aff12.1D'.format(filename))

    # return master transform
    return master_transform

# apply nonlinear transform
def NwarpApply(in_file,warped_file):
    import os
    import shutil

    # save to node folder (go up 2 directories bc of iterfield)
    cwd = os.path.dirname(os.path.dirname(os.getcwd()))

    # copy files to cwd
    input_file = os.path.abspath(shutil.copy2(in_file,cwd))
    warped_file = os.path.abspath(shutil.copy2(warped_file,cwd))

    # strip filename
    filename,ext = os.path.splitext(os.path.basename(in_file))
    while(ext != ''):
        filename,ext = os.path.splitext(filename)
    out_file = os.path.join(cwd,'{}_Qwarp.nii.gz'.format(filename))

    # check if file already exist and remove it if it does
    if os.path.exists(out_file):
        os.remove(out_file)

    # run 3dNwarpApply
    os.system('3dNwarpApply -nwarp {} -source {} -prefix {}'.format(
        warped_file,
        in_file,
        out_file
    ))

    # output warped file
    return out_file
