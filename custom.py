"""
    Define Custom Functions and Interfaces
"""
from nipype.interfaces import afni,base,fsl

# Define qualitycheck function
def qualitycheck(epi,epi_sidecar,threshold=100):
    # import necessary libraries
    import subprocess
    import json
    from os.path import basename,isfile,splitext
    # define custom indented print function
    cprint = lambda s: print("%s%s"%("\t\t",s))

    cprint("\n")
    #TODO Is this really necessary? BIDS-validator does most of this already...
    cprint("RUNNING QUALITY CONTROL...             ")
    cprint("                                       ")
    cprint("                                       ")
    cprint("                            @@@@@      ")
    cprint("                          @@@@@@@@     ")
    cprint("                         @@@@@@@@      ")
    cprint("                        @@@@@@@@       ")
    cprint("                      @@@@@@@@         ")
    cprint("                     @@@@@@@@          ")
    cprint("       @@           @@@@@@@@           ")
    cprint("     @@@@@@       @@@@@@@@             ")
    cprint("    @@@@@@@@@    @@@@@@@@              ")
    cprint("      @@@@@@@@@ @@@@@@@@               ")
    cprint("        @@@@@@@@@@@@@@                 ")
    cprint("          @@@@@@@@@@@                  ")
    cprint("            @@@@@@@                    ")
    cprint("              @@@@                     ")
    cprint("                                       ")
    cprint("                                       ")
    cprint("Running Quality Check on File: {}".format(basename(epi)))

    # call afni 3dinfo, we are checking the number of frames in the epi series
    proc = subprocess.run('3dinfo -nv {}'.format(epi),shell=True,stdout=subprocess.PIPE)
    # retrieve number of frames from epi series
    try:
        frames = int(str(proc.stdout,'utf-8'))
        cprint('Number of frames in {} = {}.'.format(basename(epi),frames))
    except:
        cprint('ERROR: 3dinfo returned an invalid output on {}'.format(epi))
        raise

    # Check if the number of frames for the series did not meet the threshold
    if frames <= threshold:
        # series did not meet the threshold
        cprint("Number of frames did not meet the required threshold (threshold = {})".format(threshold))
        cprint("\n")
        # Set output to False and return
        return {infile: False}

    # Check the bids JSON sidecar for slice timing info (Most of this stuff should already handled in the
    # BIDS-validator, but do a check anyway just in-case...)
    with open(epi_sidecar) as json_file:
        # load json as dict
        bids_sidecar = json.load(json_file)

        # get slice timing
        slice_timing = bids_sidecar['SliceTiming']
        cprint("Slice Timing: {}".format(slice_timing))

        # make sure it's defined and not an empty list
        if slice_timing == None or slice_timing == []:
            cprint("Slice Timing not defined in the BIDS sidecar. Check you BIDS conversion!")
            return {'epi': epi, 'epi_sidecar': epi_sidecar, 'QC': False}

    # file passed all checks, report True
    cprint("File has cleared quality control!")
    cprint("\n")
    return {'epi': epi, 'epi_sidecar': epi_sidecar, 'QC': True}

# Define reduce function for qualitycheck
def QCreduceset(QClist):
    # create lists for storing good epis
    epi = []
    epi_sidecar = []
    # Create dict to store files that passed
    for i in QClist:
        if i['QC']: # if file passed QC, store in lists
            epi.append(i['epi'])
            epi_sidecar.append(i['epi_sidecar'])

    # return lists of epis to process
    return (epi, epi_sidecar)

# Define string function to extract slice time info and write to file
extract_slicetime_func = lambda TMP_DIR: """
def extract_slicetime(epi_sidecar):
    # import necessary libraries
    import json
    import csv
    from os.path import join,basename,splitext
    from os import getcwd

    # open the sidecar file
    with open(epi_sidecar) as sidecar:
        # read the sidecar
        bids_data = json.load(sidecar)

        # extract slice time information
        slice_timing = bids_data['SliceTiming']

        # extract TR
        TR = bids_data['RepetitionTime']

    # write slice timing to file
    with open(join('{0}','{{}}.SLICETIME'.format(splitext(basename(epi_sidecar))[0])),'w') as st_file:
        wr = csv.writer(st_file,delimiter=' ')
        wr.writerow(slice_timing)

    # return timing pattern and TR
    return ('@{{}}'.format(join('{0}','{{}}.SLICETIME'.format(splitext(basename(epi_sidecar))[0]))), str(TR))""".format(
    TMP_DIR
    )

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
