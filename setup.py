#!/usr/bin/env python

from setuptools import find_packages, setup

setup(
    name='lippukala',
    version='1.1.1',
    description='Desuconin ja Traconin e-lippu-jarjestelma',
    author='Aarni Koskela',
    author_email='akx@desucon.fi',
    url='https://github.com/kcsry/lippukala',
    packages=find_packages('.', exclude=('lippukala_test*',)),
    include_package_data=True,
    install_requires=[
        'Django>=1.8',
        'xlwt>0.7,<=1.1',
        'reportlab>=2.6',
    ],
)
