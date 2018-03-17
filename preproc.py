#!/usr/bin/env python3.6

import os
from nipype import Workflow,config,logging
from nodedefs import * # import all defined nodes

"""
    Settings
"""
settings = {}
settings['BASE_DIR'] = os.path.dirname(os.path.realpath(__file__))
settings['ignoreframes'] = 4
#config.enable_debug_mode()
#logging.update_logging(config)

# initialize nodes from nodedefs
p3 = definednodes(settings)

"""
    Create Workflow
"""

# create a workflow
wf = Workflow(name='P3')
wf.connect([ # connect nodes (see nodedefs.py for further details on each node)
    ### File selection Nodes
    (p3.infosource,p3.fileselection,[
        ('subject_id','subject_id')
    ]),

    ### Quality Control
    (p3.fileselection,p3.QC,[
        ('epi','epi'),
        ('epi_sidecar','epi_sidecar')
    ]),
    (p3.QC,p3.QCreduce,[
        ('QClist','QClist')
    ]),

    ### Extract Slice timing info + TR
    (p3.QCreduce,p3.extract_stc,[
        ('epi_sidecar','epi_sidecar')
    ]),

    ### Time Shift/Despiking
    (p3.QCreduce,p3.despike[0],[ # despike
        ('epi','in_file')
    ]),
    (p3.despike[0],p3.tshift[0],[ # despike + time shift
        ('out_file','in_file')
    ]),
    (p3.extract_stc,p3.tshift[0],[ # despike + time shift
        ('slicetiming','tpattern'),
        ('TR','tr')
    ]),
    (p3.QCreduce,p3.tshift[1],[ # timeshift
        ('epi','in_file')
    ]),
    (p3.extract_stc,p3.tshift[1],[ # timeshift
        ('slicetiming','tpattern'),
        ('TR','tr')
    ]),
    (p3.tshift[1],p3.despike[1],[ # timeshift + despike
        ('out_file','in_file')
    ]),

    ### Setup basefile for motion correction
    (p3.QCreduce,p3.extractroi[0],[
        ('epi','in_file')
    ]),
    (p3.QCreduce,p3.firstrunonly,[
        ('epi','epi')
    ]),
    (p3.firstrunonly,p3.extractroi[1],[
        ('epi','in_file')
    ]),

    ### Do the actual motion correction
    # Align to first frame of each run
    # No despike, No stc
    (p3.extractroi[0],p3.volreg[0],[
        ('roi_file','basefile')
    ]),
    (p3.QCreduce,p3.volreg[0],[
        ('epi','in_file')
    ]),
    # despike only
    (p3.extractroi[0],p3.volreg[1],[
        ('roi_file','basefile')
    ]),
    (p3.despike[0],p3.volreg[1],[
        ('out_file','in_file')
    ]),
    # despike + stc
    (p3.extractroi[0],p3.volreg[2],[
        ('roi_file','basefile')
    ]),
    (p3.tshift[0],p3.volreg[2],[
        ('out_file','in_file')
    ]),
    # stc only
    (p3.extractroi[0],p3.volreg[3],[
        ('roi_file','basefile')
    ]),
    (p3.tshift[1],p3.volreg[3],[
        ('out_file','in_file')
    ]),
    # stc + despike
    (p3.extractroi[0],p3.volreg[4],[
        ('roi_file','basefile')
    ]),
    (p3.despike[1],p3.volreg[4],[
        ('out_file','in_file')
    ]),
    # Align to first frame of first run
    # No despike, No stc
    (p3.extractroi[1],p3.volreg[5],[
        ('roi_file','basefile')
    ]),
    (p3.QCreduce,p3.volreg[5],[
        ('epi','in_file')
    ]),
    # despike only
    (p3.extractroi[1],p3.volreg[6],[
        ('roi_file','basefile')
    ]),
    (p3.despike[0],p3.volreg[6],[
        ('out_file','in_file')
    ]),
    # despike + stc
    (p3.extractroi[1],p3.volreg[7],[
        ('roi_file','basefile')
    ]),
    (p3.tshift[0],p3.volreg[7],[
        ('out_file','in_file')
    ]),
    # stc only
    (p3.extractroi[1],p3.volreg[8],[
        ('roi_file','basefile')
    ]),
    (p3.tshift[1],p3.volreg[8],[
        ('out_file','in_file')
    ]),
    # stc + despike
    (p3.extractroi[1],p3.volreg[9],[
        ('roi_file','basefile')
    ]),
    (p3.despike[1],p3.volreg[9],[
        ('out_file','in_file')
    ]),

    ### Skullstrip
    # AFNI skull stripped images are missing edge of cortical ribbon often
    # FSL has more of the ribbon often but can have weird neck stuff too
    # Freesurfer rarely clips and is the most lenient of the skullstrips
    (p3.fileselection,p3.afni_skullstrip,[
        ('T1','in_file')
    ]),
    (p3.fileselection,p3.fsl_skullstrip,[
        ('T1','in_file')
    ]),

    ### Recon-all
    (p3.infosource,p3.reconall,[
        ('subject_id','subject_id')
    ]),
    (p3.fileselection,p3.reconall,[
        ('T1','T1_files')
    ]),

    ### REGISTER THE MPRAGE TO THE ATLAS
    # Convert orig and brainmask
    (p3.reconall,p3.orig_convert,[
        ('orig','in_file')
    ]),
    (p3.reconall,p3.brainmask_convert,[
        ('brainmask','in_file')
    ]),

    # Create transformation of FSorig to T1 
    (p3.orig_convert,p3.allineate_orig,[
        ('out_file','in_file')
    ]),
    (p3.fileselection,p3.allineate_orig,[
        ('T1','reference')
    ]),
    (p3.afni_skullstrip,p3.refit_setup,[
        ('out_file','noskull_T1')
    ]),
    (p3.refit_setup,p3.refit[0],[
        ('refit_input','atrcopy')
    ]),
    (p3.allineate_orig,p3.refit[0],[
        ('out_file','in_file')
    ]),
    
    # create atlas-aligned skull stripped brainmask
    (p3.brainmask_convert,p3.allineate_bm,[
        ('out_file','in_file')
    ]),
    (p3.fileselection,p3.allineate_bm,[
        ('T1','reference')
    ]),
    (p3.allineate_orig,p3.allineate_bm,[
        ('out_matrix','in_matrix')
    ]),
    (p3.refit_setup,p3.refit[1],[
        ('refit_input','atrcopy')
    ]),
    (p3.allineate_bm,p3.refit[1],[
        ('out_file','in_file')
    ]),
    
    # intensities are differently scaled in FS image, replace with native intensities for uniformity
    (p3.fileselection,p3.uniform,[
        ('T1','in_file_a')
    ]),
    (p3.refit[1],p3.uniform,[
        ('out_file','in_file_b')
    ]),
    
    # Use OR of AFNI, FSL, and FS skullstrips within a 3-shell expanded AFNI mask as final
    (p3.afni_skullstrip,p3.maskop1,[
        ('out_file','in_file_a')
    ]),
    (p3.maskop1,p3.maskop2[0],[
        ('out_file','in_file_a')
    ]),
    (p3.maskop2[0],p3.maskop2[1],[
        ('out_file','in_file_a')
    ]),
    (p3.maskop2[1],p3.maskop2[2],[
        ('out_file','in_file_a')
    ]),
    (p3.maskop2[2],p3.maskop3,[
        ('out_file','in_file_a')
    ]),
    (p3.fsl_skullstrip,p3.maskop3,[
        ('out_file','in_file_b')
    ]),
    (p3.afni_skullstrip,p3.maskop3,[
        ('out_file','in_file_c')
    ]),
    (p3.fileselection,p3.maskop4,[ # apparently the old way of getting noskull mprage...
        ('T1','in_file_a')
    ]),
    (p3.maskop3,p3.maskop4,[
        ('out_file','in_file_b')
    ]),
    (p3.fsl_skullstrip,p3.maskop5,[
        ('out_file','in_file_a')
    ]),
    (p3.afni_skullstrip,p3.maskop5,[
        ('out_file','in_file_b')
    ]),
    (p3.uniform,p3.maskop5,[
        ('out_file','in_file_c')
    ]),
    (p3.maskop2[2],p3.maskop6,[ # final noskull mprage
        ('out_file','in_file_a')
    ]),
    (p3.maskop5,p3.maskop6,[
        ('out_file','in_file_b')
    ]),
    (p3.fileselection,p3.maskop6,[
        ('T1','in_file_c')
    ]),

    # Output
    (p3.maskop6,p3.output[0],[
        ('out_file','output')
    ])
])
wf.run()
wf.write_graph()
