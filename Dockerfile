# p3 docker image
FROM p3proc/p3base:0.1
MAINTAINER Andrew Van <vanandrew@wustl.edu>

# Install p3proc + other dependencies
RUN pip install p3proc

# Set entrypoint
ENTRYPOINT ["p3proc"]
