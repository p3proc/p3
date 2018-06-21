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
    (p3.QCreduce,p3.extractroi[0],[
        ('epi','in_file')
    ]),
    (p3.QCreduce,p3.firstrunonly,[
        ('epi','epi')
    ]),
    (p3.firstrunonly,p3.extractroi[1],[
        ('epi','in_file')
    ]),
    (p3.extractroi[0],p3.firstframeeachrun,[
        ('roi_file','refimg')
    ]),
    (p3.extractroi[1],p3.firstframefirstrun,[
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
    # (p3.maskop2[2],p3.maskop3,[
    #     ('out_file','in_file_a')
    # ]),
    # (p3.fsl_skullstrip,p3.maskop3,[
    #     ('out_file','in_file_b')
    # ]),
    # (p3.afni_skullstrip,p3.maskop3,[
    #     ('out_file','in_file_c')
    # ]),
    # (p3.fileselection,p3.maskop4,[ # apparently the old way of getting noskull mprage...
    #     ('T1','in_file_a')
    # ]),
    # (p3.maskop3,p3.maskop4,[
    #     ('out_file','in_file_b')
    # ]),
    (p3.fsl_skullstrip,p3.maskop5,[
        ('out_file','in_file_a')
    ]),
    (p3.afni_skullstrip,p3.maskop5,[
        ('out_file','in_file_b')
    ]),
    (p3.uniform,p3.maskop5,[
        ('out_file','in_file_c')
    ]),
    (p3.maskop2[2],p3.maskop6,[
        ('out_file','in_file_a')
    ]),
    (p3.maskop5,p3.maskop6,[
        ('out_file','in_file_b')
    ]),
    (p3.fileselection,p3.maskop6,[
        ('T1','in_file_c')
    ]),
    # final noskull mprage
    (p3.maskop6,p3.skullstripped_mprage,[
        ('out_file','noskull')
    ]),


    # Register the final skullstripped mprage to atlas
    (p3.skullstripped_mprage,p3.register[0],[
        ('noskull','in_file')
    ]),
    (p3.register[0],p3.skullstripped_atlas_mprage,[
        ('out_file','noskull_at'),
        ('transform_file','transform')
    ]),


    # Transform the unskull stripped mprage
    # (p3.fileselection,p3.allineate_unskullstripped[0],[
    #     ('T1','in_file')
    # ]),
    # (p3.skullstripped_atlas_mprage,p3.allineate_unskullstripped[0],[
    #     ('transform','in_matrix')
    # ]),

    #For comparison, calculate the transform with only the AFNI version
    # (p3.afni_skullstrip,p3.register[1],[
    #     ('out_file','in_file')
    # ]),

    #Transform the un-skull-stripped mprage (AFNI version)
    # (p3.fileselection,p3.allineate_unskullstripped[1],[
    #     ('T1','in_file')
    # ]),
    # (p3.register[1],p3.allineate_unskullstripped[1],[
    #     ('transform_file','in_matrix')
    # ]),

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

    # # Transform rawEPI in ATL space and MPR space
    # (p3.skullstripped_atlas_mprage,p3.mastertransform,[
    #     ('noskull_at','in_file')
    # ]),
    # (p3.noskull_obla2e,p3.mastertransform,[
    #     ('noskull_obla2e_mat','transform1')
    # ]),
    # (p3.registert12tcat,p3.mastertransform,[
    #     ('out_matrix','transform2')
    # ]),

    # # Transform the tcat image into atlas space
    # (p3.skullstripped_atlas_mprage,p3.transformtcat2atl,[
    #     ('noskull_at','reference')
    # ]),
    # (p3.mastertransform,p3.transformtcat2atl,[
    #     ('out_file','in_matrix')
    # ]),
    # (p3.epi_3dcalc,p3.transformtcat2atl,[
    #     ('out_file','in_file')
    # ]),

    # # Transform the tcat image into mpr space
    # (p3.skullstripped_mprage,p3.transformtcat2mpr,[
    #     ('noskull','reference')
    # ]),
    # (p3.mastertransform,p3.transformtcat2mpr,[
    #     ('out_file2','in_matrix')
    # ]),
    # (p3.epi_3dcalc,p3.transformtcat2mpr,[
    #     ('out_file','in_file')
    # ]),
    #
    # # restore obliquity
    # (p3.skullstripped_mprage,p3.prermoblique,[
    #     ('noskull','in1')
    # ]),
    # (p3.prermoblique,p3.remakeoblique,[
    #     ('out','atrcopy')
    # ]),
    # (p3.transformtcat2mpr,p3.remakeoblique,[
    #     ('out_file','in_file')
    # ]),

    # you have to do cross-run alignment for anatomical consistency across runs
    # 3dvolreg can do this for you, or you can do it yourself. this is the yourself version.
    # here we register the reference images from each run to the first run reference
    # NOTE: MI and NMI seem to do a better intra-modal job of registering than correlation-based methods
    # (p3.firstframeeachrun,p3.deobliquemasterepiref,[
    #     ('refimg','card2oblique')
    # ]),
    # (p3.firstframefirstrun,p3.deobliquemasterepiref,[
    #     ('refimg','in_file')
    # ]),
    # (p3.deobliquemasterepiref,p3.resampleepiref2masterepiref,[
    #     ('out_file','master')
    # ]),
    # (p3.firstframeeachrun,p3.resampleepiref2masterepiref,[
    #     ('refimg','in_file')
    # ]),
    # (p3.deobliquemasterepiref,p3.registermaster2epiref,[
    #     ('out_file','in_file')
    # ]),
    # (p3.resampleepiref2masterepiref,p3.registermaster2epiref,[
    #     ('out_file','reference')
    # ]),
    # (p3.skullstripped_atlas_mprage,p3.transformrawEPI2ATL,[
    #     ('noskull_at','in_file')
    # ]),
    # (p3.noskull_obla2e,p3.transformrawEPI2ATL,[
    #     ('noskull_obla2e_mat','tfm1')
    # ]),
    # (p3.registert12tcat,p3.transformrawEPI2ATL,[
    #     ('out_matrix','tfm2')
    # ]),
    # (p3.deobliquemasterepiref,p3.transformrawEPI2ATL,[
    #     ('ob_transform','tfm3')
    # ]),
    # (p3.registermaster2epiref,p3.transformrawEPI2ATL,[
    #     ('out_matrix','tfm4')
    # ]),
    # (p3.skullstripped_atlas_mprage,p3.transformtcat2mprageepi,[
    #     ('noskull_at','reference')
    # ]),
    # (p3.transformrawEPI2ATL,p3.transformtcat2mprageepi,[
    #     ('master_transform','in_matrix')
    # ]),
    # (p3.remakeoblique,p3.transformtcat2mprageepi,[
    #     ('out_file','in_file')
    # ]),
    # (p3.deobliquemasterepiref,p3.transformrawEPI2EPI1,[
    #     ('ob_transform','tfm1')
    # ]),
    # (p3.registermaster2epiref,p3.transformrawEPI2EPI1,[
    #     ('out_matrix','tfm2')
    # ]),
    # (p3.firstframeeachrun,p3.transformtcat2epi1,[
    #     ('refimg','reference')
    # ]),
    # (p3.transformrawEPI2EPI1,p3.transformtcat2epi1,[
    #     ('master_transform','in_matrix')
    # ]),
    # (p3.remakeoblique,p3.transformtcat2epi1,[
    #     ('out_file','in_file')
    # ]),
    # (p3.firstframeeachrun,p3.brikconvert,[
    #     ('refimg','in_file')
    # ]),
    # (p3.brikconvert,p3.prermoblique2,[
    #     ('out_file','in1')
    # ]),
    # (p3.prermoblique2,p3.remakeoblique2,[
    #     ('out','atrcopy')
    # ]),
    # (p3.transformtcat2epi1,p3.remakeoblique2,[
    #     ('out_file','in_file')
    # ]),

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
