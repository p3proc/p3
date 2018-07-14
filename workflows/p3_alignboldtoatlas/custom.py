"""
    Define Custom Functions and Interfaces
"""

def NwarpApply(in_file,reference,tfm1,tfm2,tfm3,tfm5,tfm0=None,tfm4=None):
    import os

    # save to node folder (go up 2 directories bc of iterfield)
    cwd = os.path.dirname(os.path.dirname(os.getcwd()))

    # strip filename
    filename,ext = os.path.splitext(os.path.basename(in_file))
    while(ext != ''):
        filename,ext = os.path.splitext(filename)
    out_file = os.path.join(cwd,'{}_atlasalign.nii.gz'.format(filename))

    # check if file already exist and remove it if it does
    if os.path.exists(out_file):
        os.remove(out_file)

    # check if nonlinear transform defined
    if not tfm0:
        tfm0 = '' # set to empty string

    # check if field map correction disabled
    if not tfm4:
        tfm4 = '' # set to empty string

    # tfm3 is t1 --> epi; invert the warp
    tfm3 = '\'INV({})\''.format(tfm3)

    # concatenate warps
    concatenated_warps = ' '.join([tfm0,tfm1,tfm2,tfm3,tfm4,tfm5])
    print(concatenated_warps)

    # run 3dNwarpApply
    os.system('3dNwarpApply -nwarp {} -source {} -master {} -prefix {}'.format(
        concatenated_warps,
        in_file,
        reference,
        out_file
    ))

    # return aligned image
    return out_file
