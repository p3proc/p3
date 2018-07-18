.. p3 documentation master file, created by
    sphinx-quickstart on Thu Jul 12 12:29:44 2018.
    You can adapt this file completely to your liking, but it should at least
    contain the root `toctree` directive.

p3 fmri processing pipeline
===========================

The p3 processing pipeline is extensible preprocessing pipeline that encourages
experimentation and customization. In addition to providing a BIDS_-compatible preprocessing
pipeline for users, it also provides a platform to quickly and easily integrate new
processing methods into an neuroimaging processing stream.

Powered by the nipype_ project, p3 takes advantage of the cross package python interface
it provides, allowing users to use a variety of neuroimaging software in their pipelines from
one standard interface. The nipype_ concepts of nodes and workflows allows users to construct
processing streams in an intuitive manner.

.. toctree::
    :maxdepth: 2
    :caption: Contents:

    usage/usage.rst

Quick Usage
-----------

p3 uses the standard BIDS app run command. You can run p3 by simply running:

.. code:: bash

    p3.py [BIDS directory] [output directory]

This will run the p3 pipeline with the all standard built in settings.

If you are using the docker version of p3. The command is:

.. code:: bash

    docker run -it --rm \
        -v [BIDS directory]:/input \
        -v [output directory]:/output \
        vanandrew/p3 /input /output

.. include:: links.rst
