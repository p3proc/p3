"""
    Define Custom Functions and Interfaces
"""

def get_metadata(epi_file,bids_dir):
    """
        This function requires the "IntendedFor" field in the json sidecar of the field map to be defined.
        (See section 8.3.5 of the BIDS spec)
    """

    import re
    import os
    import subprocess
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

    # get the phase encoding direction
    ped = layout.get_metadata(epi_file)['PhaseEncodingDirection']

    # determine image orientation
    output = subprocess.run(['3dinfo','-orient',phasediff],stdout=subprocess.PIPE)
    orientation = output.stdout.decode('utf-8').rstrip()

    if ped[0] == 'i':
        # choose orientation based on ped
        if orientation[0] == 'R':
            orient_code = 'RL'
        elif orientation[0] == 'L':
            orient_code = 'LR'
        else:
            raise ValueError('Invalid Orientation!')
    elif ped[0] == 'j':
        if orientation[1] == 'A':
            orient_code = 'AP'
        elif orientation[1] == 'P':
            orient_code = 'PA'
        else:
            raise ValueError('Invalid Orientation!')
    elif ped[0] == 'k':
        if orientation[2] == 'I':
            orient_code = 'IS'
        elif orientation[2] == 'S':
            orient_code = 'SI'
        else:
            raise ValueError('Invalid Orientation!')
    else:
        raise ValueError('Invalid Phhase Encoding Direction Parsed!')

    # reverse the orientation if ped was negative
    if ped[1] == '-':
        orient_code = orient_code[::-1]

    # Using the orient code to find the equivalent FSL ped
    ped = {'RL':'x','LR':'x-','AP':'y','PA':'y-','SI':'z','IS':'z-'}[orient_code]

    # return the magnitude and phase image paths
    return (magnitude,phasediff,TE,echospacing,ped)

def fsl_prepare_fieldmap(phasediff,magnitude,TE):
    import os
    from p3.base import get_basename

    # save to node folder (go up 2 directories bc of iterfield)
    cwd = os.path.dirname(os.path.dirname(os.getcwd()))

    # get filename to output
    out_file = os.path.join(cwd,'{}_fieldmap.nii.gz'.format(get_basename(phasediff)))

    # run prepare field map
    os.system('fsl_prepare_fieldmap SIEMENS {} {} {} {}'.format(
        phasediff,
        magnitude,
        out_file,
        TE
    ))

    # return the fieldmap file
    return out_file

def get_prefix(filename):
    from p3.base import get_basename
    return '{}_'.format(get_basename(filename))
