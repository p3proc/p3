# Skullstrip Docker Image
FROM vanandrew/dglabimg:latest
MAINTAINER Andrew Van <vanandrew@wustl.edu>

# Add files to /mnt
ADD skullstrip.py /mnt/
ADD skullstripnodes.py /mnt/

# make directories
RUN mkdir -p /input \
    mkdir -p /output

# Set Entrypoint
WORKDIR /mnt
ENTRYPOINT ["/mnt/skullstrip.py"]
