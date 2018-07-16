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

def output_BIDS_summary(bids_dir):
    """
        Get a summary of the BIDS dataset input
    """

    # call pybids
    layout = BIDSLayout(bids_dir)

    # print help message
    print(
        '\nThis summary internally uses pybids to show availiable keys to filter on.\n'
        'If you are using the default p3_bidsselector workflow, you can use the keys\n'
        'here to specify what images to process. For example, in the settings file:\n'
        '\n\tbids_query = {'
        '\n\t\t\'T1\':{'
        '\n\t\t\t\'type\':\'T1w\''
        '\n\t\t},'
        '\n\t\t\'epi\':{'
        '\n\t\t\t\'modality\':\'func\','
        '\n\t\t\t\'task\':\'rest\''
        '\n\t\t}'
        '\n\t}\n\n'
        'This will filter all T1 images by type \'T1w\', while epi images will use modality\n'
        '\'func\' and task \'rest\'.\n\n'
        'You can filter on specific subjects and runs by using []:\n'
        '\n\tbids_query = {'
        '\n\t\t\'T1\':{'
        '\n\t\t\t\'type\':\'T1w\','
        '\n\t\t\t\'subject\':\'MSC0[12]\''
        '\n\t\t},'
        '\n\t\t\'epi\':{'
        '\n\t\t\t\'modality\':\'func\','
        '\n\t\t\t\'task\':\'rest\','
        '\n\t\t\t\'run\':\'[13]\''
        '\n\t\t}'
        '\n\t}\n\n'
        'This will query will use subjects MSC01 and MSC02 and process epis with runs 1 and 3.\n\n'
        'Below are some available keys in the dataset to filter on:\n'
    )

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
    time.sleep(5)

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
        'T1':{
            'modality': 'anat',
            'type':'T1w'
            },
        'epi':{
            'modality':'func',
            'task':'rest'
            }
        }
    settings['epi_reference'] = 4 # selects the epi reference frame to use (It is 0 indexed, and taken from the first run)
    settings['brain_radius'] = 50 # set brain radius for FD calculation (in mm)
    settings['nonlinear_atlas'] = True # do nonlinear transform for atlas alignment using 3dQwarp
    settings['T1_reference'] = 0 # selects the T1 to align to if multiple T1 images in dataset (It is 0 indexed. T1s are order from lowest session,lowest run to highest session,highest run. Leave as 0 if only 1 T1)
    settings['atlas'] = 'MNI152_T1_2009c+tlrc' # sets the atlas align target (you can use `cat ${AFNI_DIR}/AFNI_atlas_spaces.niml` (where ${AFNI_DIR} is your afni directory) to show availiable atlas align targets)
    settings['avgT1s'] = False # avgs all T1s in dataset if multiple T1s (Set this to False if you only have 1 T1 or you will probably get an error!)
    settings['field_map_correction'] = True # sets whether pipeline should run field map correction. You should have field maps in your dataset for this to work.
    settings['slice_time_correction'] = True # sets whether epi images should be slice time corrected
    settings['despiking'] = True # sets whether epi images should be despiked
    settings['run_recon_all'] = False # sets whether pipeline should run recon-all (if you decide not to you should place your own p3_freesurfer data under output p3_freesurfer_output, where each folder is {NAME} in sub-{NAME} in the bids dataset)
    settings['workflows'] = [ # defines the workflows to import
            'p3_bidsselector',
            'p3_freesurfer',
            'p3_skullstrip',
            'p3_timeshiftanddespike',
            'p3_fieldmapcorrection',
            'p3_alignt1toatlas',
            'p3_alignboldtot1',
            'p3_alignboldtoatlas'
            'p3_create_fs_masks'
        ]
    settings['connections'] = [ # defines the input/output connections between workflows
        {
            'source': 'p3_bidsselector',
            'destination': 'p3_freesurfer',
            'links': [
                ['output.T1','input.T1'],
                ['output.subject','input.subject']
            ]
        },
        {
            'source': 'p3_bidsselector',
            'destination': 'p3_skullstrip',
            'links': [
                ['output.T1','input.T1']
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
            'destination': 'p3_timeshiftanddespike',
            'links': [
                ['output.epi','input.epi']
            ]
        },
        {
            'source': 'p3_skullstrip',
            'destination': 'p3_alignt1toatlas',
            'links': [
                ['output.T1_skullstrip','input.T1_skullstrip']
            ]
        },
        {
            'source': 'p3_bidsselector',
            'destination': 'p3_fieldmapcorrection',
            'links': [
                ['output.epi','input.epi']
            ]
        },
        {
            'source': 'p3_timeshiftanddespike',
            'destination': 'p3_fieldmapcorrection',
            'links': [
                ['output.epi_aligned','input.epi_aligned'],
                ['output.refimg','input.refimg']
            ]
        },
        {
            'source': 'p3_fieldmapcorrection',
            'destination': 'p3_alignboldtot1',
            'links': [
                ['output.refimg','input.refimg']
            ]
        },
        {
            'source': 'p3_alignt1toatlas',
            'destination': 'p3_alignboldtot1',
            'links': [
                ['output.T1_0','input.T1_0']
            ]
        },
        {
            'source': 'p3_alignt1toatlas',
            'destination': 'p3_alignboldtoatlas',
            'links': [
                ['output.t1_2_atlas_transform','input.t1_2_atlas_transform'],
                ['output.noskull_at','input.noskull_at'],
                ['output.nonlin_warp','input.nonlin_warp']
            ]
        },
        {
            'source': 'p3_alignboldtot1',
            'destination': 'p3_alignboldtoatlas',
            'links': [
                ['output.oblique_transform','input.oblique_transform'],
                ['output.t1_2_epi','input.t1_2_epi']
            ]
        },
        {
            'source': 'p3_timeshiftanddespike',
            'destination': 'p3_alignboldtoatlas',
            'links': [
                ['output.tcat','input.tcat'],
                ['output.epi2epi1','input.epi2epi1']
            ]
        },
        {
            'source': 'p3_fieldmapcorrection',
            'destination': 'p3_alignboldtoatlas',
            'links': [
                ['output.fmc','input.fmc']
            ]
        },
        {
            'source': 'p3_freesurfer',
            'definition': 'p3_create_fs_masks'
            'links': [
                ['output.aparc_aseg','input.aparc_aseg']
            ]
        },
        {
            'source': 'p3_alignt1toatlas',
            'definition': 'p3_create_fs_masks'
            'links': [
                ['output.nonlin_warp','input.nonlin_warp'],
                ['output.t1_2_atlas_transform','input.t1_2_atlas_transform'],
                ['output.noskull_at','input.noskull_at']
            ]
        },
        {
            'source': 'p3_alignboldtoatlas',
            'definition': 'p3_create_fs_masks'
            'links': [
                ['output.epi_at','input.epi_at'],
            ]
        },
        {
            'source': 'p3_skullstrip',
            'definition': 'p3_create_fs_masks'
            'links': [
                ['output.fs2mpr','input.fs2mpr']
            ]
        }
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
