#!/usr/bin/env python3.6
"""
    An extensible pipeline in python
"""
import os
import sys
from glob import glob
from nipype import Workflow,config,logging
import importlib
import argparse
from ppp.base import generate_subworkflows

# add p3 base files to path
sys.path.append('p3')

# get default workflows path
sys.path.append('workflows')

# get version
__version__ = open(os.path.join(os.path.dirname(os.path.realpath(__file__)),'version')).read()

def create_and_run_p3_workflow(imported_workflows,settings):
    """
        Create main workflow
    """

    # define subworkflows from imported workflows
    subworkflows = generate_subworkflows(imported_workflows,settings)

    # create a workflow
    p3 = Workflow(name='p3_pipeline',base_dir=settings['tmp_dir'])
    p3.connect([ # connect nodes
        (subworkflows['bidsselector'],subworkflows['freesurfer'],[
            ('output.T1','input.T1'),
            ('output.subject','input.subject')
        ]),
        (subworkflows['bidsselector'],subworkflows['skullstrip'],[
            ('output.T1','input.T1'),
        ]),
        (subworkflows['freesurfer'],subworkflows['skullstrip'],[
            ('output.orig','input.orig'),
            ('output.brainmask','input.brainmask')
        ]),
        (subworkflows['bidsselector'],subworkflows['timeshiftanddespike'],[
            ('output.epi','input.epi')
        ]),
        (subworkflows['skullstrip'],subworkflows['alignt1toatlas'],[
            ('output.T1_skullstrip','input.T1_skullstrip')
        ]),
        (subworkflows['timeshiftanddespike'],subworkflows['alignboldtot1'],[
            ('output.refimg','input.refimg')
        ]),
        (subworkflows['alignt1toatlas'],subworkflows['alignboldtot1'],[
            ('output.T1_0','input.T1_0'),
        ]),
        (subworkflows['alignt1toatlas'],subworkflows['alignboldtoatlas'],[
            ('output.noskull_at','input.noskull_at'),
            ('output.noskull_Qwarp','input.noskull_Qwarp'),
        ]),
        (subworkflows['alignboldtot1'],subworkflows['alignboldtoatlas'],[
            ('output.oblique_transform','input.oblique_transform'),
            ('output.t1_2_epi','input.t1_2_epi')
        ]),
        (subworkflows['timeshiftanddespike'],subworkflows['alignboldtoatlas'],[
            ('output.epi2epi1','input.epi2epi1'),
            ('output.tcat','input.tcat'),
        ])
    ])
    p3.write_graph(graph2use='flat',simple_form=False)
    p3.write_graph(graph2use='colored')
    p3.run()
    #p3.run(plugin='MultiProc')

def main():
    """
        Settings
    """

    # print really cool graphic
    print('\n'
    '                  ad888888b,\n'
    '                 d8\"     \"88\n'
    '                         a8P\n'
    '    8b,dPPYba,        aad8\"\n'
    '    88P\'    \"8a       \"\"Y8,\n'
    '    88       d8          \"8b\n'
    '    88b,   ,a8\"  Y8,     a88\n'
    '    88`YbbdP\"\'    \"Y888888P\'\n'
    '    88\n'
    '    88\n')

    # get the current directory
    cwd = os.getcwd()

    # specify command line arguments
    parser = argparse.ArgumentParser(description='\033[1mp3\033[0;0m processing pipeline')
    parser.add_argument('bids_dir', help='The directory with the input dataset '
                        'formatted according to the BIDS standard.', nargs='?')
    parser.add_argument('output_dir', help='The directory where the output files '
                        'should be stored. If you are running group level analysis '
                        'this folder should be prepopulated with the results of the '
                        'participant level analysis.', nargs='?')
    parser.add_argument('analysis_level', help='Level of the analysis that will be performed. '
                        'Multiple participant level analyses can be run independently '
                        '(in parallel) using the same output_dir. (Note: group flag '
                        'is currently disabled since there are not any group level '
                        'functionalities in this pipeline currently. This is set to '
                        '\'participant\' by default and can be omitted.)',
                        choices=['participant', 'group'], nargs='?', default='participant')
    parser.add_argument('--participant_label', help='The label(s) of the participant(s) that should be analyzed.'
                        'The label corresponds to sub-<participant_label> from the BIDS spec '
                        '(so it does not include "sub-"). If this parameter is not '
                        'provided all subjects should be analyzed. Multiple '
                        'participants can be specified with a space separated list.',
                        nargs="+")
    parser.add_argument('--skip_bids_validator', help='Whether or not to perform BIDS dataset validation',
                        action='store_true')
    parser.add_argument('-v', '--version', action='version',
                        version='\033[1mp3\033[0;0m {}'.format(__version__))
    parser.add_argument('-s', '--settings', help='A JSON settings file that specifies how the pipeline '
                        'should be configured. If no settings file is provided, the pipeline will use '
                        'internally specified defaults. See docs for more help details.')
    parser.add_argument('-g', '--generate_settings', help='Generates a default settings file in the '
                        'current working directory for use/modification. This option will ignore all other '
                        'arguments.',
                        action='store_true')

    # parse command line arguments
    args = parser.parse_args()

    # check if generating settings
    if args.generate_settings:
        print('settings.json was generated in the current directory.')
        sys.exit()

    # check if bids_dir/output_dir is defined
    if not args.bids_dir or not args.output_dir:
        parser.print_usage()
        print('p3: error: positional arguments bids_dir/output_dir are required.')
        sys.exit(1)

    # only for a subset of subjects
    if args.participant_label:
        subjects_to_analyze = args.participant_label
    # for all subjects
    else:
        subject_dirs = glob(os.path.join(args.bids_dir, "sub-*"))
        subjects_to_analyze = [subject_dir.split("-")[-1] for subject_dir in subject_dirs]

    # running participant level
    if args.analysis_level == "participant":
        # define default settings
        settings = {}
        settings['epi_reference'] = 4 # selects the epi reference frame to use (It is 0 indexed.)
        settings['T1_reference'] = 0 # selects the T1 to align to if multiple T1 images in dataset (It is 0 indexed. T1s are order from lowest session,lowest run to highest session,highest run. Leave as 0 if only 1 T1)
        settings['brain_radius'] = 50 # set brain radius for FD calculation (in mm)
        settings['nonlinear_atlas'] = True # do nonlinear transform for atlas alignment using 3dQwarp
        settings['atlas'] = 'TT_N27+tlrc' # sets the atlas align target (you can use `cat ${AFNI_DIR}/AFNI_atlas_spaces.niml` (where ${AFNI_DIR} is your afni directory) to show availiable atlas align targets)
        settings['avgT1s'] = True # avgs all T1s in dataset if multiple T1s (Set this to False if you only have 1 T1 or you will probably get an error!)
        settings['field_map_correction'] = False # sets whether pipeline should run field map correction. You should have field maps in your dataset for this to work.
        settings['slice_time_correction'] = True # sets whether epi images should be slice time corrected
        settings['despiking'] = True # sets whether epi images should be despiked
        settings['run_recon_all'] = False # sets whether pipeline should run recon-all (if you decide not to you should place your own freesurfer data under output freesurfer_output, where each folder is {NAME} in sub-{NAME} in the bids dataset)
        settings['workflows'] = [ # defines the workflows to import
                'bidsselector',
                'freesurfer',
                'skullstrip',
                'timeshiftanddespike',
                'alignt1toatlas',
                'alignboldtot1',
                'alignboldtoatlas'
            ]
        settings['connections'] = [ # defines the input/output connections between workflows
        ]
        config.set('logging','workflow_level','DEBUG')
        config.set('logging','workflow_level','DEBUG')
        config.set('execution','hash_method','content')
        config.set('execution','stop_on_first_crash','true')
        logging.update_logging(config)

        # import workflows
        imported_workflows = {}
        for module in settings['workflows']:
            imported_workflows[module] = importlib.import_module('{}.workflow'.format(module))

        # add command line params to settings
        settings['subject'] = subjects_to_analyze
        settings['bids_dir'] = os.path.abspath(args.bids_dir)
        settings['output_dir'] = os.path.abspath(args.output_dir)
        settings['tmp_dir'] = os.path.join(settings['output_dir'],'tmp')

        # make directories if not exist
        os.makedirs(settings['output_dir'],exist_ok=True)
        os.makedirs(settings['tmp_dir'],exist_ok=True)

        # construct and execute workflow
        create_and_run_p3_workflow(imported_workflows,settings)

    # running group level
    elif args.analysis_level == "group":
        print('This option is disabled since there is no group level analysis availiable.')

if __name__ == '__main__':
    # execute main function
    main()
