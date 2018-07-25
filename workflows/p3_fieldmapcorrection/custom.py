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

    # replace ped string with correct letter
    ped = ped.replace('i','x').replace('j','y').replace('k','z')

    # return the magnitude and phase image paths
    return (magnitude,phasediff,TE,echospacing,ped)

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
