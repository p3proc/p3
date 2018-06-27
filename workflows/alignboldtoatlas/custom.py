"""
    Define Custom Functions and Interfaces
"""

# concatenate transform
def concattransform(in_file,tfm1,tfm2,tfm3):
    import os
    import shutil

    # save to node folder (go up 2 directories bc of iterfield)
    cwd = os.path.dirname(os.path.dirname(os.getcwd()))

    # copy files to cwd
    input_file = os.path.abspath(shutil.copy2(in_file,cwd))
    tfm_file1 = os.path.abspath(shutil.copy2(tfm1,cwd))
    tfm_file2 = os.path.abspath(shutil.copy2(tfm2,cwd))
    tfm_file3 = os.path.abspath(shutil.copy2(tfm3,cwd))

    # strip filename
    name_nii,_ = os.path.splitext(os.path.basename(tfm_file1))
    filename,_ = os.path.splitext(name_nii)

    # format string
    format_string = '-ONELINE {}::WARP_DATA -I {} {} -I {}'.format(
        in_file,
        tfm_file1,
        tfm_file2,
        tfm_file3
    )

    # run cat_matvec for transform to ATL space
    os.system('cat_matvec {} > {}'.format(
        format_string,
        os.path.join(cwd,'{}_XFM_EPI2EPI2MPR2ATL.aff12.1D'.format(filename))
    ))
    master_transform = os.path.join(cwd,'{}_XFM_EPI2EPI2MPR2ATL.aff12.1D'.format(filename))

    # return master transform
    return master_transform
