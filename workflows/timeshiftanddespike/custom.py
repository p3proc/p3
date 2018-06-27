"""
    Define Custom Functions and Interfaces
"""
from nipype.interfaces import afni,base

# Define string function to extract slice time info and write to file
def extract_slicetime(epi,bids_dir):
    # import necessary libraries
    from bids.grabbids import BIDSLayout
    import os
    import csv

    # save to node folder (go up 2 directories bc of iterfield)
    cwd = os.path.dirname(os.path.dirname(os.getcwd()))

    # specify bids layout
    layout = BIDSLayout(bids_dir)

    # get slicetiming info
    slice_timing = layout.get_metadata(epi)['SliceTiming']

    # get TR
    TR = layout.get_metadata(epi)['RepetitionTime']

    # set filename
    filename = os.path.join(cwd,'{}.SLICETIME'.format(os.path.splitext(os.path.basename(epi))[0]))

    # write slice timing to file
    with open(filename,'w') as st_file:
        wr = csv.writer(st_file,delimiter=' ')
        wr.writerow(slice_timing)

    # return timing pattern and TR
    return ('@{}'.format(filename),str(TR))

# Extend afni despike
# define extended input spec
class ExtendedDespikeInputSpec(afni.preprocess.DespikeInputSpec):
    spike_file = base.File(name_template="%s_despike_SPIKES", desc='spike image file name',
                    argstr='-ssave %s', name_source="in_file")

# define extended output spec
class ExtendedDespikeOutputSpec(afni.base.AFNICommandOutputSpec):
    spike_file = base.File(desc='spike file', exists=True)

# define extended afni despike
class ExtendedDespike(afni.Despike):
    input_spec = ExtendedDespikeInputSpec
    output_spec = ExtendedDespikeOutputSpec
