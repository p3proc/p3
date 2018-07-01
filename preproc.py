#!/usr/bin/env python3.6
"""
    An extensible pipeline in nipype
"""
import os
import sys
from nipype import Workflow,config,logging
import importlib
import argparse
from p3.base import workflowgenerator

# add p3 base files to path
sys.path.append('p3')

# get default workflows path
sys.path.append('workflows')

def create_and_run_p3_workflow(imported_workflows,settings):
    """
        Create main workflow
    """

    # create sub-workflows
    subworkflows = {}
    # loop over all imported workflows
    for name,wf in imported_workflows.items():
        # find the class whos base is the workflowgenerator
        for obj in dir(wf):
            try: # pass if no __bases__ attribute
                # the object is a workflowgenerator object
                if getattr(wf,obj).__bases__[0] == workflowgenerator:
                    # create and assign the workflow to the dictionary
                    subworkflows[name] = getattr(wf,obj)(name,settings)
            except AttributeError:
                pass # skip over non-workflow object

    # create a workflow
    p3 = Workflow(name='P3',base_dir=os.path.join(settings['BASE_DIR'],'tmp'))
    p3.connect([ # connect nodes
        (subworkflows['bidsselector'],subworkflows['freesurfer'],[
            ('output.T1','input.T1')
        ]),
        (subworkflows['bidsselector'],subworkflows['skullstrip'],[
            ('output.T1','input.T1')
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
    #p3.run()
    #p3.run(plugin='MultiProc')

def main():
    """
        Settings
    """

    # define default settings
    settings = {}
    settings['BASE_DIR'] = os.path.dirname(os.path.realpath(__file__))
    settings['DATA_DIR'] = 'MSC_BIDS'
    settings['subject'] = 'MSC01'
    settings['ignoreframes'] = 4 # selects the epi reference frame to use (It is 0 indexed.)
    settings['T1_reference'] = 0 # selects the T1 to align to if multiple T1 images in dataset (It is 0 indexed. T1s are order from lowest session,lowest run to highest session,highest run. Leave as 0 if only 1 T1)
    settings['avgT1s'] = True # avgs all T1s in dataset if multiple T1s (Set this to False if you only have 1 T1 or you will probably get an error!)
    settings['run_recon_all'] = False # sets whether pipeline should run recon-all (if you decide not to you should place your own freesurfer data under output freesurfer_output, where each folder is {NAME} in sub-{NAME} in the bids dataset)
    settings['workflows'] = ['bidsselector','freesurfer','skullstrip','timeshiftanddespike','alignt1toatlas','alignboldtot1','alignboldtoatlas'] # defines the workflows to import
    settings['connections'] =
    config.set('logging','workflow_level','DEBUG')
    config.set('logging','workflow_level','DEBUG')
    config.set('execution','hash_method','content')
    config.set('execution','stop_on_first_crash','true')
    logging.update_logging(config)

    # import workflows
    imported_workflows = {}
    for module in settings['workflows']:
        imported_workflows[module] = importlib.import_module('{}.workflow'.format(module))

    # construct and execute workflow
    create_and_run_p3_workflow(imported_workflows,settings)

if __name__ == '__main__':
    # execute main function
    main()
