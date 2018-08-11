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
    from p3.utility import get_basename

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
def calcFD(moco_params,brain_radius,threshold,filtered_threshold,TR,min_bpm,max_bpm):
    import os
    import math
    from p3.utility import get_basename
    import numpy as np
    from scipy import signal

    def respiration_iirnotch(TR_in_sec,bpm_min=18.582,bpm_max=25.7263):
        """ Function for calculating filter parameters for respiration filter

            Takes in the TR (optional min/max breaths-per-min, bpm_min, bpm_max).
            Returns the parameters for IIR Notch filter.
        """

        fs = 1.0/TR_in_sec  # Sampling frequency (Hz)
        fn = fs/2.0         # Nyquist frequency (Hz)

        # RR MIN
        rr_min = bpm_min/60.0                              # respiration rate minimum in Hz
        fa_min = abs(rr_min-math.floor((rr_min+fn)/fs)*fs) # Aliased minimum frequency (Hz)
        w0_min = fa_min/fn                                 # Normalized minimum frequency

        # RR MAX
        rr_max = bpm_max/60.0                              # respiration rate maximum in Hz
        fa_max = abs(rr_max-math.floor((rr_max+fn)/fs)*fs) # Aliased maximum frequency (Hz)
        w0_max = fa_max/fn                                 # Normalized maximum frequency

        # RR iirnotch filter
        w0 = np.mean([w0_min,w0_max])      # Mean normalized frequency
        bw = abs(w0_max-w0_min)            # Normalized bandwidth
        Q = w0/bw                          # Quality factor
        b,a = signal.iirnotch(w0,Q)        # Filter design

        return b,a

    # save to node folder (go up 2 directories bc of iterfield)
    cwd = os.path.dirname(os.path.dirname(os.getcwd()))

    # set output filename
    out_file = os.path.join(cwd,'{}.FD'.format(get_basename(moco_params)))
    tmask_out_file = os.path.join(cwd,'{}.tmask'.format(get_basename(moco_params)))
    filt_moco_file = os.path.join(cwd,'{}_filtered.1D'.format(get_basename(moco_params)))
    filt_out_file = os.path.join(cwd,'{}_filtered.FD'.format(get_basename(moco_params)))
    filt_tmask_out_file = os.path.join(cwd,'{}_filtered.tmask'.format(get_basename(moco_params)))

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

    # convert to numpy array and filter the motion numbers
    np_moco_nums = np.array(f_moco_nums)
    TR = float(TR) # convert TR to float
    b,a = respiration_iirnotch(TR,min_bpm,max_bpm) # create filter
    # filter data (run twice for 4th order)
    filt_moco_stage1 = signal.filtfilt(b,a,np_moco_nums,axis=0,padtype=None)
    filt_moco_stage2 = signal.filtfilt(b,a,filt_moco_stage1,axis=0,padtype=None)
    filt_moco = filt_moco_stage2
    # Convert rotations to mm
    filt_moco[:,4:7] = filt_moco[:,4:7]*brain_radius*math.pi/180
    # Calculate FD values for the series
    filtered_FD = np.array([np.concatenate(
            (np.array([0]),np.sum(np.absolute(filt_moco[1:,:]-filt_moco[0:-1,:]),axis=1)
        ),axis=0)]).transpose()
    # convert to lists
    filt_moco = np.ndarray.tolist(filt_moco)
    filtered_FD = [FD_val[0] for FD_val in np.ndarray.tolist(filtered_FD)]

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

    # write filtered motion numbers to file
    with open(filt_moco_file,'w') as fm_file:
        for val in filt_moco:
            fm_file.write(' '.join([str(v) for v in val]))
            fm_file.write('\n')

    # write filtered FD to file
    with open(filt_out_file,'w') as filt_FD_file:
        for val in filtered_FD:
            filt_FD_file.write(str(val))
            filt_FD_file.write('\n')

    # write filtered tmask to file
    with open(filt_tmask_out_file,'w') as filt_tmask_file:
        for val in filtered_FD:
            filt_tmask_file.write(str(int(val<filtered_threshold)))
            filt_tmask_file.write('\n')

    # return the FD file
    return out_file,tmask_out_file,filt_moco_file,filt_out_file,filt_tmask_out_file
