.. _`Sideloading`:

Sideloading
-----------
Sideloading is a unique feature of p3 that allows a user to manually
substitute any input to any node in any workflow. This is useful in cases
where the output of any step has failed/is undesirable, and needs to be
manually adjusted before continuing further steps of the pipeline. Sideloading
is accomplished by editing the **sideload** key in the settings file.

1. Identify the node you want to replace an input field for.

   In this tutorial, we are replacing the skullstrip output with one of our own files.

   .. figure:: ../_static/imgs/p3_skullstrip.png

        We will replace the **T1_skullstrip** field of the output node of the p3_skullstrip
        workflow with a skullstrip file that I've manually made at ~/skullstrip_edit/T1_skullstrip.nii.gz.

2. Generate a settings file.

   .. code:: bash

        # generate a settings file
        p3proc -g settings.json

3. In the settings file, edit the **sideload** key.

   .. code:: bash

        # We are replacing the T1_skullstrip field of the output node of the
        # p3_skullstrip workflow
        "sideload": [
            {
                "workflow": "p3_skullstrip",
                "node": "output",
                "input": ["T1_skullstrip", "~/skullstrip_edit/T1_skullstrip.nii.gz"] # we specify the path of our skullstrip edit
            }, # This is a list, so the comma allows you
               # to specify extra sideload entries here
        ]

   .. note::

        If you are using Docker/Singularity, be aware that any path you specify is
        relative to the container, not the host. So if ~/skullstrip_edit is mounted
        to /myedits, use the path /myedits/T1_skullstrip.nii.gz instead.

   .. note::

        MAKE SURE YOU SAVE THE SETTINGS FILE!!! OuO!

4. Run the pipeline.

   If you sideloaded the node correctly, you should see this in the p3 output.

   .. code:: bash

        # You should see me OuO!

        Disconnect: ('biasfieldcorrect', 'output_image', 'output', 'T1_skullstrip')

        Sideload Status for node p3_skullstrip.output:

        T1_skullstrip = ~/skullstrip_edit/T1_skullstrip.nii.gz
        allineate_freesurfer2anat = <undefined>

   And the graph of the workflow should reflect this change by disconnecting the
   node from the original node it was connected to.

   .. figure:: ../_static/imgs/p3_skullstrip_sideload.png

        **biasfieldcorrect** has been disconnected from the **output**.
