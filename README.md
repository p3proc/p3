# p3 - an extensible preprocessing pipeline
An fMRI Preprocessing Pipeline in python based on a 2015 Jonathan Power Pipeline

[![https://www.singularity-hub.org/static/img/hosted-singularity--hub-%23e32929.svg](https://www.singularity-hub.org/static/img/hosted-singularity--hub-%23e32929.svg)](https://singularity-hub.org/collections/1388)

#### Installing

##### Docker/Singularity Install

Simply pull the image from either [Docker Hub](https://hub.docker.com/r/vanandrew/p3/) or
[Singularity Hub](https://www.singularity-hub.org/collections/1388)
```
# Docker
docker pull vanandrew/p3:[version]

# Singularity
singularity pull docker://vanandrew/p3:[version] # Docker version for conversion
# or (the recommended way)
singularity pull shub://vanandrew/p3:[version] # Direct Singularity Image
```
You should replace `[version]` with the pipeline release you are interested in.

##### Native Install (For Developers)

You will need python 3.6.x installed. If you are on a linux distro, the easiest way is to compile
from [source](https://www.python.org/downloads/release/python-366/). If you are on a mac, you can
use [Homebrew](https://brew.sh/).

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
./p3proc [BIDS_dataset] [output_folder]
```

##### Uasge

See the [documentation](http://p3.readthedocs.io/en/latest/) for more information.
