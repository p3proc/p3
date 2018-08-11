""" Defines functions that return default settings
"""

def default_preproc_settings():
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
            'task':'rest'
            }
        }
    settings['func_reference_run'] = 0 # selects the epi run to take the reference image from (It is 0 indexed)
    settings['func_reference_frame'] = 4 # selects the epi reference frame to use (It is 0 indexed, and taken from the first run)
    settings['anat_reference'] = 0 # selects the T1 to align to if multiple T1 images in dataset (It is 0 indexed. T1s are order from lowest session,lowest run to highest session,highest run. Leave as 0 if only 1 T1)
    settings['atlas'] = 'MNI152.nii.gz' # sets the atlas align target
    settings['avganats'] = True # avgs all T1s in dataset if multiple T1s (Set this to False if you only have 1 T1 or you will probably get an error!)
    settings['field_map_correction'] = True # sets whether pipeline should run field map correction. You should have field maps in your dataset for this to work.
    settings['slice_time_correction'] = True # sets whether epi images should be slice time corrected
    settings['despiking'] = True # sets whether epi images should be despiked
    settings['run_recon_all'] = True # sets whether pipeline should run recon-all (if you decide not to you should place your own p3_freesurfer data under output p3_freesurfer_output, where each folder is {NAME} in sub-{NAME} in the bids dataset)
    settings['num_threads'] = 8 # sets the number of threads for ANTS registration
    settings['brain_radius'] = 50 # brain radius for FD calculations (in mm)
    settings['min_bpm'] = 18.582 # breathing rate for lower bound of filter
    settings['max_bpm'] = 25.7263 # breathing rate for upper bound of filter
    settings['FD_threshold'] = 0.2 # FD threshold for creating tmasks
    settings['FD_filtered_threshold'] = 0.1 # Filtered FD threshold for filtered tmask
    settings['workflows'] = [ # defines the workflows to import
            'p3_bidsselector',
            'p3_freesurfer',
            'p3_skullstrip',
            'p3_stcdespikemoco',
            'p3_fieldmapcorrection',
            'p3_alignanattoatlas',
            'p3_alignfunctoanat',
            'p3_alignfunctoatlas',
            'p3_create_fs_masks'
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
                ['output.warp_fmc','input.warp_fmc'],
                ['output.refimg','input.refimg']
            ]
        },
        {
            'source': 'p3_alignfunctoanat',
            'destination': 'p3_alignfunctoatlas',
            'links': [
                ['output.affine_func_2_anat','input.affine_func_2_anat']
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
        {
            'source': 'p3_freesurfer',
            'destination': 'p3_create_fs_masks',
            'links': [
                ['output.aparc_aseg','input.aparc_aseg'],
                ['output.orig','input.orig']
            ]
        },
        {
            'source': 'p3_alignanattoatlas',
            'destination': 'p3_create_fs_masks',
            'links': [
                ['output.affine_anat_2_atlas','input.affine_anat_2_atlas'],
                ['output.warp_anat_2_atlas','input.warp_anat_2_atlas'],
                ['output.anat_atlas','input.anat_atlas']
            ]
        },
        {
            'source': 'p3_alignfunctoatlas',
            'destination': 'p3_create_fs_masks',
            'links': [
                ['output.func_atlas','input.func_atlas'],
            ]
        },
        {
            'source': 'p3_bidsselector',
            'destination': 'p3_create_fs_masks',
            'links': [
                ['output.anat','input.T1'],
            ]
        }
    ]
    settings['sideload'] = []

    # return settings
    return settings
