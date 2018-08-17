.. _Settings:

Settings
--------
Settings in p3, are defined in JSON format and can be loaded in through the **-s** or
**--settings** command line flags. This document describes the settings available to
default workflows of p3.

bids_query
^^^^^^^^^^
Sets the bids query for the bidsselector workflow. The input to this settings key should
be a dictionary containing the *anat* and *func* keys. See pybids_ docs for more
information.

.. code:: bash

    # This sets the anatomy images to be of modality 'anat' and type 'T1w'
    # and the functional images to be modality 'func' and type 'rest'
    {
    'anat':{
        'modality': 'anat',
        'type':'T1w',
        },
    'func':{
        'modality':'func',
        'task':'rest'
        }
    }

func_reference_run
^^^^^^^^^^^^^^^^^^
Selects the epi run to take the reference image from. It is 0 indexed so the first run loaded
in to the func key would be 0.

func_reference_frame
^^^^^^^^^^^^^^^^^^^^
Selects the epi reference frame to use. It is 0 indexed and taken from the whatever run was set to the
**func_reference_run**.

anat_reference
^^^^^^^^^^^^^^
Selects the anat to align to if multiple anat images in dataset. It is 0 indexed. Anatomy imagess are
ordered from lowest session, lowest run to highest session, highest run. Leave as 0 if only 1 anat.

atlas
^^^^^
Sets the atlas align target. You can specify a path to an atlas here, or use one of p3's built in
templates. Currently the only availiable template in p3 is *MNI152.nii.gz*

avganats
^^^^^^^^
True or False. Averages all anats in the dataset if multiple T1s. Set this to False if you only have
1 anatomy image or you will probably get an error!

field_map_correction
^^^^^^^^^^^^^^^^^^^^
True or False. Sets whether the pipeline should run field map correction. You should have field maps in your
dataset for this to work. **p3 currently only supports gradient echo field maps.**

slice_time_correction
^^^^^^^^^^^^^^^^^^^^^
True or False. Sets whether the functional images should be slice time corrected.

despiking
^^^^^^^^^
True of False. Sets whether epi images should be despiked.

run_recon_all
^^^^^^^^^^^^^
True or False. Sets whether pipeline should run recon-all (if you decide not to you should place your own p3_freesurfer data under output p3_freesurfer_output, where each folder is {NAME} in sub-{NAME} in the bids dataset)

num_threads
^^^^^^^^^^^
Sets the number of threads for all ANTs programs.

brain_radius
^^^^^^^^^^^^
Sets the brain radius for FD calculations (in mm).

min_bpm
^^^^^^^
Sets the breathing rate for lower bound of the respiratory filter.

max_bpm
^^^^^^^
Sets the breathing rate for upper bound of the respiratory filter.

FD_threshold
^^^^^^^^^^^^
FD threshold for creating tmask outputs.

FD_filtered_threshold
^^^^^^^^^^^^^^^^^^^^^
Filtered FD threshold for creating filtered tmask outputs.

workflows
^^^^^^^^^
Defines the workflows to import.

.. code:: bash

    "workflows": [
        "p3_bidsselector",
        "p3_freesurfer",
        "p3_skullstrip",
        "p3_stcdespikemoco",
        "p3_fieldmapcorrection",
        "p3_alignanattoatlas",
        "p3_alignfunctoanat",
        "p3_alignfunctoatlas",
        "p3_create_fs_masks"
    ]

See :ref:`Creating New Workflows` for more details.

connections
^^^^^^^^^^^
Defines the connections between workflows.

.. code:: bash

    "connections": [
        {
            'source': 'p3_bidsselector', # the source workflow
            'destination': 'p3_freesurfer', # the destination workflow
            'links': [
                [ # this sets the anat of p3_bidsselector to T1 of p3_freesurfer
                    'output.anat',
                    'input.T1'
                ],
                [ # this sets the subject of p3_bidsselector to subject of p3_freesurfer
                    'output.subject',
                    'input.subject'
                ]
            ]
        },
        {
            'source': 'p3_bidsselector', # the source workflow
            'destination': 'p3_skullstrip', # the destination workflow
            'links': [
                [ # this sets the anat of p3_bidsselector to T1 of p3_skullstrip
                    'output.anat',
                    'input.T1'
                ]
            ]
        },
        ...
    ]

See :ref:`Creating New Workflows` for more details.

sideload
^^^^^^^^
A list of inputs to sideload a node.

.. code:: bash

    "sideload": [
        {
            "workflow": "myworkflow1",
            "node": "node1",
            "input": ["field1", "value1"] # a single string sideload
        },
        {
            "workflow": "myworkflow2",
            "node": "node2",
            "input": ["field2", ["value2_1","value2_2","value2_3"]] # an array sideload
        }
    ]

See :ref:`Sideloading` for more details.

.. include:: ../links.rst
