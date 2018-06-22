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
config.set('logging','workflow_level','DEBUG')
config.set('logging','workflow_level','DEBUG')
config.set('execution','hash_method','content')
config.set('execution','stop_on_first_crash','true')
logging.update_logging(config)

# initialize nodes from nodedefs
p3 = definednodes(settings)

"""
    Create Workflow
"""

# create a workflow
wf = Workflow(name='P3',base_dir=os.path.join(settings['BASE_DIR'],'tmp'))
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
    (p3.QCreduce,p3.despike,[ # despike
        ('epi','in_file')
    ]),
    (p3.despike,p3.tshift,[ # time shift
        ('out_file','in_file')
    ]),
    (p3.extract_stc,p3.tshift,[
        ('slicetiming','tpattern'),
        ('TR','tr')
    ]),

    ### Setup basefile for motion correction
    (p3.QCreduce,p3.firstrunonly,[
        ('epi','epi')
    ]),
    (p3.firstrunonly,p3.extractroi,[
        ('epi','in_file')
    ]),
    (p3.extractroi,p3.firstframefirstrun,[
        ('roi_file','refimg')
    ]),

    ### Do the actual motion correction
    # Align to first frame of first run
    (p3.firstframefirstrun,p3.volreg,[
        ('refimg','basefile')
    ]),
    (p3.tshift,p3.volreg,[
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
    (p3.fsl_skullstrip,p3.maskop3,[
        ('out_file','in_file_a')
    ]),
    (p3.afni_skullstrip,p3.maskop3,[
        ('out_file','in_file_b')
    ]),
    (p3.uniform,p3.maskop3,[
        ('out_file','in_file_c')
    ]),
    (p3.maskop2[2],p3.maskop4,[
        ('out_file','in_file_a')
    ]),
    (p3.maskop3,p3.maskop4,[
        ('out_file','in_file_b')
    ]),
    (p3.fileselection,p3.maskop4,[
        ('T1','in_file_c')
    ]),
    # final noskull mprage
    (p3.maskop4,p3.skullstripped_mprage,[
        ('out_file','noskull')
    ]),


    # Register the final skullstripped mprage to atlas
    (p3.skullstripped_mprage,p3.register,[
        ('noskull','in_file')
    ]),
    (p3.register,p3.skullstripped_atlas_mprage,[
        ('out_file','noskull_at'),
        ('transform_file','transform')
    ]),

    # Skullstrip the EPI image
    (p3.firstframefirstrun,p3.epi_skullstrip,[
        ('refimg','in_file')
    ]),
    (p3.firstframefirstrun,p3.epi_automask,[
        ('refimg','in_file')
    ]),
    (p3.epi_automask,p3.epi_3dcalc,[
        ('brain_file','in_file_a')
    ]),
    (p3.epi_skullstrip,p3.epi_3dcalc,[
        ('out_file','in_file_b')
    ]),
    (p3.firstframefirstrun,p3.epi_3dcalc,[
        ('refimg','in_file_c')
    ]),

    # deoblique
    (p3.epi_3dcalc,p3.warp,[
        ('out_file','card2oblique')
    ]),
    (p3.skullstripped_mprage,p3.warp,[
        ('noskull','in_file')
    ]),
    (p3.warp_args,p3.warp,[
        ('args','args')
    ]),
    (p3.warp,p3.noskull_obla2e,[
        ('out_file','noskull_ob'),
        ('ob_transform','noskull_obla2e_mat')
    ]),

    # resample the EPIREF to MPRAGE
    (p3.noskull_obla2e,p3.resample,[
        ('noskull_ob','master')
    ]),
    (p3.epi_3dcalc,p3.resample,[
        ('out_file','in_file')
    ]),

    # create weightmask
    (p3.resample,p3.weightmask,[
        ('out_file','in_file')
    ]),
    (p3.epi_3dcalc,p3.weightmask,[
        ('out_file','no_skull')
    ]),

    # register mprage to tcat
    (p3.weightmask,p3.registert12tcat,[
        ('out_file','weight')
    ]),
    (p3.resample,p3.registert12tcat,[
        ('out_file','reference')
    ]),
    (p3.noskull_obla2e,p3.registert12tcat,[
        ('noskull_ob','in_file')
    ]),

    # Create Atlas-Registered BOLD Data
    (p3.skullstripped_atlas_mprage,p3.transformepi2epi2mpr2atl,[
        ('noskull_at','in_file')
    ]),
    (p3.noskull_obla2e,p3.transformepi2epi2mpr2atl,[
        ('noskull_obla2e_mat','tfm1')
    ]),
    (p3.registert12tcat,p3.transformepi2epi2mpr2atl,[
        ('out_matrix','tfm2')
    ]),
    (p3.volreg,p3.transformepi2epi2mpr2atl,[
        ('oned_matrix_save','tfm3')
    ]),
    (p3.tshift,p3.alignepi2atl,[
        ('out_file','in_file')
    ]),
    (p3.transformepi2epi2mpr2atl,p3.alignepi2atl,[
        ('master_transform','in_matrix')
    ]),
    (p3.skullstripped_atlas_mprage,p3.alignepi2atl,[
        ('noskull_at','reference')
    ]),

    # Output
    (p3.alignepi2atl,p3.output[0],[
        ('out_file','output')
    ]),
    (p3.transformepi2epi2mpr2atl,p3.output[1],[
        ('master_transform','output')
    ]),
])
wf.run()
#print(p3.allineate_orig.inputs)
#wf.run(plugin='MultiProc')
wf.write_graph()
