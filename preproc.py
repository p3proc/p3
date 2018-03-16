#!/usr/bin/env python3.6

import os
from nipype import Node,MapNode,Workflow,IdentityInterface
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
slicetime = exslt(TMP_DIR) # create object
extract_stc = MapNode(
    Function(
        input_names=['epi_sidecar'],
        output_names=['slicetiming','TR'],
        function=slicetime.extract_slicetime
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
ExVolreg = ExtendedVolreg.init_class(IGNOREFRAMES)
volreg1 = MapNode(
    ExVolreg(
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
    ExVolreg(
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
    ExVolreg(
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
    ExVolreg(
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
    ExVolreg(
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
    (QCreduce,volreg1,[
        ('epi','basefile')
    ]),
    (QCreduce,volreg1,[
        ('epi','in_file')
    ]),
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
    (allineate,output1,[
        ('out_matrix','output')
    ]),
    (allineate,output2,[
        ('out_file','output')
    ])
])
#wf.run()
wf.write_graph()
