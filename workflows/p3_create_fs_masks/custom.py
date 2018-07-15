"""
    Define Custom Functions and Interfaces
"""

def resample_2_epi(atlas,T1,aparc_aseg,epi):
    """
        Resample images to epi resolution
    """

    import os

    # get cwd
    cwd = os.getcwd()

    # get filename of atlas
    name,ext = os.path.splitext(os.path.basename(atlas))
    while(ext != ''):
        name,ext = os.path.splitext(os.path.basename(name))
    out_file = os.path.join(cwd,'{}_epi.nii.gz'.format(name))

    # if atlas is not already .nii.gz; convert to .nii.gz
    if ext != 'gz':
        os.system('mri_convert -prefix {} {}'.format(
            atlas,
            os.path.join(cwd,'{}.nii.gz'.format(name))
        ))
        # set atlas to converted file
        atlas = os.path.join(cwd,'{}.nii.gz'.format(name))

    # resample the atlas
    os.system('3dresample -rmode Li -master {} -prefix {} -inset {}'.format(
        epi,
        out_file,
        atlas
    ))
    atlas_epi = out_file

    # get filename of T1
    name,ext = os.path.splitext(os.path.basename(T1))
    while(ext != ''):
        name,ext = os.path.splitext(os.path.basename(name))
    out_file = os.path.join(cwd,'{}_epi.nii.gz'.format(name))

    # resample the T1
    os.system('3dresample -rmode Li -master {} -prefix {} -inset {}'.format(
        epi,
        out_file,
        T1
    ))
    T1_epi = out_file

    # get filename of aparc_aseg
    name,ext = os.path.splitext(os.path.basename(aparc_aseg))
    while(ext != ''):
        name,ext = os.path.splitext(os.path.basename(name))
    out_file = os.path.join(cwd,'{}_epi.nii.gz'.format(name))

    # resample the aparc_aseg
    os.system('3dresample -rmode NN -master {} -prefix {} -inset {}'.format(
        epi,
        out_file,
        aparc_aseg
    ))
    aparc_aseg_epi = out_file

    # return resampled images
    return (atlas_epi,T1_epi,aparc_aseg_epi)