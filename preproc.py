#!/usr/bin/env python3.6

import os
from nipype import Workflow,config,logging
import workflows.bidsselector.workflow as bidsselector
import workflows.reconall.workflow as reconall
import workflows.skullstrip.workflow as skullstrip
import workflows.timeshiftanddespike.workflow as timeshiftanddespike
import workflows.alignt1toatlas.workflow as alignt1toatlas
import workflows.alignboldtot1.workflow as alignboldtot1
import workflows.alignboldtoatlas.workflow as alignboldtoatlas

"""
    Settings
"""
settings = {}
settings['BASE_DIR'] = os.path.dirname(os.path.realpath(__file__))
settings['DATA_DIR'] = 'MSC_BIDS'
settings['subject'] = 'MSC01'
settings['ignoreframes'] = 4 # selects the epi reference frame to use (It is 0 indexed.)
settings['T1_reference'] = 0 # selects the T1 to align to if multiple T1 images in dataset (It is 0 indexed. T1s are order from lowest session,lowest run to highest session,highest run. Leave as 0 if only 1 T1)
settings['avgT1s'] = True # avgs all T1s in dataset if multiple T1s (Set this to False if you only have 1 T1 or you will probably get an error!)
settings['run_recon_all'] = False # sets whether pipeline should run recon-all (if you decide not to you should place your own freesurfer data under output freesurfer_output, where each folder is {NAME} in sub-{NAME} in the bids dataset)
config.set('logging','workflow_level','DEBUG')
config.set('logging','workflow_level','DEBUG')
config.set('execution','hash_method','content')
config.set('execution','stop_on_first_crash','true')
logging.update_logging(config)

"""
    Create Workflow
"""
# create sub-workflows
wf_bidsselector = bidsselector.bidsselectorworkflow('bidsselector',settings).workflow
wf_reconall = reconall.reconallworkflow('reconall',settings).workflow
wf_skullstrip = skullstrip.skullstripworkflow('skullstrip',settings).workflow
wf_timeshiftanddespike = timeshiftanddespike.timeshiftanddespikeworkflow('timeshiftanddespike',settings).workflow
wf_alignt1toatlas = alignt1toatlas.alignt1toatlasworkflow('alignt1toatlas',settings).workflow
wf_alignboldtot1 = alignboldtot1.alignboldtot1workflow('alignboldtot1',settings).workflow
wf_alignboldtoatlas = alignboldtoatlas.alignboldtoatlasworkflow('alignboldtoatlas',settings).workflow

# create a workflow
wf = Workflow(name='P3',base_dir=os.path.join(settings['BASE_DIR'],'tmp'))
wf.connect([ # connect nodes
    (wf_bidsselector,wf_reconall,[
        ('output.T1','input.T1')
    ]),
    (wf_bidsselector,wf_skullstrip,[
        ('output.T1','input.T1')
    ]),
    (wf_reconall,wf_skullstrip,[
        ('output.orig','input.orig')
    ]),
    (wf_reconall,wf_skullstrip,[
        ('output.brainmask','input.brainmask')
    ]),
    (wf_bidsselector,wf_timeshiftanddespike,[
        ('output.epi','input.epi')
    ]),
    (wf_skullstrip,wf_alignt1toatlas,[
        ('output.T1_skullstrip','input.T1_skullstrip')
    ]),
    (wf_timeshiftanddespike,wf_alignboldtot1,[
        ('output.refimg','input.refimg')
    ]),
    (wf_alignt1toatlas,wf_alignboldtot1,[
        ('output.T1_0','input.T1_0'),
    ]),
    (wf_alignt1toatlas,wf_alignboldtoatlas,[
        ('output.noskull_at','input.noskull_at'),
    ]),
    (wf_alignboldtot1,wf_alignboldtoatlas,[
        ('output.oblique_transform','input.oblique_transform'),
        ('output.t1_2_epi','input.t1_2_epi')
    ]),
    (wf_timeshiftanddespike,wf_alignboldtoatlas,[
        ('output.epi2epi1','input.epi2epi1'),
        ('output.tcat','input.tcat'),
    ])
])
wf.write_graph(graph2use='flat',simple_form=False)
wf.write_graph(graph2use='colored')
wf.run()
#wf.run(plugin='MultiProc')
