"""
    Define Custom Functions and Interfaces
"""

# weight mask
def alignepi2anat(in_file,anat):
    import os
    import shutil
    import subprocess

    # save to node folder
    cwd = os.getcwd()

    # copy file to cwd
    input_file = os.path.basename(shutil.copy2(in_file,cwd))
    anat_file = os.path.basename(shutil.copy2(anat,cwd))

    # get filename to output
    name,ext = os.path.splitext(os.path.basename(input_file))
    while(ext != ''):
        name,ext = os.path.splitext(os.path.basename(name))
    epi_al_mat = os.path.join(cwd,'{}_al_mat.aff12.1D'.format(name))
    epi_al_orig = os.path.join(cwd,'{}_al.nii.gz'.format(name))
    # head file to convert
    epi_al_head = os.path.join(cwd,'{}_al+orig'.format(name))

    # get location of align_epi_anat command
    out = subprocess.run(['which','align_epi_anat.py'],stdout=subprocess.PIPE)
    script_loc = out.stdout.decode('utf-8').rstrip()

    # run command
    os.system(
        'python2 {} -anat {} -anat_has_skull no -epi2anat '
        '-epi {} -epi_base 0 -epi_strip None -suffix _al -tshift off -volreg off '
        '-big_move -cmass nocmass -resample on'.format(
            script_loc,
            anat_file,
            input_file
        )
    )

    # convert to nifti
    os.system('3dAFNItoNIFTI -prefix {} {} -verb'.format(
        epi_al_orig,
        epi_al_head
    ))
    raise ValueError

    return(epi_al_mat,epi_al_orig)
