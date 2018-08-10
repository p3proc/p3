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

    # check if None; this means the IntendedFor tag is not defined; Try to guess the field map from the data
    # TODO THIS POTENTIALLY UNSTABLE CODE. SOMEONE SHOULD COME UP WITH A BETTER WAY TO DO THIS!
    # I assume there is only 1 fieldmap per session
    if not fieldmap:
        print('\n****************************************************************************')
        print('File: {}'.format(epi_file))
        print('IntendedFor field undefined! I\'ll try to guess the fieldmap file...\n')
        sub = os.path.split(epi_file)[1].split("_")[0].split("sub-")[1] # set subject
        type_ = '(phase1|phasediff|epi|fieldmap)' # get all fieldmap types
        files = layout.get(subject=sub, type=type_, extensions=['nii.gz', 'nii']) # get the potential fmaps
        # check files length, if 1 then there is probable only 1 session and only one fieldmap
        if len(files) == 1:
            fieldmap = {
                'phasediff': files[0].filename,
                'type': files[0].type,
                'magnitude1': files[0].filename.replace('phasediff','magnitude1'),
                'magnitude2': files[0].filename.replace('phasediff','magnitude2')
            }
        else: # assume more than one session
            ses = os.path.split(epi_file)[1].split("_")[1].split("ses-")[1]
            for file in files:
                if file.session == ses: # match the session number
                    fieldmap = {
                        'phasediff': file.filename,
                        'type': file.type,
                        'magnitude1': file.filename.replace('phasediff','magnitude1'),
                        'magnitude2': file.filename.replace('phasediff','magnitude2')
                    }

        # check if we were able to get the fieldmap
        assert bool(fieldmap), 'We couldn\'t find a fieldmap. Specify the IntendedFor Field or disable field map correction.'
        print('I think {} is the fieldmap. You should verify this is correct.'.format(fieldmap['phasediff']))
        print('****************************************************************************\n')

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
    from p3.utility import get_basename

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

def convertvsm2ANTSwarp(in_file,ped):
    """
        Convert the voxel shift map to ants warp

        Grabbed this from fmriprep
        (https://github.com/poldracklab/fmriprep/blob/master/fmriprep/interfaces/itk.py#L178)
    """
    import nibabel as nb
    import numpy as np
    import os
    from p3.utility import get_basename

    # save to node folder (go up 2 directories bc of iterfield)
    cwd = os.path.dirname(os.path.dirname(os.getcwd()))

    # load file
    nii = nb.load(in_file)

    phaseEncDim = {'x': 0, 'y': 1, 'z': 2}[ped[0]]

    if len(ped) == 2:
        phaseEncSign = 1.0
    else:
        phaseEncSign = -1.0

    # Fix header
    hdr = nii.header.copy()
    hdr.set_data_dtype(np.dtype('<f4'))
    hdr.set_intent('vector', (), '')

    # Get data, convert to mm
    data = nii.get_data()

    aff = np.diag([1.0, 1.0, -1.0])
    if np.linalg.det(aff) < 0 and phaseEncDim != 0:
       # Reverse direction since ITK is LPS
       aff *= -1.0
    aff = aff.dot(nii.affine[:3, :3])

    # scale the data correctly
    data *= phaseEncSign * nii.header.get_zooms()[phaseEncDim]

    # Add missing dimensions
    zeros = np.zeros_like(data)
    field = [zeros, zeros]
    field.insert(phaseEncDim, data)
    field = np.stack(field, -1)
    # Add empty axis
    field = field[:, :, :, np.newaxis, :]

    # Write out
    out_file = os.path.join(cwd,'{}_antswarp.nii.gz'.format(get_basename(in_file)))
    nb.Nifti1Image(field.astype(np.dtype('<f4')), nii.affine, hdr).to_filename(out_file)

    return out_file

def combinetransforms(avgepi,reference,unwarp,realign):
    import os
    from p3.utility import get_basename

    # save to node folder (go up 2 directories bc of iterfield)
    cwd = os.path.dirname(os.path.dirname(os.getcwd()))

    # get filename to output
    combined_transforms = os.path.join(cwd,'{}_unwarpedtransform.nii.gz'.format(get_basename(avgepi)))

    # set up transforms
    transforms = '-t {} -t {}'.format(
        realign,
        unwarp
    )

    # convert the transforms to 4D
    print('Combining transforms into one warp displacement field...')
    command = 'antsApplyTransforms -f 0.0 -d 3 -o [{},1] {} -r {} -v'.format(
        combined_transforms,
        transforms,
        reference
    )
    print(command)
    os.system(command)

    # return the 4D combined transform
    return combined_transforms

def get_prefix(filename):
    from p3.utility import get_basename
    return '{}_'.format(get_basename(filename))
