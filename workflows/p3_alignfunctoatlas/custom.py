"""
    Define Custom Functions and Interfaces
"""

def applytransforms(in_file,reference,warp_func_2_refimg,affine_func_2_anat,warp_func_2_anat,affine_anat_2_atlas,warp_anat_2_atlas,affine_fmc=None,warp_fmc=None):
    import os

    # save to node folder (go up 2 directories bc of iterfield)
    cwd = os.path.dirname(os.path.dirname(os.getcwd()))

    # get filename to output
    name,ext = os.path.splitext(os.path.basename(in_file))
    while(ext != ''):
        name,ext = os.path.splitext(os.path.basename(name))
    out_file = os.path.join(cwd,'{}_moco_atlas.nii.gz'.format(name))

    # set up transforms (check in field map correction files exist)
    if affine_fmc and warp_fmc:
        transform = '-t {} -t {} -t {} -t {} -t {} -t {} -t {}'.format(
            warp_anat_2_atlas,
            affine_anat_2_atlas,
            warp_func_2_anat,
            affine_func_2_anat,
            warp_fmc,
            affine_fmc,
            warp_func_2_refimg
        )
    else:
        transform = '-t {} -t {} -t {} -t {} -t {}'.format(
            warp_anat_2_atlas,
            affine_anat_2_atlas,
            warp_func_2_anat,
            affine_func_2_anat,
            warp_func_2_refimg
        )

    # set up command to run
    command = 'antsApplyTransforms -d 4 -i {} -r {} -o {} {} -v'.format(
        in_file,
        reference,
        out_file,
        transform
    )
    print(command)

    # apply transforms
    os.system(command)

    # return moco, atlas-aligned functional image
    return out_file
