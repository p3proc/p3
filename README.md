# p3 - an extensible preprocessing pipeline

p3 is an extensible preprocessing pipeline that encourages
experimentation and customization. In addition to providing a [BIDS](http://bids.neuroimaging.io/)-compatible preprocessing
pipeline for users, it also provides a platform to quickly and easily integrate new
processing methods into an neuroimaging processing stream.

Powered by the [nipype](https://nipype.readthedocs.io/en/latest/index.html) project, p3 takes advantage of the cross package python interface
it provides, allowing users to use a variety of neuroimaging software in their pipelines from
one standard interface. The [nipype](https://nipype.readthedocs.io/en/latest/index.html) concepts of nodes and workflows allows users to construct
processing streams in an intuitive manner.

[![Build Status](https://travis-ci.org/vanandrew/p3.svg?branch=master)](https://travis-ci.org/vanandrew/p3) [![codecov](https://codecov.io/gh/vanandrew/p3/branch/master/graph/badge.svg)](https://codecov.io/gh/vanandrew/p3) [![https://www.singularity-hub.org/static/img/hosted-singularity--hub-%23e32929.svg](https://www.singularity-hub.org/static/img/hosted-singularity--hub-%23e32929.svg)](https://singularity-hub.org/collections/1388)

See the [documentation](http://p3.readthedocs.io/en/latest/) for more information.
