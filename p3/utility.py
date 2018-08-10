import os
from bids.grabbids import BIDSLayout

def get_basename(filename):
    """
        Just a convenient function for getting the filename without extension
    """

    # strip filename extension
    name,ext = os.path.splitext(os.path.basename(filename))
    while(ext != ''):
        name,ext = os.path.splitext(os.path.basename(name))

    # return the basename
    return name

def set_atlas_path(atlas):
    """
        Checks atlas path for existence
    """

    # check atlas path; if not exists check the templates directory
    if not os.path.exists(atlas):
        # check in templates dir
        if os.path.exists(os.path.join(os.path.dirname(os.path.realpath(__file__)),'templates',os.path.basename(atlas))):
            # set atlas to that directory
            atlas = os.path.join(os.path.dirname(os.path.realpath(__file__)),'templates',os.path.basename(atlas))
        else:
            raise IOError('Could not find specified atlas file.')

    # return the path to the atlas
    return atlas

def output_BIDS_summary(bids_dir):
    """
        Get a summary of the BIDS dataset input
    """

    # call pybids
    layout = BIDSLayout(bids_dir)
    print('Below are some available keys in the dataset to filter on:\n')

    # show availiable keys
    keys = [
        'subject',
        'session',
        'run',
        'type',
        'task',
        'modality'
        ]
    for k in keys:
        query = layout.get(target=k,return_type='id')
        print('Availiable {}:'.format(k))
        for q in query:
            print(q,end=' ')
        print('\n')
