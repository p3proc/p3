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
config.enable_debug_mode()
logging.update_logging(config)

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

    ### Convert orig and brainmask
    (p3.reconall,p3.orig_convert,[
        ('orig','in_file')
    ]),
    (p3.reconall,p3.brainmask_convert,[
        ('brainmask','in_file')
    ]),

    ### Align T1 to ATLAS
    (p3.orig_convert,p3.allineate,[
        ('out_file','in_file')
    ]),
    (p3.fileselection,p3.allineate,[
        ('T1','reference')
    ]),
    (p3.afni_skullstrip,p3.refit_setup,[
        ('out_file','noskull_T1')
    ]),
    (p3.refit_setup,p3.refit,[
        ('refit_input','atrcopy')
    ]),
    (p3.allineate,p3.refit,[
        ('out_file','in_file')
    ]),

    ### Output Data
    (p3.allineate,p3.output1,[
        ('out_matrix','output')
    ]),
    (p3.refit,p3.output2,[
        ('out_file','output')
    ])
])
wf.run()
wf.write_graph()
