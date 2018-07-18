Usage
=====

Summary
-------
.. code-block:: none

    usage: p3.py [-h]
                 [--participant_label PARTICIPANT_LABEL [PARTICIPANT_LABEL ...]]
                 [--skip_bids_validator] [-v] [-s SETTINGS] [-g] [-m]
                 [--disable_run] [-w WORKFLOWS [WORKFLOWS ...]] [--summary]
                 [bids_dir] [output_dir] [{participant,group}]

    p3 processing pipeline

    positional arguments:
      bids_dir              The directory with the input dataset formatted
                            according to the BIDS standard.
      output_dir            The directory where the output files should be stored.
                            If you are running group level analysis this folder
                            should be prepopulated with the results of the
                            participant level analysis.
      {participant,group}   Level of the analysis that will be performed. Multiple
                            participant level analyses can be run independently
                            (in parallel) using the same output_dir. (Note: group
                            flag is currently disabled since there are not any
                            group level functionalities in this pipeline
                            currently. This is set to 'participant' by default and
                            can be omitted.)

    optional arguments:
      -h, --help            show this help message and exit
      --participant_label PARTICIPANT_LABEL [PARTICIPANT_LABEL ...]
                            The label(s) of the participant(s) that should be
                            analyzed.The label corresponds to
                            sub-<participant_label> from the BIDS spec (so it does
                            not include "sub-"). If this parameter is not provided
                            all subjects should be analyzed. Multiple participants
                            can be specified with a space separated list.
      --skip_bids_validator
                            Whether or not to perform BIDS dataset validation
      -v, --version         show program's version number and exit
      -s SETTINGS, --settings SETTINGS
                            A JSON settings file that specifies how the pipeline
                            should be configured. If no settings file is provided,
                            the pipeline will use internally specified defaults.
                            See docs for more help details.
      -g, --generate_settings
                            Generates a default settings file in the current
                            working directory for use/modification. This option
                            will ignore all other arguments.
      -m, --multiproc       Runs pipeline in multiprocessing mode. Note that it is
                            harder to debug when this option is on.
      --disable_run         Stop after writing graphs. Does not run pipeline.
                            Useful for making sure your workflow is connected
                            properly before running.
      -w WORKFLOWS [WORKFLOWS ...], --workflows WORKFLOWS [WORKFLOWS ...]
                            Other paths p3 should search for workflows. Note that
                            you should have an empty __init__.py so that the
                            directory is importable.
      --summary             Get a summary of the BIDS dataset input.


This summary internally uses pybids to show availiable keys to filter on.
If you are using the default p3_bidsselector workflow, you can use the keys
here to specify what images to process. For example, in the settings file:

.. code:: json

    {
        "bids_query":
        {
            "T1":
            {
                "type": "T1w"
            },
            "epi":
            {
                "modality": "func",
                "task: "rest"
            }
        }
    }

This will filter all T1 images by type "T1w", while epi images will use modality
"func" and task "rest".

You can filter on specific subjects and runs by using []:

.. code:: json

    {
        "bids_query":
        {
            "T1":
            {
                "type": "T1w",
                "subject": "MSC0[12]"
            },
            "epi":
            {
                "modality": "func",
                "task": "rest",
                "run": "[13]"
            }
        }
    }

This will query will use subjects MSC01 and MSC02 and process epis with runs 1 and 3.
