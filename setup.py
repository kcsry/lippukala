#!/usr/bin/env python

from setuptools import find_packages, setup

setup(
    name='lippukala',
    version='1.2.1',
    description='Desuconin ja Traconin e-lippu-jarjestelma',
    author='Aarni Koskela',
    author_email='akx@desucon.fi',
    url='https://github.com/kcsry/lippukala',
    packages=find_packages('.', exclude=('lippukala_test*',)),
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=[
        'Django>=3.0',
        'xlwt',
        'reportlab>=2.6',
    ],
)
