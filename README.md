# p3 - an extensible preprocessing pipeline
An fMRI Preprocessing Pipeline in python based on a 2015 Jonathan Power Pipeline

#### Installing
To use this pipeline you can do the following:

##### Docker/Singularity Install

TBD - It's on the TODO list... I promise!

##### Native Install (For Developers)

You will need python 3.6.x installed. If you are on a linux distro, the easiest way is to compile from [source](https://www.python.org/downloads/release/python-366/). If your
on a mac, you can use [homebrew](https://brew.sh/).

Install the dependencies in requirements.txt using:
```
# you can use the --user flag to install locally; Make sure to use pip3.6!
pip install -r requirements.txt
```

If you are a developer testing with documentation, also install the requirements.txt under docs:
```
pip install -r docs/requirements.txt
```

You will also need to install [afni](https://afni.nimh.nih.gov/download) and [fsl](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation).
Follow the instructions for each respective package's install page.

You can then clone this repo on your system, and run the pipeline:
```
git clone https://github.com/vanandrew/p3.git
cd p3
./p3.py [BIDS_dataset] [output_folder]
```

##### How to use

For more comprehensive usage information, see the [documentation](http://p3.readthedocs.io/en/latest/).

See Help
```
p3.py -h
```

```
usage: p3.py [-h]
             [--participant_label PARTICIPANT_LABEL [PARTICIPANT_LABEL ...]]
             [--skip_bids_validator] [-v] [-s SETTINGS] [-g] [-m]
             [--disable_run]
             [bids_dir] [output_dir] [{participant,group}]

p3 processing pipeline

positional arguments:
  bids_dir              The directory with the input dataset formatted
                        according to the BIDS standard.
  output_dir            The directory where the output files should be stored.
                        If you are running group level analysis this folder
                        should be prepopulated with the results of the
                        participant level analysis.
  {participant,group}   Level of the analysis that will be performed. Multiple
                        participant level analyses can be run independently
                        (in parallel) using the same output_dir. (Note: group
                        flag is currently disabled since there are not any
                        group level functionalities in this pipeline
                        currently. This is set to 'participant' by default and
                        can be omitted.)

optional arguments:
  -h, --help            show this help message and exit
  --participant_label PARTICIPANT_LABEL [PARTICIPANT_LABEL ...]
                        The label(s) of the participant(s) that should be
                        analyzed.The label corresponds to
                        sub-<participant_label> from the BIDS spec (so it does
                        not include "sub-"). If this parameter is not provided
                        all subjects should be analyzed. Multiple participants
                        can be specified with a space separated list.
  --skip_bids_validator
                        Whether or not to perform BIDS dataset validation
  -v, --version         show program's version number and exit
  -s SETTINGS, --settings SETTINGS
                        A JSON settings file that specifies how the pipeline
                        should be configured. If no settings file is provided,
                        the pipeline will use internally specified defaults.
                        See docs for more help details.
  -g, --generate_settings
                        Generates a default settings file in the current
                        working directory for use/modification. This option
                        will ignore all other arguments.
  -m, --multiproc       Runs pipeline in multiprocessing mode. Note that it is
                        harder to debug when this option is on.
  --disable_run         Stop after writing graphs. Does not run pipeline

```
