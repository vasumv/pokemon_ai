import os
from setuptools import setup, find_packages
from pip.req import parse_requirements
import uuid

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements("requirements.txt", session=uuid.uuid1())

# reqs is a list of requirement
# e.g. ['django==1.5.1', 'mezzanine==1.4.6']
reqs = [str(ir.req) for ir in install_reqs]


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...

setup(
    name = "showdown_ai",
    version = "0.0.1",
    author = "Vasu Vikram",
    author_email = "vasumvikram@gmail.com",
    description = "",
    license = "MIT",
    keywords = "",
    url = "",
    packages=find_packages(include=[
        'showdown_ai'
    ]),
    entry_points={
        'console_scripts': [
            'showdownai=showdown_ai.showdown:main'
        ],
    },
    install_requires=reqs,
    long_description="",
    classifiers=[
    ],
)
