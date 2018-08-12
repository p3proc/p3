#!/usr/bin/env python3.6
import setuptools
import os
from p3 import __version__

with open("README.md","r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="p3proc",
    version=__version__,
    author="Andrew Van",
    author_email="vanandrew@wustl.edu",
    description="The p3 fmri processing pipeline",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vanandrew/p3",
    packages=setuptools.find_packages(exclude=["tests"]),
    include_package_data=True,
    install_requires=[
        'nipype >= 1.1.1',
        'duecredit >= 0.2.2',
        'pybids >= 0.6.3',
        'pandas >= 0.23.1',
        'patsy >= 0.5.0',
        'numpy == 1.14.5', # at least until warnings on 1.15.0 are fixed
        'xvfbwrapper >= 0.2.9'
    ],
    scripts=['p3proc'],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    )
)
