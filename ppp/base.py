"""Define Nodes for nipype workflow

TODO

"""
import os
import inspect
import time
from nipype import Workflow,config,logging
from nipype import Node
from nipype.interfaces.utility import IdentityInterface
from nipype.interfaces.io import DataSink
from bids.grabbids import BIDSLayout

def get_basename(filename):
    import os # import os here for function interfaces

    # strip filename extension
    name,ext = os.path.splitext(os.path.basename(filename))
    while(ext != ''):
        name,ext = os.path.splitext(os.path.basename(name))

    # return the basename
    return name

def output_BIDS_summary(bids_dir):
    """
        Get a summary of the BIDS dataset input
    """

    # call pybids
    layout = BIDSLayout(bids_dir)
    print('Below are some available keys in the dataset to filter on:\n')

    # show availiable keys
    keys = [
        'subject',
        'session',
        'run',
        'type',
        'task',
        'modality'
        ]
    for k in keys:
        query = layout.get(target=k,return_type='id')
        print('Availiable {}:'.format(k))
        for q in query:
            print(q,end=' ')
        print('\n')

def check_query(bids_query,bids_dir):
    """
        Check BIDS selection query
    """

    # get bids layout
    layout = BIDSLayout(bids_dir)

    # parse bids query
    output = {}
    for key in bids_query:
        # return the query
        output[key] = layout.get(**bids_query[key])
        # print the output of the query
        print('{}:'.format(key))
        for o in output[key]:
            print(o.filename)

    # wait 5 seconds
    print('Files listed are to be processed. Quit now if they are not the right ones...')
    #time.sleep(2)

def create_and_run_p3_workflow(imported_workflows,settings):
    """
        Create main workflow
    """

    # Set nipype config settings TODO expose these as debug settings
    config.set('logging','workflow_level','DEBUG')
    config.set('logging','workflow_level','DEBUG')
    config.set('execution','hash_method','content')
    config.set('execution','stop_on_first_crash','true')
    logging.update_logging(config)

    # define subworkflows from imported workflows
    subworkflows = generate_subworkflows(imported_workflows,settings)

    # create a workflow
    p3 = Workflow(name='p3_pipeline',base_dir=settings['tmp_dir'])

    # get connections
    connections = generate_connections(subworkflows,settings)

    # connect nodes
    p3.connect(connections)

    # Create graph images
    p3.write_graph(graph2use='flat',simple_form=False)
    p3.write_graph(graph2use='colored')

    # check files being processed
    # TODO: Not really sure if I want to keep this... is p3_bidsselector specific
    check_query(settings['bids_query'],settings['bids_dir'])

    # Run pipeline (check multiproc setting)
    if not settings['disable_run']:
        if settings['multiproc']:
            p3.run(plugin='MultiProc')
        else:
            p3.run()

def generate_subworkflows(imported_workflows,settings):
    """
        TODO: document this function
    """

    # create sub-workflows
    subworkflows = {}
    # loop over all imported workflows
    for name,wf in imported_workflows.items():
        # find the class whos base is the workflowgenerator
        for obj in dir(wf):
            if inspect.isclass(getattr(wf,obj)): # check if object is class
                # the object is a workflowgenerator object
                if getattr(wf,obj).__bases__[0] == workflowgenerator:
                    # create and assign the workflow to the dictionary
                    subworkflows[name] = getattr(wf,obj)(name,settings)

    # return subworkflows
    return subworkflows

def generate_connections(subworkflows,settings):
    """
        TODO: document this function
    """

    # define initial connection list
    connections = []

    # go through connections in settings and build connections list
    for connection_entry in settings['connections']:
        # append to connections list
        connections.append(( # define tuple
            subworkflows[connection_entry['source']],
            subworkflows[connection_entry['destination']],
            [tuple(link) for link in connection_entry['links']] # convert each entry in links list to tuple
        ))

    # return connection list
    return connections

def default_settings():
    """
        TODO: document this function
    """

    # define default settings
    settings = {}
    settings['bids_query'] = { # bids query
        'anat':{
            'modality': 'anat',
            'type':'T1w',
            },
        'func':{
            'modality':'func',
            'task':'rest',
            'session': 'func01'
            }
        }
    settings['epi_reference'] = 4 # selects the epi reference frame to use (It is 0 indexed, and taken from the first run)
    settings['brain_radius'] = 50 # set brain radius for FD calculation (in mm)
    settings['num_threads'] = 4 # sets the number of threads for ANTS registration
    settings['anat_reference'] = 0 # selects the T1 to align to if multiple T1 images in dataset (It is 0 indexed. T1s are order from lowest session,lowest run to highest session,highest run. Leave as 0 if only 1 T1)
    settings['atlas'] = '/home/vana/Projects/p3/templates/MNI152.nii.gz' # sets the atlas align target (you can use `cat ${AFNI_DIR}/AFNI_atlas_spaces.niml` (where ${AFNI_DIR} is your afni directory) to show availiable atlas align targets)
    settings['avganats'] = False # avgs all T1s in dataset if multiple T1s (Set this to False if you only have 1 T1 or you will probably get an error!)
    settings['field_map_correction'] = True # sets whether pipeline should run field map correction. You should have field maps in your dataset for this to work.
    settings['slice_time_correction'] = True # sets whether epi images should be slice time corrected
    settings['despiking'] = True # sets whether epi images should be despiked
    settings['run_recon_all'] = False # sets whether pipeline should run recon-all (if you decide not to you should place your own p3_freesurfer data under output p3_freesurfer_output, where each folder is {NAME} in sub-{NAME} in the bids dataset)
    settings['workflows'] = [ # defines the workflows to import
            'p3_bidsselector',
            'p3_freesurfer',
            'p3_skullstrip',
            'p3_stcdespikemoco',
            'p3_fieldmapcorrection',
            'p3_alignanattoatlas',
            'p3_alignfunctoanat',
            'p3_alignfunctoatlas',
            #'p3_create_fs_masks'
        ]
    settings['connections'] = [ # defines the input/output connections between workflows
        {
            'source': 'p3_bidsselector',
            'destination': 'p3_freesurfer',
            'links': [
                ['output.anat','input.T1'],
                ['output.subject','input.subject']
            ]
        },
        {
            'source': 'p3_bidsselector',
            'destination': 'p3_skullstrip',
            'links': [
                ['output.anat','input.T1']
            ]
        },
        {
            'source': 'p3_freesurfer',
            'destination': 'p3_skullstrip',
            'links': [
                ['output.orig','input.orig'],
                ['output.brainmask','input.brainmask']
            ]
        },
        {
            'source': 'p3_bidsselector',
            'destination': 'p3_stcdespikemoco',
            'links': [
                ['output.func','input.func']
            ]
        },
        {
            'source': 'p3_skullstrip',
            'destination': 'p3_alignanattoatlas',
            'links': [
                ['output.T1_skullstrip','input.T1_skullstrip']
            ]
        },
        {
            'source': 'p3_bidsselector',
            'destination': 'p3_fieldmapcorrection',
            'links': [
                ['output.func','input.func']
            ]
        },
        {
            'source': 'p3_stcdespikemoco',
            'destination': 'p3_fieldmapcorrection',
            'links': [
                ['output.func_aligned','input.func_aligned'],
                ['output.refimg','input.refimg']
            ]
        },
        {
            'source': 'p3_fieldmapcorrection',
            'destination': 'p3_alignfunctoanat',
            'links': [
                ['output.refimg','input.refimg']
            ]
        },
        {
            'source': 'p3_skullstrip',
            'destination': 'p3_alignfunctoanat',
            'links': [
                ['output.T1_skullstrip','input.T1_skullstrip']
            ]
        },
        {
            'source': 'p3_bidsselector',
            'destination': 'p3_alignfunctoatlas',
            'links': [
                ['output.func','input.func'],
            ]
        },
        {
            'source': 'p3_stcdespikemoco',
            'destination': 'p3_alignfunctoatlas',
            'links': [
                ['output.func_stc_despike','input.func_stc_despike'],
                ['output.warp_func_2_refimg','input.warp_func_2_refimg']
            ]
        },
        {
            'source': 'p3_fieldmapcorrection',
            'destination': 'p3_alignfunctoatlas',
            'links': [
                ['output.affine_fmc','input.affine_fmc'],
                ['output.warp_fmc','input.warp_fmc'],
                ['output.refimg','input.refimg']
            ]
        },
        {
            'source': 'p3_alignfunctoanat',
            'destination': 'p3_alignfunctoatlas',
            'links': [
                ['output.affine_func_2_anat','input.affine_func_2_anat'],
                ['output.warp_func_2_anat','input.warp_func_2_anat']
            ]
        },
        {
            'source': 'p3_alignanattoatlas',
            'destination': 'p3_alignfunctoatlas',
            'links': [
                ['output.affine_anat_2_atlas','input.affine_anat_2_atlas'],
                ['output.warp_anat_2_atlas','input.warp_anat_2_atlas']
            ]
        },
        # {
        #     'source': 'p3_freesurfer',
        #     'destination': 'p3_create_fs_masks',
        #     'links': [
        #         ['output.aparc_aseg','input.aparc_aseg']
        #     ]
        # },
        # {
        #     'source': 'p3_alignanattoatlas',
        #     'destination': 'p3_create_fs_masks',
        #     'links': [
        #         ['output.affine_anat_2_atlas','input.affine_anat_2_atlas'],
        #         ['output.warp_anat_2_atlas','input.warp_anat_2_atlas'],
        #         ['output.anat_atlas','input.anat_atlas']
        #     ]
        # },
        # {
        #     'source': 'p3_alignfunctoatlas',
        #     'destination': 'p3_create_fs_masks',
        #     'links': [
        #         ['output.func_atlas','input.func_atlas'],
        #     ]
        # },
        # {
        #     'source': 'p3_skullstrip',
        #     'destination': 'p3_create_fs_masks',
        #     'links': [
        #         ['output.allineate_freesurfer2anat','input.allineate_freesurfer2anat']
        #     ]
        # }
    ]




    # return settings
    return settings

class basenodedefs:
    """Base class for initializing nodes in workflow

        TODO

    """
    def __init__(self,settings):
        # Define datasink node
        self.datasink = Node(
            DataSink(
                base_directory=os.path.join(settings['output_dir']),
                substitutions=[
                    ('_subject_','sub-')
                ]
            ),
            name='datasink'
        )

    def set_input(self,input_list):
        # assign input list to inputnode fields
        self.inputnode = Node(
            IdentityInterface(
                fields=input_list
            ),
            name='input'
        )

    def set_output(self,output_list):
        # assign output list to outputnode fields
        self.outputnode = Node(
            IdentityInterface(
                fields=output_list
            ),
            name='output'
        )

    def set_subs(self,sub_list):
        # append substitution list to substitutions
        self.datasink.inputs.substitutions.extend(sub_list)

    def set_resubs(self,sub_list):
        # add regular expression substitution to list
        self.datasink.inputs.regexp_substitutions = sub_list

class workflowgenerator:
    """ Base class defining a workflow

        TODO

    """
    def __new__(cls,name,settings):
        # define workflow name and path
        cls.workflow = Workflow(name=name,base_dir=settings['tmp_dir'])
