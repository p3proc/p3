#!/usr/bin/env python3.6
import setuptools
import os
from p3 import __version__

with open("README.md","r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="p3",
    version=__version__,
    author="Andrew Van",
    author_email="vanandrew@wustl.edu",
    description="The p3 fmri processing pipeline",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vanandrew/p3",
    packages=setuptools.find_packages(exclude=["tests"]),
    include_package_data=True,
    scripts=['p3proc'],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    )
)
