# Skullstrip Docker Image
FROM vanandrew/dglabimg:latest
MAINTAINER Andrew Van <vanandrew@wustl.edu>

# install xvfb and xvfbwrapper
RUN apt-get install -y xvfb
RUN pip3 install xvfbwrapper

# Add files to /mnt
ADD skullstrip.py /mnt/
ADD skullstripnodes.py /mnt/
ADD allineate.patch /mnt/

# patch nipype with working allineate patch
RUN patch /usr/local/lib/python3.5/dist-packages/nipype/interfaces/afni/preprocess.py -i /mnt/allineate.patch

# make directories
RUN mkdir -p /input \
    mkdir -p /output

# Set Entrypoint
WORKDIR /mnt
ENTRYPOINT ["/mnt/skullstrip.py"]
