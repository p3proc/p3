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

This will run the pipeline with its default settings. To customize the settings,
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
