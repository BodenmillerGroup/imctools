# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='imctools',
    version='1.0.1',
    description='Tools to handle IMC data',
    long_description=readme,
    author='Vito Zanotelli',
    author_email='vito.zanotelli@uzh.ch',
    url='https://github.com/bodenmillerlab/imctools',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=[
        'tifffile>=0.13.5',
        'scikit-image',
        'numpy',
        'scipy',
        'pandas']
)
