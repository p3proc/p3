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
settings['ignoreframes'] = 4
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
wf.connect([ # connect nodes (see nodedefs.py for further details on each node)
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
    (wf_bidsselector,wf_alignt1toatlas,[
        ('output.T1','input.T1')
    ]),
    (wf_timeshiftanddespike,wf_alignt1toatlas,[
        ('output.refimg','input.refimg')
    ]),
    (wf_alignt1toatlas,wf_alignboldtoatlas,[
        ('output.noskull_at','input.noskull_at')
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
wf.run()
#wf.run(plugin='MultiProc')
wf.write_graph()
