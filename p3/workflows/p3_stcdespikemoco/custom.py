"""
    Define Custom Functions and Interfaces
"""
from nipype.interfaces import afni,base

# Define string function to extract slice time info and write to file
def extract_slicetime(epi,bids_dir):
    # import necessary libraries
    from bids.grabbids import BIDSLayout
    import os
    import csv

    # save to node folder (go up 2 directories bc of iterfield)
    cwd = os.path.dirname(os.path.dirname(os.getcwd()))

    # specify bids layout
    layout = BIDSLayout(bids_dir)

    # get slicetiming info
    slice_timing = layout.get_metadata(epi)['SliceTiming']

    # get TR
    TR = layout.get_metadata(epi)['RepetitionTime']

    # set filename
    filename = os.path.join(cwd,'{}.SLICETIME'.format(os.path.splitext(os.path.basename(epi))[0]))

    # write slice timing to file
    with open(filename,'w') as st_file:
        wr = csv.writer(st_file,delimiter=' ')
        wr.writerow(slice_timing)

    # return timing pattern and TR
    return ('@{}'.format(filename),str(TR))

# Extend afni despike
# define extended input spec
class ExtendedDespikeInputSpec(afni.preprocess.DespikeInputSpec):
    spike_file = base.File(name_template="%s_despike_SPIKES", desc='spike image file name',
                    argstr='-ssave %s', name_source="in_file")

# define extended output spec
class ExtendedDespikeOutputSpec(afni.base.AFNICommandOutputSpec):
    spike_file = base.File(desc='spike file', exists=True)

# define extended afni despike
class ExtendedDespike(afni.Despike):
    input_spec = ExtendedDespikeInputSpec
    output_spec = ExtendedDespikeOutputSpec

# define a custom function for the antsMotionCorr
def antsMotionCorr(fixed_image,moving_image,transform,writewarp):
    import os
    from p3.base import get_basename

    # save to node folder (go up 2 directories bc of iterfield)
    cwd = os.path.dirname(os.path.dirname(os.getcwd()))

    # strip filename extension
    name = get_basename(moving_image)
    output_basename = os.path.join(cwd,name) # set the output basename
    output_mocoparams = os.path.join(cwd,'{}MOCOparams.csv'.format(name))
    output_warp = os.path.join(cwd,'{}Warp.nii.gz'.format(name))
    output_warpedimg = os.path.join(cwd,'{}_Warped.nii.gz'.format(name))

    # check write warp boolean
    if writewarp:
        writewarp = 1
    else:
        writewarp = 0

    # setup commandline execution
    command = 'antsMotionCorr -d 3 -o [{},{}] -m MI[{},{},{},{},{},{}] -t {}[{}] -u 1 -e 1 ' \
        '-s {} -f {} -i {} -n 1 -w {} -v'.format(
            output_basename,
            output_warpedimg,
            fixed_image,
            moving_image,
            1, # metric weight
            32, # number of bins
            'Regular', # sampling Strategy
            0.2, # sampling percentage
            transform,
            0.1, # gradient step
            '1x0', # smoothing sigmas
            '2x1', # shrink factors
            '20x5', # iterations,
            writewarp # set flag for writing warps
        )
    print(command) # print command before running

    # run antsMotionCorr
    os.system(command)

    # remove the InverseWarp image to save space
    os.system('rm {}'.format(os.path.join(cwd,'*InverseWarp.nii.gz')))

    # return the outputs
    return(output_warp,output_mocoparams,output_warpedimg)

# calculate FD
def calcFD(moco_params,brain_radius,threshold):
    import os
    import math
    from p3.base import get_basename

    # save to node folder (go up 2 directories bc of iterfield)
    cwd = os.path.dirname(os.path.dirname(os.getcwd()))

    # set output filename
    out_file = os.path.join(cwd,'{}.FD'.format(get_basename(moco_params)))
    tmask_out_file = os.path.join(cwd,'{}.tmask'.format(get_basename(moco_params)))

    # open file
    with open(moco_params,'r') as moco_file:
        moco_nums = moco_file.readlines()

    # format the moco numbers from strings to float
    f_moco_nums = [tuple(map(float,list(filter(bool,moco_num.rstrip().split("  "))))) for moco_num in moco_nums]
    fr_moco_nums = [(
        f_moco_num[0]*brain_radius*math.pi/180,
        f_moco_num[1]*brain_radius*math.pi/180,
        f_moco_num[2]*brain_radius*math.pi/180,
        f_moco_num[3],
        f_moco_num[4],
        f_moco_num[5]
        ) for f_moco_num in f_moco_nums]

    # calculate FD
    FD = [0]
    for f1,f2 in zip(fr_moco_nums[0:-1],fr_moco_nums[1:]):
        FD.append(sum(map(abs,[v1 - v2 for v1,v2 in zip(f1,f2)])))

    # write FD to file
    with open(out_file,'w') as FD_file:
        for val in FD:
            FD_file.write(str(val))
            FD_file.write('\n')

    # write tmask to file
    with open(tmask_out_file,'w') as tmask_file:
        for val in FD:
            tmask_file.write(str(int(val<threshold)))
            tmask_file.write('\n')

    # return the FD file
    return out_file,tmask_out_file
