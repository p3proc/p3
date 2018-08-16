.. _`Basic Example`:

Basic Example
-------------
This example shows you how to run p3. It's meant for non-technical users and
assumes not knowledge of Docker.

1. Obtain a BIDS_ dataset. You can convert your own data or use one of the shared
   BIDS_ dataset on OpenNeuro_. In this tutorial, we use the `MSC dataset`_.

    .. figure:: ../_static/imgs/mscbids.png
        :align: center

        The BIDS version of the MSC dataset.

2. Download the p3 `Docker Image`_/`Singularity Image`_.

   .. code:: bash

        # Docker
        docker pull p3proc/p3:latest

        # Verify that the image is installed
        docker images

        REPOSITORY          TAG                  IMAGE ID            CREATED             SIZE
        p3proc/p3           latest               6c8204e4f40f        XX hours ago        17.1GB
        p3proc/p3base       0.1                  59c60216e586        XX hours ago        16.6GB

        # OR

        # Singularity (This will create a .simg file in your current directory)
        singularity pull shub://p3proc/p3:latest

3. In this example, my bids dataset is located in ~/MSC_BIDS. I want my output files
   to go into ~/output.

   But first, let's store a reference to the ~ directory.

   .. code:: bash

        # change to home
        cd ~
        # this stores the home directory as an absolute path in ${HOMEPATH}
        export HOMEPATH=$(pwd -P)

4. Now let's mount the volumes on to the docker container. The **-v** command lets
   you mount host volumes to the docker container. We'll mount the BIDS dataset
   to /dataset on the container and the output directory to the /output directory
   (Note that docker needs absolute paths).

   .. code:: bash

        # run the p3 docker with mounts and not arguments
        docker run -it --rm \ # This is the standard docker run command
            -v ${HOMEPATH}/MSC_BIDS:/dataset:ro \ # this mounts the BIDS data as read-only
            -v ${HOMEPATH}/output:/output \ # mount the output directory
            p3proc/p3

   You should see this output, since we didn't pass any arguments...

   .. code:: bash

        usage: p3proc [-h]
              [--participant_label PARTICIPANT_LABEL [PARTICIPANT_LABEL ...]]
              [--skip_bids_validator] [-v] [-s SETTINGS]
              [-g GENERATE_SETTINGS] [--summary] [--disable_run]
              [-w WORKFLOWS [WORKFLOWS ...]] [-c CREATE_NEW_WORKFLOW] [-m]
              [-d]
              [bids_dir] [output_dir] [{participant,group}]
        p3proc: error: positional arguments bids_dir/output_dir are required.

   If you didn\'t see this exact message. Check for mispellings in your command.

   .. note::

        Docker mounts are automatically created, even if they don\'t exist. This means
        you can use any names for the container path.

        .. code:: bash

            # use a custom path
            docker run -it --rm \
                -v ${HOMEPATH}/mydir:/custompath # This mounts ~/mydir to /custompath
                p3proc/p3

5. Next, let\'s generate a settings file. We need to create a settings folder to mount.

   .. code:: bash

        # and store out settings file
        mkdir ~/mysettings

   Now generate the settings file, mounting our newly created settings folder.

   .. code:: bash

        # Generate the settings file,
        docker run -it --rm \
            -v ${HOMEPATH}/mysettings:/settings \
            p3proc -g /settings/newsettings.json

   This will generate a settings file called **newsettings.json**. Since we mounted
   our **mysettings** folder to the ./settings folder on the container, the **newsettings.json**
   file should exist there.

   The **newsettings.json** file can be modified with any text editor. See the :ref:`Settings`
   section for more details on each option.

6. Finally, let\'s run the pipeline. The most basic command provides a BIDS directory and an output
   directory.

   .. code:: bash

        # Run the most basic pipeline command
        docker run -it --rm \
            -v ${HOMEPATH}/MSC_BIDS:/dataset:ro \
            -v ${HOMEPATH}/output:/output \
            p3proc/p3 /dataset /output # we use the container paths for the dataset/output

   This will run the internally set default settings. If we want to use our
   settings file generated in step 5. We\'ll need to mount our **mysettings**
   folder and add the settings argument to the execution call.

   .. code:: bash

         # Run the most basic pipeline command
         docker run -it --rm \
             -v ${HOMEPATH}/MSC_BIDS:/dataset:ro \
             -v ${HOMEPATH}/output:/output \
             -v ${HOMEPATH}/mysettings:/settings \ # mount our settings folder
             p3proc/p3 /dataset /output -s settings/newsettings.json # add the settings argument

   This will run the pipeline with the specified settings.

That\'s it! You\'ve run the p3 pipeline successfully!

.. include:: ../links.rst
