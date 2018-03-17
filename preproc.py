#!/usr/bin/env python3.6

import os
from nipype import Node,MapNode,Workflow,IdentityInterface,config,logging
from nipype.interfaces import afni,fsl,freesurfer
from nipype.interfaces.io import SelectFiles,DataSink
from nipype.interfaces.utility import Function
from custom import *

"""
    Settings
"""
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
SUBJECTS_DIR = os.path.join(BASE_DIR,'output','freesurfer_output')
TMP_DIR = os.path.join(BASE_DIR,'tmp')
IGNOREFRAMES = 4
#config.enable_debug_mode()
#logging.update_logging(config)

# make directories if not exist
os.makedirs(SUBJECTS_DIR,exist_ok=True)
os.makedirs(TMP_DIR,exist_ok=True)

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
extract_slicetime = extract_slicetime_func(TMP_DIR) # create object
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

# Setup basefile for volreg
firstrunonly = Node(
    Function(
        input_names=['epi'],
        output_names=['epi'],
        function=lambda epi: [epi[0] for item in epi]
    ),
    name='retrievefirstrun'
)
extractroi1 = MapNode( # this will moco the images to the first frame of the each run
    fsl.ExtractROI(
        t_min=IGNOREFRAMES,
        t_size=1,
        output_type='NIFTI_GZ'
    ),
    iterfield=['in_file'],
    name='extractroi1'
)
extractroi2 = MapNode( # this will moco the images to the first frame of first run
    fsl.ExtractROI(
        t_min=IGNOREFRAMES,
        t_size=1,
        output_type='NIFTI_GZ'
    ),
    iterfield=['in_file'],
    name='extractroi2'
)

# Motion correction
volreg1 = MapNode(
    afni.Volreg(
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
    afni.Volreg(
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
    afni.Volreg(
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
    afni.Volreg(
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
    afni.Volreg(
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
volreg6 = MapNode(
    afni.Volreg(
        args="-heptic -maxite {}".format(
            25
        ),
        verbose=True,
        zpad=10,
        outputtype="NIFTI_GZ"
    ),
    iterfield=['basefile','in_file'],
    name='volreg6'
)
volreg7 = MapNode(
    afni.Volreg(
        args="-heptic -maxite {}".format(
            25
        ),
        verbose=True,
        zpad=10,
        outputtype="NIFTI_GZ"
    ),
    iterfield=['basefile','in_file'],
    name='volreg7'
)
volreg8 = MapNode(
    afni.Volreg(
        args="-heptic -maxite {}".format(
            25
        ),
        verbose=True,
        zpad=10,
        outputtype="NIFTI_GZ"
    ),
    iterfield=['basefile','in_file'],
    name='volreg8'
)
volreg9 = MapNode(
    afni.Volreg(
        args="-heptic -maxite {}".format(
            25
        ),
        verbose=True,
        zpad=10,
        outputtype="NIFTI_GZ"
    ),
    iterfield=['basefile','in_file'],
    name='volreg9'
)
volreg10 = MapNode(
    afni.Volreg(
        args="-heptic -maxite {}".format(
            25
        ),
        verbose=True,
        zpad=10,
        outputtype="NIFTI_GZ"
    ),
    iterfield=['basefile','in_file'],
    name='volreg10'
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
        out_file=os.path.join(TMP_DIR,'orig_out_allineate.nii.gz'), # bug in nipype, it doesn't produce output without setting this parameter... we write this to our own tmp dir for now...
        out_matrix='FSorig.XFM.FS2MPR.aff12.1D',
        overwrite=True,
        outputtype='NIFTI_GZ'
    ),
    name='3dallineate'
)

# Inline function for setting up to copy IJK_TO_DICOM_REAL file attribute
refit_setup = Node(
    Function(
        input_names=['noskull_T1'],
        output_names=['refit_input'],
        function=lambda noskull_T1: (noskull_T1,'IJK_TO_DICOM_REAL')
    ),
    name='refitsetup'
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
    (QCreduce,despike1,[ # despike
        ('epi','in_file')
    ]),
    (despike1,tshift1,[ # despike + time shift
        ('out_file','in_file')
    ]),
    (extract_stc,tshift1,[ # despike + time shift
        ('slicetiming','tpattern'),
        ('TR','tr')
    ]),
    (QCreduce,tshift2,[ # timeshift
        ('epi','in_file')
    ]),
    (extract_stc,tshift2,[ # timeshift
        ('slicetiming','tpattern'),
        ('TR','tr')
    ]),
    (tshift2,despike2,[ # timeshift + despike
        ('out_file','in_file')
    ]),

    # Motion Correction
    # Setup basefile
    (QCreduce,extractroi1,[
        ('epi','in_file')
    ]),
    (QCreduce,firstrunonly,[
        ('epi','epi') 
    ]),
    (firstrunonly,extractroi2,[
        ('epi','in_file')
    ]),
    
    # Do the actual motion correction
    # Align to first frame of each run
    # No despike, No stc
    (extractroi1,volreg1,[
        ('roi_file','basefile')
    ]),
    (QCreduce,volreg1,[
        ('epi','in_file')
    ]),
    # despike only
    (extractroi1,volreg2,[
        ('roi_file','basefile')
    ]),
    (despike1,volreg2,[
        ('out_file','in_file')
    ]),
    # despike + stc
    (extractroi1,volreg3,[
        ('roi_file','basefile')
    ]),
    (tshift1,volreg3,[
        ('out_file','in_file')
    ]),
    # stc only
    (extractroi1,volreg4,[
        ('roi_file','basefile')
    ]),
    (tshift2,volreg4,[
        ('out_file','in_file')
    ]),
    # stc + despike
    (extractroi1,volreg5,[
        ('roi_file','basefile')
    ]),
    (despike2,volreg5,[
        ('out_file','in_file')
    ]),
    # Align to first frame of first run
    # No despike, No stc
    (extractroi2,volreg6,[
        ('roi_file','basefile')
    ]),
    (QCreduce,volreg6,[
        ('epi','in_file')
    ]),
    # despike only
    (extractroi2,volreg7,[
        ('roi_file','basefile')
    ]),
    (despike1,volreg7,[
        ('out_file','in_file')
    ]),
    # despike + stc
    (extractroi2,volreg8,[
        ('roi_file','basefile')
    ]),
    (tshift1,volreg8,[
        ('out_file','in_file')
    ]),
    # stc only
    (extractroi2,volreg9,[
        ('roi_file','basefile')
    ]),
    (tshift2,volreg9,[
        ('out_file','in_file')
    ]),
    # stc + despike
    (extractroi2,volreg10,[
        ('roi_file','basefile')
    ]),
    (despike2,volreg10,[
        ('out_file','in_file')
    ]),
    
    # Skullstrip
    (fileselection,afni_skullstrip,[
        ('T1','in_file')
    ]),
    (fileselection,fsl_skullstrip,[
        ('T1','in_file')
    ]),

    # Recon-all
    (infosource,reconall,[
        ('subject_id','subject_id')
    ]),
    (fileselection,reconall,[
        ('T1','T1_files')
    ]),

    # Convert orig and brainmask
    (reconall,orig_convert,[
        ('orig','in_file')
    ]),
    (reconall,brainmask_convert,[
        ('brainmask','in_file')
    ]),

    # Align T1 to ATLAS
    (orig_convert,allineate,[
        ('out_file','in_file')
    ]),
    (fileselection,allineate,[
        ('T1','reference')
    ]),
    (afni_skullstrip,refit_setup,[
        ('out_file','noskull_T1')
    ]),
    (refit_setup,refit,[
        ('refit_input','atrcopy')
    ]),
    (allineate,refit,[
        ('out_file','in_file')
    ]),

    # Output Data
    (allineate,output1,[
        ('out_matrix','output')
    ]),
    (refit,output2,[
        ('out_file','output')
    ])
])
wf.run()
wf.write_graph()
