p3 - fmri processing pipeline
=============================

p3 is an extensible preprocessing pipeline that encourages
experimentation and customization. In addition to providing a BIDS_-compatible preprocessing
pipeline for users, it also provides a platform to quickly and easily integrate new
processing methods into an neuroimaging processing stream.

Powered by the nipype_ project, p3 takes advantage of the cross package python interface
it provides, allowing users to use a variety of neuroimaging software in their pipelines from
one standard interface. The nipype_ concepts of nodes and workflows allows users to construct
processing streams in an intuitive manner.

.. toctree::
    :maxdepth: 2

    user/install.rst
    user/usage.rst
    user/settings.rst
    user/outputs.rst
    usr/tutorials.rst
    dev/developers.rst
    dev/tutorials.rst

Quick Usage
-----------

p3 uses the standard BIDS_ app run command. You can run p3 by simply running:

.. code:: bash

    p3proc [BIDS directory] [output directory]

This will run the p3 pipeline with the all standard built in settings.

If you are using the Docker_ version of p3, the command is:

.. code:: bash

    docker run -it --rm \
        -v [BIDS directory]:/dataset \
        -v [output directory]:/output \
        vanandrew/p3 /dataset /output

where **[BIDS directory]** and **[output directory]** are paths on the host
system to the BIDS dataset and output directory respectively.

If you are using the Singularity_ version of p3, the command is:

.. code:: bash

    singularity run \
        -B [BIDS directory]:/dataset \
        -B [output directory]:/output \
        vanandrew_p3.simg /dataset /output

where **vanandrew_p3.simg** is replaced with the singularity image filename.

.. include:: links.rst
