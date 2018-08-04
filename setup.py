import setuptools
import os

# get version
__version__ = open(os.path.join(os.path.dirname(os.path.realpath(__file__)),'version')).read()

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
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    )
)
