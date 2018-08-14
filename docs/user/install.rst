.. _Install:

Installation
============
There are 2 ways to install and use p3. The first and recommended way for most
users is to use the pre-built software containers available from `Docker Hub`_
and `Singularity Hub`_. The second is to install p3 and all its dependencies
natively.

Docker/Singularity
------------------
You can obtain the p3 container images by pulling from their respective repos on
`Docker Hub`_ and `Singularity Hub`_.

.. code:: bash

    # You can replace 'latest' with the specific version you want

    # Docker
    docker pull vanandrew/p3:latest

    # Singularity
    ### Direct Singularity Image
    singularity pull shub://vanandrew/p3:latest
    ### Docker version for conversion; known to fail occasionally
    singularity pull docker://vanandrew/p3:latest

You can then run the pipeline with the run commands of Docker_ and Singularity_.

.. code:: bash

    # docker
    docker run -it --rm vanandrew/p3:latest

    # singularity
    singularity run vanandrew_p3.simg

See the :ref:`Usage` section for more details on how to run p3.

Native Install (For Advanced Users and Developers)
--------------------------------------------------
The native install process for p3 is quite involved and generally not recommended
for most end users. It is mainly intended for developers of p3 to debug the pipeline.

To use the native version of p3. It is recommended to have at least Python 3.6 and up. On Linux,
the easiest way to obtain a copy is from your package manager, or to compile from `Python Source`_.
If you are on a Mac, the recommended way is through Homebrew_.

After obtaining Python, you can install p3 in 2 ways. The first is to git clone the repo and
install all the Python dependencies in requirements.txt.

.. code:: bash

    # git clone the repo
    git clone https://github.com/vanandrew/p3.git
    cd p3

    # you can use the --user flag to install locally; Make sure to use pip3.6+!
    pip install -r requirements.txt

If you are testing with documentation, also install the requirements.txt under the docs.

.. code:: bash

    # This installs the docs dependencies
    pip install -r docs/requirements.txt

The other way is install p3 via pip.

.. code:: bash

    # install via pip
    pip install p3proc

Note that this method does not let you modify the source code/documentation.

Next you will need to install all of neuroimaging packages required by the default workflows in p3.

- AFNI_
- FSL_
- Freesurfer_
- ANTs_

Follow the instructions for each respective package's install page for your OS.

You will also need the bids-validator application which can be obtained through npm.

.. code:: bash

    # This installs the bids validator globally
    npm install -g bids-validator

This should allow you to run all default p3 pipeline workflows. See the :ref:`Usage`
section for more details on running the pipeline.

.. include:: ../links.rst
