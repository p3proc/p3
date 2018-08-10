"""
    Define Custom Functions and Interfaces
"""

def join_warps(reference,affine_fs_2_anat,affine_anat_2_atlas,warp_anat_2_atlas):
    """
        join warps to align freesurfer output to atlas
    """
    import os

    # get the current working directory
    cwd = os.getcwd()

    # just set the output name for the freesurfer concatenated transform
    fs_concat_transform = os.path.join(cwd,'fs_concat_transform.nii.gz')

    # setup command for execution
    command = 'antsApplyTransforms -f 0.0 -d 3 -o [{},1] -t {} -t {} -t {} -r {} -v'.format(
        fs_concat_transform,
        warp_anat_2_atlas,
        affine_anat_2_atlas,
        affine_fs_2_anat,
        reference
    )
    print(command)

    # run concat transforms
    os.system(command)

    # return the combined tranform
    return fs_concat_transform

def apply_warp(in_file,reference,transform):
    import os
    from p3.utility import get_basename

    # get cwd
    cwd = os.getcwd()

    # get filename to output
    out_file = os.path.join(cwd,'{}_atlas.nii.gz'.format(get_basename(in_file)))

    # set up command to run
    command = 'antsApplyTransforms -f 0.0 -d 3 -i {} -r {} -o {} -t {} -v'.format(
        in_file,
        reference,
        out_file,
        transform
    )
    print(command)

    # run transform
    os.system(command)

    # return output
    return out_file

def resample_2_epi(T1,epi,aparc_aseg=None):
    """
        Resample images to epi resolution
    """
    import os
    import shutil
    from p3.utility import get_basename

    # get cwd
    cwd = os.getcwd()

    # get first epi from list
    epi = epi[0]

    # get filename of T1
    out_file = os.path.join(cwd,'{}_funcres.nii.gz'.format(get_basename(T1)))

    # resample the T1
    os.system('3dresample -rmode Li -master {} -prefix {} -inset {}'.format(
        epi,
        out_file,
        T1
    ))
    T1_epi = out_file

    # ONLY if aparc_aseg defined
    if aparc_aseg:
        # get filename of aparc_aseg
        out_file = os.path.join(cwd,'{}_funcres.nii.gz'.format(get_basename(aparc_aseg)))

        # resample the aparc_aseg
        os.system('3dresample -rmode NN -master {} -prefix {} -inset {}'.format(
            epi,
            out_file,
            aparc_aseg
        ))
        aparc_aseg_epi = out_file
    else: # set to empty
        aparc_aseg_epi = ''

    # return resampled images
    return (T1_epi,aparc_aseg_epi)
