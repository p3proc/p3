.. p3 documentation master file, created by
   sphinx-quickstart on Thu Jul 12 12:29:44 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to p3's documentation!
==============================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

.. container::

    This summary internally uses pybids to show availiable keys to filter on.
    If you are using the default p3_bidsselector workflow, you can use the keys
    here to specify what images to process. For example, in the settings file:

    .. code:: json

        {
            'bids_query':
            {
                'T1':
                {
                    'type': 'T1w'
                },
                'epi':
                {
                    'modality': 'func',
                    'task: 'rest'
                }
            }
        }

    This will filter all T1 images by type T1w, while epi images will use modality
    'func and task rest.

    You can filter on specific subjects and runs by using []:

    .. code:: json

        {
            'bids_query':
            {
                'T1':
                {
                    'type': 'T1w',
                    'subject': 'MSC0[12]'
                },
                'epi':
                {
                    'modality': 'func',
                    'task': 'rest',
                    'run': '[13]'
                }
            }
        }

    This will query will use subjects MSC01 and MSC02 and process epis with runs 1 and 3.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
