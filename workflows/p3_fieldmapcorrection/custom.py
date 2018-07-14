"""
    Define Custom Functions and Interfaces
"""

def get_magnitude_phase_TE(epi_file,bids_dir):
    """
        This function requires the "IntendedFor" field in the json sidecar of the field map to be defined.
        (See section 8.3.5 of the BIDS spec)
    """

    import re
    import os
    from bids.grabbids import BIDSLayout
    # save to node folder (go up 2 directories bc of iterfield)
    cwd = os.path.dirname(os.path.dirname(os.getcwd()))

    # get bids layout
    layout = BIDSLayout(bids_dir)

    # get fieldmaps for epi
    fieldmap = layout.get_fieldmap(epi_file)

    # we only know how to use phasediff map, anything else is not supported...
    assert fieldmap['type'] == 'phasediff', 'Non-phasediff map unsupported for field map correction.'

    # get the phase diff image
    phasediff = fieldmap['phasediff']

    # get the list of magnitude images
    magnitude = [fieldmap[key] for key in fieldmap if re.match('magnitude',key)]

    # choose 1st magnitude image TODO: add setting that lets user choose magnitude image
    magnitude = magnitude[0]

    # get effective echo time of phasediff
    echotime1 = layout.get_metadata(phasediff)['EchoTime1']
    echotime2 = layout.get_metadata(phasediff)['EchoTime2']
    TE = (echotime2 - echotime1)*1000

    # get the echospacing for the epi image
    echospacing = layout.get_metadata(epi_file)['EffectiveEchoSpacing']

    # return the magnitude and phase image paths
    return (magnitude,phasediff,TE,echospacing)

def fsl_prepare_fieldmap(phasediff,magnitude,TE):
    import os

    # save to node folder (go up 2 directories bc of iterfield)
    cwd = os.path.dirname(os.path.dirname(os.getcwd()))

    # get filename to output
    name,ext = os.path.splitext(os.path.basename(phasediff))
    while(ext != ''):
        name,ext = os.path.splitext(os.path.basename(name))
    out_file = os.path.join(cwd,'{}_fieldmap.nii.gz'.format(name))

    # run prepare field map
    os.system('fsl_prepare_fieldmap SIEMENS {} {} {} {}'.format(
        phasediff,
        magnitude,
        out_file,
        TE
    ))

    # return the fieldmap file
    return out_file

def convert_2_afni(in_file,bids_dir,phasediff):
    import os
    import subprocess

    # I'm lazy, so I just pass in the entire phasediff list...
    # just take the first item of the list because thats the fieldmap
    # for the refimg
    phasediff = phasediff[0]

    # get cwd
    cwd = os.getcwd()

    # get filename to output
    name,ext = os.path.splitext(os.path.basename(phasediff))
    while(ext != ''):
        name,ext = os.path.splitext(os.path.basename(name))
    out_file = os.path.join(cwd,'{}_afni.nii.gz'.format(name))

    # get bids layout
    layout = BIDSLayout(bids_dir)

    # determine the phase encoding direction
    ped = layout.get_metadata(phasediff)['PhaseEncodingDirection']

    # determine image orientation
    output = subprocess.run(['3dinfo','-orient',phasediff],stdout=subprocess.PIPE)
    orientation = output.stdout.decode('utf-8').rstrip()

    # choose orientation based on ped
    if ped[0] == 'i':
        if orientation[0] == 'R':
            orient_code = 'RL'
        elif orientation[0] == 'L':
            orient_code = 'LR'
        else:
            raise ValueError('Invalid Orientation!')
    elif ped[0] == 'j':
        if orientation[0] == 'A':
            orient_code = 'AP'
        elif orientation[0] == 'P':
            orient_code = 'PA'
        else:
            raise ValueError('Invalid Orientation!')
    elif ped[0] == 'k':
        if orientation[0] == 'I':
            orient_code = 'IS'
        elif orientation[0] == 'S':
            orient_code = 'SI'
        else:
            raise ValueError('Invalid Orientation!')
    else:
        raise ValueError('Invalid Phhase Encoding Direction Parsed!')

    # reverse the orientation if ped was negative
    if ped[1] == '-':
        orient_code = orient_code[::-1]

    # get the voxel size of the image
    output = subprocess.run(['3dinfo','-ad{}'.format(ped[0]),phasediff],stdout=subprocess.PIPE)
    voxel_size = output.stdout.decode('utf-8').rstrip()

    # convert to shiftmap to afni readable format
    command = '3dNwarpCat -warp1 {}:{}:{} -prefix {}'.format(
        orient_code,
        voxel_size,
        in_file,
        out_file
    )
    print(command)
    os.system(command)

    # return afni shiftmap
    return out_file
