#!/usr/bin/env python3

import os
import argparse
from nipype import Workflow,config,logging
from skullstripnodes import * # import all defined nodes

"""
    Settings
"""
def run_workflow(settings):
    settings['input_dir'] = '/input'
    settings['output_dir'] = '/output'
    config.set('logging','workflow_level','DEBUG')
    config.set('logging','workflow_level','DEBUG')
    config.set('execution','hash_method','content')
    config.set('execution','stop_on_first_crash','true')
    logging.update_logging(config)

    # Create tmp dir
    os.makedirs(os.path.join(settings['output_dir'],'tmp'),exist_ok=True)

    # initialize nodes from nodedefs
    ss = definednodes(settings)

    """
        Create Workflow
    """

    # create a workflow
    wf = Workflow(name='skullstrip',base_dir=os.path.join(settings['output_dir'],'tmp'))
    wf.connect([ # connect nodes (see nodedefs.py for further details on each node)
        ### Skullstrip
        # AFNI skull stripped images are missing edge of cortical ribbon often
        # FSL has more of the ribbon often but can have weird neck stuff too
        # Freesurfer rarely clips and is the most lenient of the skullstrips
        (ss.fileselection,ss.afni_skullstrip,[
            ('T1','in_file')
        ]),
        (ss.fileselection,ss.fsl_skullstrip,[
            ('T1','in_file')
        ]),

        ### Recon-all
        (ss.fileselection,ss.reconall,[
            ('T1','T1_files')
        ]),

        ### REGISTER THE MPRAGE TO THE ATLAS
        # Convert orig and brainmask
        (ss.reconall,ss.orig_convert,[
            ('orig','in_file')
        ]),
        (ss.reconall,ss.brainmask_convert,[
            ('brainmask','in_file')
        ]),

        # Create transformation of FSorig to T1
        (ss.orig_convert,ss.allineate_orig,[
            ('out_file','in_file')
        ]),
        (ss.fileselection,ss.allineate_orig,[
            ('T1','reference')
        ]),
        (ss.afni_skullstrip,ss.refit_setup,[
            ('out_file','noskull_T1')
        ]),
        (ss.refit_setup,ss.refit[0],[
            ('refit_input','atrcopy')
        ]),
        (ss.allineate_orig,ss.refit[0],[
            ('out_file','in_file')
        ]),

        # create atlas-aligned skull stripped brainmask
        (ss.brainmask_convert,ss.allineate_bm,[
            ('out_file','in_file')
        ]),
        (ss.fileselection,ss.allineate_bm,[
            ('T1','reference')
        ]),
        (ss.allineate_orig,ss.allineate_bm,[
            ('out_matrix','in_matrix')
        ]),
        (ss.refit_setup,ss.refit[1],[
            ('refit_input','atrcopy')
        ]),
        (ss.allineate_bm,ss.refit[1],[
            ('out_file','in_file')
        ]),

        # intensities are differently scaled in FS image, replace with native intensities for uniformity
        (ss.fileselection,ss.uniform,[
            ('T1','in_file_a')
        ]),
        (ss.refit[1],ss.uniform,[
            ('out_file','in_file_b')
        ]),

        # Use OR of AFNI, FSL, and FS skullstrips within a 3-shell expanded AFNI mask as final
        (ss.afni_skullstrip,ss.maskop1,[
            ('out_file','in_file_a')
        ]),
        (ss.maskop1,ss.maskop2[0],[
            ('out_file','in_file_a')
        ]),
        (ss.maskop2[0],ss.maskop2[1],[
            ('out_file','in_file_a')
        ]),
        (ss.maskop2[1],ss.maskop2[2],[
            ('out_file','in_file_a')
        ]),
        (ss.maskop2[2],ss.maskop3,[
            ('out_file','in_file_a')
        ]),
        (ss.fsl_skullstrip,ss.maskop3,[
            ('out_file','in_file_b')
        ]),
        (ss.afni_skullstrip,ss.maskop3,[
            ('out_file','in_file_c')
        ]),
        (ss.fsl_skullstrip,ss.maskop5,[
            ('out_file','in_file_a')
        ]),
        (ss.afni_skullstrip,ss.maskop5,[
            ('out_file','in_file_b')
        ]),
        (ss.uniform,ss.maskop5,[
            ('out_file','in_file_c')
        ]),
        (ss.maskop2[2],ss.maskop6,[ # final noskull mprage
            ('out_file','in_file_a')
        ]),
        (ss.maskop5,ss.maskop6,[
            ('out_file','in_file_b')
        ]),
        (ss.fileselection,ss.maskop6,[
            ('T1','in_file_c')
        ]),

        # Output
        (ss.maskop6,ss.output[0],[
            ('out_file','output')
        ]),
    ])
    if settings['multiproc']:
        wf.run(plugin='MultiProc')
    else:
        wf.run()


if __name__ == "__main__":
    # parse arguments to command
    parser = argparse.ArgumentParser(description='This script does skull-stripping using Jonathan Power\'s combined afni,fsl,and freesurfer skullstrip method.')
    parser.add_argument('--input_t1', required=True, help='A .nii.gz file to skullstrip.')
    parser.add_argument('--subject_id', required=True, help='Subject Name/ID (Should match freesurfer subject name in subjects directory)')
    parser.add_argument('--fs_license',help='A freesurfer license file (Required for freesurfer to work)')
    parser.add_argument('--multiproc',action='store_true',help='Flag to specify run workflow with multiprocessing')

    # parse arguments into dict
    settings = vars(parser.parse_args())

    # run workflow
    run_workflow(settings)
