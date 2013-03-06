#!/usr/bin/env python

import os
from setuptools import setup, find_packages

def requirements(filename):
    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), filename))) as f:
        return f.readlines()

setup(
    name='lippukala',
    version='0.0.0',
    description='Desuconin ja Traconin e-lippu-jarjestelma',
    author='Aarni Koskela',
    author_email='akx@desucon.fi',
    url='https://github.com/kcsry/lippukala',
    packages=find_packages(),
    install_requires=requirements('requirements.txt')
)
