# p3 - an extensible preprocessing pipeline

p3 is an extensible preprocessing pipeline that encourages
experimentation and customization. In addition to providing a [BIDS](http://bids.neuroimaging.io/)-compatible preprocessing
pipeline for users, it also provides a platform to quickly and easily integrate new
processing methods into an neuroimaging processing stream.

Powered by the [nipype](https://nipype.readthedocs.io/en/latest/index.html) project, p3 takes advantage of the cross package python interface
it provides, allowing users to use a variety of neuroimaging software in their pipelines from
one standard interface. The [nipype](https://nipype.readthedocs.io/en/latest/index.html) concepts of nodes and workflows allows users to construct
processing streams in an intuitive manner.

[![Build Status](https://travis-ci.org/p3proc/p3.svg?branch=master)](https://travis-ci.org/p3proc/p3) [![codecov](https://codecov.io/gh/p3proc/p3/branch/master/graph/badge.svg)](https://codecov.io/gh/p3proc/p3) [![https://www.singularity-hub.org/static/img/hosted-singularity--hub-%23e32929.svg](https://www.singularity-hub.org/static/img/hosted-singularity--hub-%23e32929.svg)](https://singularity-hub.org/collections/1453) [![](https://images.microbadger.com/badges/version/p3proc/p3.svg)](https://microbadger.com/images/p3proc/p3 "Get your own version badge on microbadger.com") [![PyPI version](https://badge.fury.io/py/p3proc.svg)](https://badge.fury.io/py/p3proc)

## DevOps Notes

change version --> build p3 --> upload to PyPI --> upload to docker hub --> build on singularity hub

### Build p3 package

```
# change version in p3/version first!
python3 setup.py sdist bdist_wheel # creates the package
```

### Upload to PyPI
```
twine upload dist/* # uploads new packages
```

### Build and upload Docker image
```
# build/tag images
docker build . -t p3proc/p3:tag # builds and tags image
docker tag p3proc/p3:tag p3/proc:latest # tags the built image as latest

# push images
docker push p3proc/p3:tag
docker push p3proc/p3:latest
```

### Add Singularity file for hub build
```
# create singularity build file
touch Singularity/Singularity.tag

# open Singularity/Singularity for an example
```

See the [documentation](http://p3.readthedocs.io/en/latest/) for more information.
