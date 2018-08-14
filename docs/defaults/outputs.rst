.. _Outputs:

Outputs
-------
.. note::

    It should be noted that these are the outputs of the default workflows for the
    p3 pipeline. Changes to the workflow will not gurantee that you will have the same outputs
    as these or that they will be named the same.

**graph**
    This folder contains the graph outputs of each subworkflow as well as the overall workflow (saved as **p3.png**).

**freesurfer**
    This folder contains the freesurfer outputs. There is a **skullstrip** subfolder for storing
    the brainmask used in the default p3 skullstrip workflow. Freesurfer outputs for each subject are
    under each subject folder prefixed with **sub-**.

**p3**
    This folder contains the main outputs of the p3 pipeline. Outputs that are generally used for further
    preprocessing stages are placed here. Subject outputs are separated into subfolders prefixed with
    **sub-**. The structure of each subject folder should be the following:

    **atlas**
        Contains the atlas image resampled to the space of the functional reference image::

            sub-(subject)/atlas/(atlas)_funcres.nii.gz # resampled atlas

    **anat**
        Contains the processed anatomy image, and its resampled functional space version::

            sub-(subject)/anat/(processed_anat).nii.gz # processed aligned anatomy image
            sub-(subject)/anat/(processed_anat)_funcres.nii.gz # resampled version

    **func**
        This folder has an option session directory output if session are detected, prefixed with
        **ses-**. Aligned processed functional images are output here::

            sub-(subject)/func/ses-(session)/(processed_func_image)_moco_atlas.nii.gz # aligned functional image
            sub-(subject)/func/ses-(session)/(func).1D # motion parameters
            sub-(subject)/func/ses-(session)/(func).FD # framewise displacement
            sub-(subject)/func/ses-(session)/(func).tmask # temporal mask
            sub-(subject)/func/ses-(session)/(funce)_filtered.1D # filtered motion parameters
            sub-(subject)/func/ses-(session)/(func)_filtered.FD # filtered framewise displacment
            sub-(subject)/func/ses-(session)/(func)_filtered.tmask # temporal Mask

**p3_QC**
    This folder contains the QC outputs of the p3 pipeline. Outputs that are only useful for
    quality checking and are most likely *not* used for futher processing stages are placed here.
    All subfolders have a subject folder prefixed by **sub-**. The following subfolders are the following:

    **alignfunctoanat**
        This contains QC outputs for the functional to anatomy alignment workflow::

            sub-(subject)(processed_func)_reference_unwarped_skullstrip.nii.gz # skullstripped functional reference image
            sub-(subject)/(processed_func)_reference_unwarped_skullstrip_anat.nii.gz # aligned reference image
            sub-(subject)/(avg_anat)_skullstrip_corrected.nii.gz # skullstripped bias field corrected anatomy image

    **bidsselector**
        This contains QC outputs from the bidsselector workflow. Despite it's name
        this workflow also does the alignement of each anatomy image to each other and
        averages them together. The QC output here is for checking these alignments::

            sub-(subject)/(anat).nii.gz # raw anatomy image
            sub-(subject)/(anat)_allineate.nii.gz # aligned anatomy image
            sub-(subject)/(anat)_avg.nii.gz # averaged anatomy image

    **fieldmapcorrection**
        This contains QC outputs for the field map correction workflows::

            sub-(subject)/(processed_func)_reference.nii.gz # functional reference image
            sub-(subject)/(processed_func)_reference_unwarped.nii.gz # unwarped functional reference image
            sub-(subject)/(processed_func).nii.gz # processed functional image
            sub-(subject)/(processed_func)_unwarped.nii.gz # unwarped functional image
            sub-(subject)/(processed_func)_unwarped_realign.nii.gz # realigned unwarped functional image

    **skullstrip**
        This contains the QC outputs for the skullstrip workflow::

            sub-(subject)/(anat)_avg.nii.gz # averaged anatomy image
            sub-(subject)/(anat)_avg_skullstrip.nii.gz # skullstripped anatomy image
            sub-(subject)/(anat)_avg_skullstrip_corrected.nii.gz # bias field corrected skullstripped anatomy image

    **stcdespikemoco**
        This contains the QC outputs for the slice time corrected/despike/motion correction workflow::

            sub-(subject)/(func_processed)_Warped.nii.gz # processed motion corrected functional image

**fs_masks**
    This folder contains the freesurfer mask outputs.

    **aparc_aseg**

    **cb**

    **csf**

    **gm**

    **gmr**

    **scn**

    **wm**

.. include:: ../links.rst
