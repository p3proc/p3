"""
    Define Custom Functions and Interfaces
"""

# Define custom warp command function
def warp_custom(in_file,card2oblique,args=''):
    import os
    import subprocess
    import shutil

    # save to node folder (go up 2 directories bc of iterfield)
    cwd = os.path.dirname(os.path.dirname(os.getcwd()))

    # copy file to cwd
    input_file = os.path.basename(shutil.copy2(in_file,cwd))
    card_file = os.path.basename(shutil.copy2(card2oblique,cwd))

    # strip filename
    name_nii,_ = os.path.splitext(input_file)
    filename,_ = os.path.splitext(name_nii)

    print("3dWarp -verb -card2oblique {} -prefix {}_ob.nii.gz {} -overwrite {}".format(
        os.path.join(cwd,card_file),
        os.path.join(cwd,filename),
        args,
        os.path.join(cwd,input_file)))

    # spawn the 3dwarp command with the subprocess command
    warpcmd = subprocess.run(
        "3dWarp -verb -card2oblique {} -prefix {}_ob.nii.gz {} -overwrite {}".format(
            os.path.join(cwd,card_file),
            os.path.join(cwd,filename),
            args,
            os.path.join(cwd,input_file)
        ),
        stdout=subprocess.PIPE,l
        shell=True
        )
    with open(os.path.join(cwd,"{}_obla2e_mat.1D".format(filename)),"w") as text_file:
        print(warpcmd.stdout.decode('utf-8'),file=text_file)

    # get the out files
    out_file = os.path.join(cwd,'{}_ob.nii.gz'.format(filename))
    ob_transform = os.path.join(cwd,'{}_obla2e_mat.1D'.format(filename))

    return (out_file,ob_transform)

# weight mask
def create_weightmask(in_file,no_skull):
    import subprocess
    import os
    import shutil

    # save to node folder (go up 2 directories bc of iterfield)
    cwd = os.path.dirname(os.path.dirname(os.getcwd()))

    # copy file to cwd
    input_file = os.path.basename(shutil.copy2(in_file,cwd))

    # strip filename
    name_nii,_ = os.path.splitext(input_file)
    filename,_ = os.path.splitext(name_nii)

    rtn = subprocess.run(
        '3dBrickStat -automask -percentile 90.000000 1 90.000000 {} | tail -n1 | awk \'{{print $2}}\''.format(
            no_skull
        ),
        stdout=subprocess.PIPE,
        shell=True
    )
    perc = float(rtn.stdout.decode('utf-8'))
    calc = subprocess.run(
        '3dcalc -datum float -prefix {}_weighted.nii.gz -a {} -expr \'min(1,(a/\'{}\'))\''.format(
            os.path.join(cwd,filename),
            os.path.join(cwd,input_file),
            perc
        ),
        shell=True
    )

    # return weightmask
    weightmask = os.path.join(cwd,'{}_weighted.nii.gz'.format(filename))
    return weightmask
