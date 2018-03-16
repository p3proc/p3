#!/usr/bin/env python3.6

import os
from nipype import Node,MapNode,Workflow,IdentityInterface
from nipype.interfaces import afni,base,fsl,freesurfer
from nipype.interfaces.io import SelectFiles,DataSink
from nipype.interfaces.utility import Function

"""
    Settings
"""
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
SUBJECTS_DIR = os.path.join(BASE_DIR,'output','freesurfer_output')
TMP_DIR = '/home/vana/Projects/p3/tmp'
IGNOREFRAMES = 4

# make directories if not exist
os.makedirs(SUBJECTS_DIR,exist_ok=True)
os.makedirs(TMP_DIR,exist_ok=True)

"""
    Define Custom Functions and Interfaces
"""

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

# Define function to extract slice time info and write to file
def extract_slicetime(epi_sidecar,TMP_DIR=TMP_DIR):
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
    with open(join(TMP_DIR,'{}.SLICETIME'.format(splitext(basename(epi_sidecar))[0])),'w') as st_file:
        wr = csv.writer(st_file,delimiter=' ')
        wr.writerow(slice_timing)

    # return timing pattern and TR
    return ("@{}".format(join(TMP_DIR,'{}.SLICETIME'.format(splitext(basename(epi_sidecar))[0]))), str(TR))

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

# Extend afni volreg
# Extend afni volreg input spec to register to specific frame
class ExtendedVolregInputSpec(afni.preprocess.VolregInputSpec):
    basefile = base.File(
        desc='base file for registration',
        argstr="-base %s'[{}]'".format(IGNOREFRAMES),
        position=-6,
        exists=True)

# define extended afni volreg
class ExtendedVolreg(afni.Volreg):
    input_spec = ExtendedVolregInputSpec

"""
    Define Nodes for nipype workflow
"""

# Create an Identity interface to select subjects
infosource = Node(
    IdentityInterface(
        fields=['subject_id']
    ),
    iterables = [('subject_id',['sub-CTS200'])],
    name='infosource'
)

# Select epis and T1s (and their sidecars)
fileselection = Node(
    SelectFiles(
        {
            'epi': os.path.join(BASE_DIR,'dataset','{subject_id}','func','*baseline*.nii.gz'),
            'epi_sidecar': os.path.join(BASE_DIR,'dataset','{subject_id}','func','*baseline*.json'),
            'T1': os.path.join(BASE_DIR,'dataset','{subject_id}','anat','*T1w*.nii.gz'),
            'T1_sidecar': os.path.join(BASE_DIR,'dataset','{subject_id}','anat','*T1w*.json')
        }
    ),
    name='selectfiles'
)

# Do QC on all files
QC = MapNode(
    Function(
        input_names=['epi','epi_sidecar'],
        output_names=['QClist'],
        function=qualitycheck
    ),
    iterfield=['epi','epi_sidecar'],
    name='QC'
)

# Reduce set based on QC check
QCreduce = Node(
    Function(
        input_names=['QClist'],
        output_names=['epi','epi_sidecar'],
        function=QCreduceset
    ),
    name='QCreduce'
)

# Despike epi data
despike1 = MapNode(
    ExtendedDespike(
        args="-ignore {} -NEW -nomask".format(
            IGNOREFRAMES
        ),
        outputtype="NIFTI_GZ"
    ),
    iterfield=['in_file'],
    name='despike1'
)
despike2 = MapNode(
    ExtendedDespike(
        args="-ignore {} -NEW -nomask".format(
            IGNOREFRAMES
        ),
        outputtype="NIFTI_GZ"
    ),
    iterfield=['in_file'],
    name='despike2'
)

# extract slice timing so we can pass it to slice time correction
extract_stc = MapNode(
    Function(
        input_names=['epi_sidecar'],
        output_names=['slicetiming','TR'],
        function=extract_slicetime
    ),
    iterfield=['epi_sidecar'],
    name='extract_stc'
)

# timeshift data
tshift1 = MapNode(
    afni.TShift(
        args="-heptic",
        ignore=IGNOREFRAMES,
        tzero=0,
        outputtype="NIFTI_GZ"
    ),
    iterfield=['in_file','tpattern','tr'],
    name='tshift1'
)
tshift2 = MapNode(
    afni.TShift(
        args="-heptic",
        ignore=IGNOREFRAMES,
        tzero=0,
        outputtype="NIFTI_GZ"
    ),
    iterfield=['in_file','tpattern','tr'],
    name='tshift2'
)

# Motion correction
volreg1 = MapNode(
    ExtendedVolreg(
        args="-heptic -maxite {}".format(
            25
        ),
        verbose=True,
        zpad=10,
        outputtype="NIFTI_GZ"
    ),
    iterfield=['basefile','in_file'],
    name='volreg1'
)
volreg2 = MapNode(
    ExtendedVolreg(
        args="-heptic -maxite {}".format(
            25
        ),
        verbose=True,
        zpad=10,
        outputtype="NIFTI_GZ"
    ),
    iterfield=['basefile','in_file'],
    name='volreg2'
)
volreg3 = MapNode(
    ExtendedVolreg(
        args="-heptic -maxite {}".format(
            25
        ),
        verbose=True,
        zpad=10,
        outputtype="NIFTI_GZ"
    ),
    iterfield=['basefile','in_file'],
    name='volreg3'
)
volreg4 = MapNode(
    ExtendedVolreg(
        args="-heptic -maxite {}".format(
            25
        ),
        verbose=True,
        zpad=10,
        outputtype="NIFTI_GZ"
    ),
    iterfield=['basefile','in_file'],
    name='volreg4'
)
volreg5 = MapNode(
    ExtendedVolreg(
        args="-heptic -maxite {}".format(
            25
        ),
        verbose=True,
        zpad=10,
        outputtype="NIFTI_GZ"
    ),
    iterfield=['basefile','in_file'],
    name='volreg5'
)

# Skullstrip
# skullstrip mprage (afni)
afni_skullstrip = Node(
    afni.SkullStrip(
        args="-orig_vol",
        outputtype="NIFTI_GZ"
    ),
    name='afni_skullstrip'
)
# skullstrip mprage (fsl)
fsl_skullstrip = Node(
    fsl.BET(),
    name='fsl_skullstrip'
)

# Recon-all
reconall = Node(
    freesurfer.ReconAll(
        directive='all',
        subjects_dir=SUBJECTS_DIR,
        parallel=True,
        openmp=4
    ),
    name='reconall'
)

# MRIConvert
orig_convert = Node(
    freesurfer.MRIConvert(
        in_type='mgz',
        out_type='niigz'
    ),
    name='orig_mriconvert'
)
brainmask_convert = Node(
    freesurfer.MRIConvert(
        in_type='mgz',
        out_type='niigz'
    ),
    name='brainmask_mriconvert'
)

# 3dAllineate
allineate = Node(
    afni.Allineate(
        no_pad=True,
        out_matrix='FSorig.XFM.FS2MPR.aff12.1D',
        outputtype='NIFTI_GZ'
    ),
    name='3dallineate'
)

# 3dRefit
refit = Node(
    afni.Refit(),
    name='3drefit'
)

# Output
output1 = Node(
     DataSink(base_directory=BASE_DIR),
     name='output1'
)
output2 = Node(
     DataSink(base_directory=BASE_DIR),
     name='output2'
)
output3 = Node(
     DataSink(base_directory=BASE_DIR),
     name='output3'
)

"""
    Create Workflow
"""

wf = Workflow(name='P3')
wf.connect([
    # File selection Nodes
    (infosource,fileselection,[
        ('subject_id','subject_id')
    ]),
    (fileselection,QC,[
        ('epi','epi'),
        ('epi_sidecar','epi_sidecar')
    ]),
    # Quality Control
    (QC,QCreduce,[
        ('QClist','QClist')
    ]),
    # Extract Slice timing info + TR
    (QCreduce,extract_stc,[
        ('epi_sidecar','epi_sidecar')
    ]),
    # Time Shift/Despiking
    (QCreduce,despike1,[
        ('epi','in_file')
    ]),
    (despike1,tshift1,[
        ('out_file','in_file')
    ]),
    (extract_stc,tshift1,[
        ('slicetiming','tpattern'),
        ('TR','tr')
    ]),
    (QCreduce,tshift2,[
        ('epi','in_file')
    ]),
    (extract_stc,tshift2,[
        ('slicetiming','tpattern'),
        ('TR','tr')
    ]),
    (tshift2,despike2,[
        ('out_file','in_file')
    ]),
    # Motion Correction
    # No despike, No stc
    # (QCreduce,volreg1,[
    #     ('epi','basefile')
    # ]),
    # (QCreduce,volreg1,[
    #     ('epi','in_file')
    # ]),
    # despike only
    (QCreduce,volreg2,[
        ('epi','basefile')
    ]),
    (despike1,volreg2,[
        ('out_file','in_file')
    ]),
    # despike + stc
    (QCreduce,volreg3,[
        ('epi','basefile')
    ]),
    (tshift1,volreg3,[
        ('out_file','in_file')
    ]),
    # stc only
    (QCreduce,volreg4,[
        ('epi','basefile')
    ]),
    (tshift2,volreg4,[
        ('out_file','in_file')
    ]),
    # stc + despike
    (QCreduce,volreg5,[
        ('epi','basefile')
    ]),
    (despike2,volreg5,[
        ('out_file','in_file')
    ]),
    # # Skullstrip
    # (fileselection,afni_skullstrip,[
    #     ('T1','in_file')
    # ]),
    # (fileselection,fsl_skullstrip,[
    #     ('T1','in_file')
    # ]),
    # # Recon-all
    # (infosource,reconall,[
    #     ('subject_id','subject_id')
    # ]),
    # (fileselection,reconall,[
    #     ('T1','T1_files')
    # ]),
    # # Convert orig and brainmask
    # (reconall,orig_convert,[
    #     ('orig','in_file')
    # ]),
    # (reconall,brainmask_convert,[
    #     ('brainmask','in_file')
    # ]),
    # Align T1 to ATLAS
    # (orig_convert,allineate,[
    #     ('out_file','in_file')
    # ]),
    # (fileselection,allineate,[
    #     ('T1','reference')
    # ]),
    # (allineate,output1,[
    #     ('out_matrix','output')
    # ]),
    # (allineate,output2,[
    #     ('out_file','output')
    # ])
])
#wf.run()
wf.write_graph()
