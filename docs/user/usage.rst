.. _Usage:

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
    to access your data.

    .. code:: bash

        # mounting in docker is -v
        docker run -it --rm \
        -v /path/on/host:/path/on/image \
        vanandrew/p3 /path/on/image/dataset /path/on/image/output

        # mounting in singularity is -B
        singularity run \
        -B /path/on/host:/path/on/image \
        vanandrew_p3.simg /path/on/image/dataset /path/on/image/output

    It is recommended to refer to the `Docker Volume`_ and `Singularity Bind`_
    documentation.

Overview
--------

.. include:: help_text.txt
    :literal:

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

You can run specific subjects with:

.. code:: bash

    # this runs subject 01 02 and 03
    p3proc /dataset /output --participant_label 01 02 03

These labels are the same as the **sub-** tags defined in the BIDS spec.

You can also run p3 in multiproc mode, which will use all availiable cores of the
compute environment.

.. code:: bash

    # run in multiproc mode
    p3proc /dataset /output --multiproc

p3 includes the BIDS-Validator_, which you can disable.

.. code:: bash

    # this disables the bids validator
    p3proc /dataset /output --skip_bids_validator

Settings
--------
Without a settings argument, p3 will use its default settings. To customize the settings,
you need to generate a settings file.

.. code:: bash

    # This will generate settings at the specified path/file
    p3proc --generate_settings /path/to/settings.json

This will generate a settings.json file at the specified path.

.. warning::

    The generate settings option will overwrite any file in the directory path you
    specify. Be sure you aren't losing any current files before
    running this!

The settings file will allow you to customize runtime settings. See the :ref:`Settings`
section for information about particular parameters in the default parameters in
the settings file.

You can use the settings file you generate with the following:

.. code:: bash

    # This will use the settings defined in settings.json
    p3proc /dataset /output --settings settings.json

Creating workflows and testing
------------------------------
p3 allows you to extend its capabilities by adding new workflows. You can create a template workflow with:

.. code:: bash

    # This will create a new template workflow at the specified path
    p3proc --create_new_workflow /path/to/mynewworkflow

    # Template directory stucture
    /path/to/mynewworkflow
        __init__.py
        custom.py
        nodedefs.py
        workflow.py

See creating new workflows for more information.

To use the new workflows you've created. You will need to import them on the command line.

.. code:: bash

    # this will import your workflows and use your settings file
    p3proc /dataset /output --workflows /path/to/workflows --settings /path/to/settings.json

where **/path/to/workflows** is a folder that contains a folder of workflows generated from the **--create_new_workflow**
option, and an empty __init__.py file.

.. code:: bash

        # This is what your directory structure should look like
        /path/to/workflows
            __init__.py
            mynewworkflow1
                __init__.py
                custom.py
                nodedefs.py
                workflow.py
            mynewworkflow2
                __init__.py
                custom.py
                nodedefs.py
                workflow.py
            ...

You also need to register them in the settings file.

.. code:: bash

    # In your settings file, your workflows field should contain the workflow you are adding
    "workflows": [
        "p3_bidsselector",
        "p3_freesurfer",
        "p3_skullstrip",
        "p3_stcdespikemoco",
        "p3_fieldmapcorrection",
        "p3_alignanattoatlas",
        "p3_alignfunctoanat",
        "p3_alignfunctoatlas",
        "p3_create_fs_masks",
        "mynewworkflow" # <-- Added workflow
    ]

.. note::

    When registering the workflow in your settings file, you should use the name of the
    folder containing the workflow, not the name of the workflowgenerator class in the workflow.py file.

A useful option is to stop p3 prior to running the pipeline.

.. code:: bash

    p3proc /dataset /output --disable_run

This is useful to check for errors/see the connected graph output before actually running the pipeline.

You can also use the pipeline in **verbose mode**, which will print useful messages for debugging purposes.

    p3proc /dataset /output --verbose

Filtering the dataset
---------------------
p3 has the option to print availiable keys in the BIDS_ dataset that you
can filter.

.. code:: bash

    # Note that the only argument required here is the BIDS dataset itself
    p3proc /MSC_BIDS --summary

This is what should be outputted:

.. code:: bash

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
                "task": "rest"
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
