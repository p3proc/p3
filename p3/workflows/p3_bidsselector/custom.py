"""
    Define Custom Functions and Interfaces
"""

def avganats(anat_list):
    import os
    from p3.utility import get_basename

    # get current path
    path = os.getcwd()

    # join list into string
    filelist = ' '.join(anat_list)

    # get filename of first file
    outfile = '{}_avg.nii.gz'.format(get_basename(anat_list[0]))

    os.system('3dMean -prefix {} {}'.format(
        outfile,
        filelist
    ))

    # return avg anat
    return os.path.join(path,outfile)

def check_query(bids_query,bids_dir):
    """
        Check BIDS selection query
    """
    from bids.grabbids import BIDSLayout

    # get bids layout
    layout = BIDSLayout(bids_dir)

    # parse bids query
    print('\n')
    output = {}
    for key in bids_query:
        # return the query
        output[key] = layout.get(**bids_query[key])
        # print the output of the query
        print('{}:'.format(key))
        for o in output[key]:
            print(o.filename)
    print('Files listed are to be processed.\n\n')
