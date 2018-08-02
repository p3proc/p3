.. Usage:

Usage
=====

.. note::

    The examples in this document use the non-container version of
    p3. If you are using docker/singularity to run p3, simply replace
    any reference to the **p3proc** command with the appropriate container
    call.

    .. code:: bash

        # These are equivalent to p3proc /dataset /output
        docker run -it --rm vanandrew/p3 /dataset /output
        # or
        singularity run vanandrew_p3.simg /dataset /output

    These are just examples. You still need to mount/bind the host volumes
    to access your data see the `Docker Volume`_ and `Singularity Bind`_ documentation.

Overview
--------
.. code-block:: none

    usage: p3proc [-h]
          [--participant_label PARTICIPANT_LABEL [PARTICIPANT_LABEL ...]]
          [--skip_bids_validator] [-v] [-s SETTINGS] [-g] [-m]
          [--disable_run] [-w WORKFLOWS [WORKFLOWS ...]] [--summary]
          [-l LICENSE_FILE]
          [bids_dir] [output_dir] [{participant,group}]

    p3 processing pipeline

    positional arguments:
    bids_dir            The directory with the input dataset formatted
                        according to the BIDS standard.
    output_dir          The directory where the output files should be stored.
                        If you are running group level analysis this folder
                        should be prepopulated with the results of the
                        participant level analysis.
    {participant,group} Level of the analysis that will be performed. Multiple
                        participant level analyses can be run independently
                        (in parallel) using the same output_dir. (Note: group
                        flag is currently disabled since there are not any
                        group level functionalities in this pipeline
                        currently. This is set to 'participant' by default and
                        can be omitted.)

    optional arguments:
    -h, --help          show this help message and exit
    --participant_label PARTICIPANT_LABEL [PARTICIPANT_LABEL ...]
                        The label(s) of the participant(s) that should be
                        analyzed.The label corresponds to
                        sub-<participant_label> from the BIDS spec (so it does
                        not include "sub-"). If this parameter is not provided
                        all subjects should be analyzed. Multiple participants
                        can be specified with a space separated list.
    --skip_bids_validator
                        Whether or not to perform BIDS dataset validation
    -v, --version       show program's version number and exit
    -s SETTINGS, --settings SETTINGS
                        A JSON settings file that specifies how the pipeline
                        should be configured. If no settings file is provided,
                        the pipeline will use internally specified defaults.
                        See docs for more help details.
    -g, --generate_settings
                        Generates a default settings file in the current
                        working directory for use/modification. This option
                        will ignore all other arguments.
    -m, --multiproc     Runs pipeline in multiprocessing mode. Note that it is
                        harder to debug when this option is on.
    --disable_run       Stop after writing graphs. Does not run pipeline.
                        Useful for making sure your workflow is connected
                        properly before running.
    -w WORKFLOWS [WORKFLOWS ...], --workflows WORKFLOWS [WORKFLOWS ...]
                        Other paths p3 should search for workflows. Note that
                        you should have an empty __init__.py so that the
                        directory is importable.
    --summary           Get a summary of the BIDS dataset input.
    -l LICENSE_FILE, --license_file LICENSE_FILE
                        Path to FreeSurfer license key file. To obtain it you
                        need to register (for free) at
                        https://surfer.nmr.mgh.harvard.edu/registration.html

Running the pipeline
--------------------
p3 uses the standard BIDS_ app interface for execution:

.. code:: bash

    p3proc /dataset /output

.. note::

    If you are familiar with the standard BIDS_ app interface, you may
    notice the omission of the analysis level argument (participant,group). p3
    does not currently run with group level analysis and so disables it by default.
    The **participant** option is specified implicitly on program execution.

This will run the pipeline with its default settings. To customize the settings,
you need to generate a settings file.

.. code:: bash

    # This will generate settings in the current directory
    p3proc --generate_settings

This will generate a settings.json file in the current directory.

.. warning::

    The generate settings option will overwrite any file called **settings.json** in the
    current directory you call it in. Be sure you aren't losing any current files before
    running this!

The settings file will allow you to customize runtime settings. See the :ref:`Settings`
section for information about particular parameters in the default parameters in
the settings file.

You can use the settings file you generate with the following:

.. code:: bash

    # This will use the settings defined in settings.json
    p3proc /dataset /output --settings settings.json

Filtering the Dataset
---------------------
p3 has the option to print availiable keys in the BIDS_ dataset that you
can filter.

.. code:: bash

    # Note that the only argument required here is the BIDS dataset itself
    p3proc /MSC_BIDS --summary

    Below are some available keys in the dataset to filter on:

    Availiable subject:
    MSC01

    Availiable session:
    func01 func02 func03 func04 func05 func06 func07 func08 func09 func10 struct01 struct02

    Availiable run:
    1 2 3 4

    Availiable type:
    angio BIS bold defacemask description events FFI group KBIT2 magnitude1 magnitude2 participants phasediff scans sessions T1w T2w Toolbox veno

    Availiable task:
    glasslexical memoryfaces memoryscenes memorywords motor rest

    Availiable modality:
    anat fmap func

The summary internally uses pybids_ to show availiable keys to filter on.
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

.. include:: ../links.rst
