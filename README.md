# imctools

[![Build Status](https://travis-ci.org/BodenmillerGroup/imctools.svg?branch=master)](https://travis-ci.org/BodenmillerGroup/imctools)
[![Documentation Status](https://readthedocs.org/projects/imctools/badge/?version=latest)](https://imctools.readthedocs.io/en/latest/?badge=latest)

An IMC file conversion tool that aims to convert IMC rawfiles (.mcd, .txt) into an intermediary ome.tiff, containing all the relevant metadata. Further it contains tools to generate simpler tiff files that can be directly be used as input files for e.g. CellProfiller, Ilastik, Fiji etc.

Further imctools can directly work as a FIJI plugin, exploiting the Jython language. That allows that IMC data can be directly visualized in FIJI.

For a description of the associated segmentation pipline, please visit: https://github.com/BodenmillerGroup/ImcSegmentationPipeline

Documentation: https://imctools.readthedocs.io

## Features

- MCD lazy data access using memorymaps
- Full MCD metadata access
- TXT file loading
- OME-TIFF loading
- OME-TIFF/TIFF export (including optional compression)

## Prerequisites

- The package is written for Python3, but should also work with Python2
- The core functions have a 'base' pure Python/Jython implementation with no dependencies outside the standard libraries.
- The fast functions do need Python packages, such as numpy, scipy etc. installed.

## Installation

Use the pip installation manger to directly install the package from Github:

```
pip install git+https://github.com/BodenmillerGroup/imctools.git
```

## Usage

imctools is often used from jupyter as part of the preprocessing pipeline, mainly using the 'script' wrapper functions. Check 'notebooks/example_preprocessing_pipline.ipynb' as a template

Further imctools can be directly used as a module:

```python
import imctools.io.mcdparser as mcdparser
import imctools.io.txtparser as txtparser
import imctools.io.ometiffparser as omeparser
import imctools.io.mcdxmlparser as meta

fn_mcd = '/home/vitoz/Data/varia/201708_instrument_comp/mcd/20170815_imccomp_zoidberg_conc5_acm1.mcd'

mcd = mcdparser.McdParser(fn_mcd)

# parsed Metadata Access
mcd.acquisition_ids
mcd.get_acquisition_channels('1')
mcd.get_acquisition_description('1')

# a metadata object for comprehensive metadata access
acmeta = mcd.meta.get_object(meta.ACQUISITION, '1')
acmeta.properties

# The common class to represent a single IMC acquisition is
# The IMC acuqisition class.
# All parser classes have a 'get_imc_acquisition' method
imc_ac = mcd.get_imc_acquisition('1')

# imc acquisitions can yield the image data
image_matrix = imc_ac.get_img_by_metal('Ir191')

# or can be used to save the images using the image writer class
fn_out ='/home/vitoz/temp/test.ome.tiff'
img = imc_ac.get_image_writer(filename=fn_out, metals=['Ir191', 'Yb172'])
img.save_image(mode='ome', compression=0, dtype=None, bigtiff=False)

# as the mcd object is using lazy loading memory maps, it needs to be closed
# or used with a context manager.
mcd.close()
```
