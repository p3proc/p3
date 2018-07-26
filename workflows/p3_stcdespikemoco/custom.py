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

    # save to node folder (go up 2 directories bc of iterfield)
    cwd = os.path.dirname(os.path.dirname(os.getcwd()))

    # strip filename extension
    name,ext = os.path.splitext(os.path.basename(moving_image))
    while(ext != ''):
        name,ext = os.path.splitext(os.path.basename(name))
    output_basename = os.path.join(cwd,name) # set the output basename
    output_mocoparams = os.path.join(cwd,'{}MOCOparams.csv'.format(name))
    output_warp = os.path.join(cwd,'{}Warp.nii.gz'.format(name))
    output_warpedimg = os.path.join(cwd,'{}_Warped.nii.gz'.format(name))
    output_avgimg = os.path.join(cwd,'{}_avg.nii.gz'.format(name))

    # check write warp boolean
    if writewarp:
        writewarp = 1
    else:
        writewarp = 0

    # setup commandline execution
    command = 'antsMotionCorr -d 3 -o [{},{},{}] -m MI[{},{},{},{},{},{}] -t {}[{}] -u 1 -e 1 ' \
        '-s {} -f {} -i {} -w {} -v'.format(
            output_basename,
            output_warpedimg,
            output_avgimg,
            fixed_image,
            moving_image,
            1, # metric weight
            32, # number of bins
            'Regular', # sampling Strategy
            0.15, # sampling percentage
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
    return(output_warp,output_mocoparams,output_warpedimg,output_avgimg)
