# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='imctools',
    version='0.0.3',
    description='Tools to handle IMC data',
    long_description=readme,
    author='Vito Zanotelli',
    author_email='vito.zanotelli@uzh.ch',
    url='https://github.com/bodenmillerlab/imctools',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires = [
                       'tifffile', 'scikit-image', 'numpy', 'scipy', 'requests'
                   ],
)

