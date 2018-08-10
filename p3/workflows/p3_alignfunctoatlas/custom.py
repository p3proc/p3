"""
    Define Custom Functions and Interfaces
"""

def get_resolution(reference):
    import subprocess

    # get resolution of voxel so we can resample it
    out = subprocess.run(['3dinfo','-adi',reference],stdout=subprocess.PIPE)
    resolution = float(out.stdout.decode('utf-8').rstrip())

    return resolution

def format_reference(func,reference,bids_dir):
    import os
    import nibabel
    from p3.utility import get_basename
    from bids.grabbids import BIDSLayout

    # save to node folder (go up 2 directories bc of iterfield)
    cwd = os.path.dirname(os.path.dirname(os.getcwd()))

    # get filename to output
    formatted_reference = os.path.join(cwd,'{}_format4D.nii.gz'.format(get_basename(func)))

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

def combinetransforms(func,reference,dim4,TR,affine_func_2_anat,affine_anat_2_atlas,warp_anat_2_atlas,warp_fmc=None):
    import os
    from p3.utility import get_basename

    # save to node folder (go up 2 directories bc of iterfield)
    cwd = os.path.dirname(os.path.dirname(os.getcwd()))

    # get filename to output
    name = get_basename(func)
    combined_transforms = os.path.join(cwd,'{}_combined_transforms.nii.gz'.format(name))
    combined_transforms4D = os.path.join(cwd,'{}_combined_transforms4D.nii.gz'.format(name))

    # set up transforms (check in field map correction files exist)
    # we exclude the func_2_refimg transform since it is already 4D
    if warp_fmc:
        transforms = '-t {} -t {} -t {} -t {}'.format(
            warp_anat_2_atlas,
            affine_anat_2_atlas,
            affine_func_2_anat,
            warp_fmc,
        )
    else:
        transforms = '-t {} -t {} -t {}'.format(
            warp_anat_2_atlas,
            affine_anat_2_atlas,
            affine_func_2_anat,
        )

    # convert the transforms to 4D
    print('Combining transforms into one warp displacement field...')
    command = 'antsApplyTransforms -f 0.0 -d 3 -o [{},1] {} -r {} -v'.format(
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

def create_dfnd_mask(refimg,affine_func_2_anat,affine_anat_2_atlas,warp_anat_2_atlas,reference):
    import os
    from p3.utility import get_basename

    # get the current node directory
    cwd = os.getcwd()

    # get filename to output
    out_file = os.path.join(cwd,'{}_atlas.nii.gz'.format(get_basename(refimg)))
    mask_file = os.path.join(cwd,'{}_atlas_dfnd.nii.gz'.format(get_basename(refimg)))

    # create dfnd mask
    command = 'antsApplyTransforms -f 0.0 -d 3 -o {} -i {} -t {} -t {} -t {} -r {} -v'.format(
        out_file,
        refimg,
        warp_anat_2_atlas,
        affine_anat_2_atlas,
        affine_func_2_anat,
        reference
    )
    print(command)
    os.system(command)

    # convert to binary
    os.system('fslmaths {} -bin {}'.format(
        out_file,
        mask_file
    ))

    return mask_file

def applytransforms(in_file,reference4D,combined_transforms4D,warp_func_2_refimg,dfnd_mask):
    import os
    from p3.utility import get_basename

    # save to node folder (go up 2 directories bc of iterfield)
    cwd = os.path.dirname(os.path.dirname(os.getcwd()))

    # get filename to output
    out_file = os.path.join(cwd,'{}_moco_atlas.nii.gz'.format(get_basename(in_file)))

    # set up command to run
    command = 'antsApplyTransforms -f 0.0 -d 4 -i {} -r {} -o {} -t {} -t {} -v'.format(
        in_file,
        reference4D,
        out_file,
        combined_transforms4D,
        warp_func_2_refimg
    )
    print(command)

    # apply transforms
    os.system(command)

    # mask the aligned func with the dfnd mask
    print('Applying dfnd mask...')
    os.system('fslmaths {0} -mul {1} {0}'.format(
        out_file,
        dfnd_mask
    ))

    # return moco, atlas-aligned functional image
    return out_file
