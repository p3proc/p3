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
def extract_slicetime(epi_sidecar):
    # import necessary libraries
    import json
    import csv
    import os
    from os.path import join,basename,splitext

    # save to node folder (go up 2 directories bc of iterfield)
    cwd = os.path.dirname(os.path.dirname(os.getcwd()))

    # open the sidecar file
    with open(epi_sidecar) as sidecar:
        # read the sidecar
        bids_data = json.load(sidecar)

        # extract slice time information
        slice_timing = bids_data['SliceTiming']

        # extract TR
        TR = bids_data['RepetitionTime']

    # write slice timing to file
    with open(join(cwd,'{}.SLICETIME'.format(splitext(basename(epi_sidecar))[0])),'w') as st_file:
        wr = csv.writer(st_file,delimiter=' ')
        wr.writerow(slice_timing)

    # return timing pattern and TR
    return ('@{}'.format(join(cwd,'{}.SLICETIME'.format(splitext(basename(epi_sidecar))[0]))),str(TR))

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

# Extend afni 3dwarp
# define extended input spec
class ExtendedWarpInputSpec(afni.preprocess.WarpInputSpec):
    card2oblique = base.File(
        desc='spike image file name',
        argstr='-card2oblique %s',
        exists=True)

# define extended afni despike
class ExtendedWarp(afni.Warp):
    input_spec = ExtendedWarpInputSpec

# Define custom warp command function
def warp_custom(in_file,card2oblique,args=''):
    import os
    import subprocess
    import shutil

    # save to node folder (go up 2 directories bc of iterfield)
    cwd = os.path.dirname(os.path.dirname(os.getcwd()))

    # copy file to cwd
    input_file = os.path.basename(shutil.copy2(in_file,cwd))
    card_file = os.path.basename(shutil.copy2(card2oblique,cwd))

    # strip filename
    name_nii,_ = os.path.splitext(input_file)
    filename,_ = os.path.splitext(name_nii)

    print("3dWarp -verb -card2oblique {} -prefix {}_ob.nii.gz {} -overwrite {}".format(
        os.path.join(cwd,card_file),
        os.path.join(cwd,filename),
        args,
        os.path.join(cwd,input_file)))

    # spawn the 3dwarp command with the subprocess command
    warpcmd = subprocess.run(
        "3dWarp -verb -card2oblique {} -prefix {}_ob.nii.gz {} -overwrite {}".format(
            os.path.join(cwd,card_file),
            os.path.join(cwd,filename),
            args,
            os.path.join(cwd,input_file)
        ),
        stdout=subprocess.PIPE,
        shell=True
        )
    with open(os.path.join(cwd,"{}_obla2e_mat.1D".format(filename)),"w") as text_file:
        print(warpcmd.stdout.decode('utf-8'),file=text_file)

    # get the out files
    out_file = os.path.join(cwd,'{}_ob.nii.gz'.format(filename))
    ob_transform = os.path.join(cwd,'{}_obla2e_mat.1D'.format(filename))

    return (out_file,ob_transform)

# define custom register to atlas function (the afni interface in nipype sucks...)
def register_atlas(in_file):
    import os
    import shutil

    # copy file to cwd
    input_file = os.path.basename(shutil.copy2(in_file,os.getcwd()))

    # spawn the auto_tlrc process with os.system
    os.system(
        '@auto_tlrc -no_ss -base TT_N27+tlrc -input {0} -pad_input 60'.format(
            input_file,
        )
    )

    # split extension of input file
    name_nii,_ = os.path.splitext(input_file)
    filename,_ = os.path.splitext(name_nii)

    #  gzip the nifti
    os.system(
        'gzip {}'.format('{}_at.nii'.format(filename))
    )

    # get the out_file
    out_file = os.path.join(os.getcwd(),'{}_at.nii.gz'.format(filename))
    transform_file = os.path.join(os.getcwd(),'{}_at.nii.Xaff12.1D'.format(filename))

    # return the out_file
    return (out_file,transform_file)

# weight mask
def create_weightmask(in_file,no_skull):
    import subprocess
    import os
    import shutil

    # save to node folder (go up 2 directories bc of iterfield)
    cwd = os.path.dirname(os.path.dirname(os.getcwd()))

    # copy file to cwd
    input_file = os.path.basename(shutil.copy2(in_file,cwd))

    # strip filename
    name_nii,_ = os.path.splitext(input_file)
    filename,_ = os.path.splitext(name_nii)

    rtn = subprocess.run(
        '3dBrickStat -automask -percentile 90.000000 1 90.000000 {} | tail -n1 | awk \'{{print $2}}\''.format(
            no_skull
        ),
        stdout=subprocess.PIPE,
        shell=True
    )
    perc = float(rtn.stdout.decode('utf-8'))
    calc = subprocess.run(
        '3dcalc -datum float -prefix {}_weighted.nii.gz -a {} -expr \'min(1,(a/\'{}\'))\''.format(
            os.path.join(cwd,filename),
            os.path.join(cwd,input_file),
            perc
        ),
        shell=True
    )

    # return weightmask
    weightmask = os.path.join(cwd,'{}_weighted.nii.gz'.format(filename))
    return weightmask

# master transform
def mastertransform(in_file,transform1,transform2):
    import os
    import shutil

    # save to node folder (go up 2 directories bc of iterfield)
    cwd = os.path.dirname(os.path.dirname(os.getcwd()))

    # copy files to cwd
    input_file = os.path.abspath(shutil.copy2(in_file,cwd))
    transform_file1 = os.path.abspath(shutil.copy2(transform1,cwd))
    transform_file2 = os.path.abspath(shutil.copy2(transform2,cwd))

    # strip filename
    name_nii,_ = os.path.splitext(os.path.basename(transform_file1))
    filename,_ = os.path.splitext(name_nii)

    # format string
    format_string = '-ONELINE {}::WARP_DATA -I {} {} -I'.format(
        input_file,
        transform_file1,
        transform_file2
    )

    # run cat_matvec for transform to ATL space
    os.system('cat_matvec {} > {}'.format(
        format_string,
        os.path.join(cwd,'{}_rawEPI2ATL.aff12.1D'.format(filename))
    ))
    master_transform1 = os.path.join(cwd,'{}_rawEPI2ATL.aff12.1D'.format(filename))

    # format string
    format_string = '-ONELINE {} {} -I'.format(
        transform_file1,
        transform_file2
    )

    # run cat_matvec for transform to MPR space
    os.system('cat_matvec {} > {}'.format(
        format_string,
        os.path.join(cwd,'{}_rawEPI2MPR.aff12.1D'.format(filename))
    ))
    master_transform2 = os.path.join(cwd,'{}_rawEPI2MPR.aff12.1D'.format(filename))

    # return master transforms
    return master_transform1, master_transform2

# concatenate transform
def concattransform(in_file,tfm1,tfm2,tfm3,tfm4):
    import os
    import shutil

    # save to node folder (go up 2 directories bc of iterfield)
    cwd = os.path.dirname(os.path.dirname(os.getcwd()))

    # copy files to cwd
    input_file = os.path.abspath(shutil.copy2(in_file,cwd))
    tfm_file1 = os.path.abspath(shutil.copy2(tfm1,cwd))
    tfm_file2 = os.path.abspath(shutil.copy2(tfm2,cwd))
    tfm_file3 = os.path.abspath(shutil.copy2(tfm3,cwd))
    tfm_file4 = os.path.abspath(shutil.copy2(tfm4,cwd))

    # strip filename
    name_nii,_ = os.path.splitext(os.path.basename(tfm_file1))
    filename,_ = os.path.splitext(name_nii)

    # format string
    format_string = '-ONELINE {}::WARP_DATA -I {} {} -I {} {} -I'.format(
        input_file,
        tfm_file1,
        tfm_file2,
        tfm_file3,
        tfm_file4,
    )

    # run cat_matvec for transform to ATL space
    os.system('cat_matvec {} > {}'.format(
        format_string,
        os.path.join(cwd,'{}_rawEPI_viaEPI1_to_ATL.aff12.1D'.format(filename))
    ))
    master_transform = os.path.join(cwd,'{}_rawEPI_viaEPI1_to_ATL.aff12.1D'.format(filename))

    # return master transform
    return master_transform

def concattransform2(tfm1,tfm2):
    import os
    import shutil

    # save to node folder (go up 2 directories bc of iterfield)
    cwd = os.path.dirname(os.path.dirname(os.getcwd()))

    # copy files to cwd
    tfm_file1 = os.path.abspath(shutil.copy2(tfm1,cwd))
    tfm_file2 = os.path.abspath(shutil.copy2(tfm2,cwd))

    # strip filename
    name_nii,_ = os.path.splitext(os.path.basename(tfm_file1))
    filename,_ = os.path.splitext(name_nii)

    # format string
    format_string = '-ONELINE {} {} -I'.format(
        tfm_file1,
        tfm_file2
    )

    # run cat_matvec for transform to ATL space
    os.system('cat_matvec {} > {}'.format(
        format_string,
        os.path.join(cwd,'{}_XFM_rawEPI_to_EPI1.aff12.1D'.format(filename))
    ))
    master_transform = os.path.join(cwd,'{}_XFM_rawEPI_to_EPI1.aff12.1D'.format(filename))

    # return master transform
    return master_transform
