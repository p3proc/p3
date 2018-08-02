# p3 - an extensible preprocessing pipeline
An fMRI Preprocessing Pipeline in python based on a 2015 Jonathan Power Pipeline

[![https://www.singularity-hub.org/static/img/hosted-singularity--hub-%23e32929.svg](https://www.singularity-hub.org/static/img/hosted-singularity--hub-%23e32929.svg)](https://singularity-hub.org/collections/1388)

#### Installing

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

See the [documentation](http://p3.readthedocs.io/en/latest/).
