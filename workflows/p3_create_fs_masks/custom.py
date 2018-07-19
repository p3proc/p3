"""
    Define Custom Functions and Interfaces
"""

def resample_2_epi(atlas,T1,epi,aparc_aseg=None):
    """
        Resample images to epi resolution
    """

    import os
    import shutil

    # get cwd
    cwd = os.getcwd()

    # get first epi from list
    epi = epi[0]

    # does the atlas have an extension?
    name,ext = os.path.splitext(os.path.basename(atlas))
    if ext == '': # I'm assuming it's from the atlas directory so we give it the BRIK/HEAD extension
        root = atlas
        atlas = '{}.BRIK.gz'.format(root)
        atlas2 = '{}.HEAD'.format(root)
        shutil.copy2(atlas2,cwd) # copy to local dir

    # copy atlas to local directory
    atlas = os.path.basename(shutil.copy2(atlas,cwd))

    # get filename of atlas to construct output name
    root_name,ext = os.path.splitext(os.path.basename(atlas))
    while(ext != ''):
        root_name,ext = os.path.splitext(os.path.basename(root_name))
    out_file = os.path.join(cwd,'{}_epi.nii.gz'.format(root_name)).replace('+','_')
    print(out_file)
    
    # if atlas is not already .nii.gz; convert to .nii.gz
    if atlas[-7:] != '.nii.gz':
        # uncompress gz
        if atlas[-3:] == '.gz':
            os.system('gzip -d {}'.format(atlas))
            # strip gz from name
            atlas,ext = os.path.splitext(os.path.basename(atlas))
        os.system('ls')
        # convert to .nii.gz
        os.system('mri_convert {} {}'.format(
            atlas,
            os.path.join(cwd,'{}.nii.gz'.format(root_name))
        ))
        # set atlas to converted file
        atlas = os.path.join(cwd,'{}.nii.gz'.format(root_name))

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

    # ONLY if aparc_aseg defined
    if aparc_aseg:
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
    else: # set to empty
        aparc_aseg_epi = ''
    
    # return resampled images
    return (atlas_epi,T1_epi,aparc_aseg_epi)
