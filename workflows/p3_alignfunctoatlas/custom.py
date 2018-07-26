"""
    Define Custom Functions and Interfaces
"""

def format_reference(func,reference,bids_dir):
    import os
    import nibabel
    from bids.grabbids import BIDSLayout

    # save to node folder (go up 2 directories bc of iterfield)
    cwd = os.path.dirname(os.path.dirname(os.getcwd()))

    # get filename to output
    name,ext = os.path.splitext(os.path.basename(func))
    while(ext != ''):
        name,ext = os.path.splitext(os.path.basename(name))
    formatted_reference = os.path.join(cwd,'{}_format4D.nii.gz'.format(name))

    # get dim 4 and TR of input image
    dim4 = nibabel.load(func).header.get_data_shape()[3] # get the 4th dim
    TR = BIDSLayout(bids_dir).get_metadata(func)['RepetitionTime'] # get the TR

    # make the reference image the same dims as the input
    print('Formatting reference image...')
    command = 'ImageMath 3 {} ReplicateImage {} {} {} 0'.format(
        formatted_reference,
        reference,
        dim4,
        TR
    )
    print(command)
    os.system(command)

    return (formatted_reference,dim4,TR)

def combinetransforms(func,reference,dim4,TR,affine_func_2_anat,warp_func_2_anat,affine_anat_2_atlas,warp_anat_2_atlas,affine_fmc=None,warp_fmc=None):
    import os

    # save to node folder (go up 2 directories bc of iterfield)
    cwd = os.path.dirname(os.path.dirname(os.getcwd()))

    # get filename to output
    print(func)
    name,ext = os.path.splitext(os.path.basename(func))
    while(ext != ''):
        name,ext = os.path.splitext(os.path.basename(name))
    combined_transforms = os.path.join(cwd,'{}_combined_transforms.nii.gz'.format(name))
    combined_transforms4D = os.path.join(cwd,'{}_combined_transforms4D.nii.gz'.format(name))

    # set up transforms (check in field map correction files exist)
    # we exclude the func_2_refimg transform since it is already 4D
    if affine_fmc and warp_fmc:
        transforms = '-t {} -t {} -t {} -t {} -t {} -t {}'.format(
            warp_anat_2_atlas,
            affine_anat_2_atlas,
            warp_func_2_anat,
            affine_func_2_anat,
            warp_fmc,
            affine_fmc,
        )
    else:
        transforms = '-t {} -t {} -t {} -t {}'.format(
            warp_anat_2_atlas,
            affine_anat_2_atlas,
            warp_func_2_anat,
            affine_func_2_anat,
        )

    # convert the transforms to 4D
    print('Combining transforms into one warp displacement field...')
    command = 'antsApplyTransforms -d 3 -o [{},1] {} -r {} -v'.format(
        combined_transforms,
        transforms,
        reference
    )
    print(command)
    os.system(command)

    # replicate the combined transform
    print('Replicating the combined transform into 4D...')
    command = 'ImageMath 3 {} ReplicateDisplacement {} {} {} 0'.format(
        combined_transforms4D,
        combined_transforms,
        dim4,
        TR
    )
    print(command)
    os.system(command)

    # return the 4D combined transform
    return combined_transforms4D

def applytransforms(in_file,reference4D,combined_transforms4D,warp_func_2_refimg):
    import os

    # save to node folder (go up 2 directories bc of iterfield)
    cwd = os.path.dirname(os.path.dirname(os.getcwd()))

    # get filename to output
    name,ext = os.path.splitext(os.path.basename(in_file))
    while(ext != ''):
        name,ext = os.path.splitext(os.path.basename(name))
    out_file = os.path.join(cwd,'{}_moco_atlas.nii.gz'.format(name))

    # set up command to run
    command = 'antsApplyTransforms -d 4 -i {} -r {} -o {} -t {} -t {} -v'.format(
        in_file,
        reference4D,
        out_file,
        combined_transforms4D,
        warp_func_2_refimg
    )
    print(command)

    # apply transforms
    os.system(command)

    # return moco, atlas-aligned functional image
    return out_file
