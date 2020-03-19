# imctools

[![Build Status](https://github.com/BodenmillerGroup/imctools/workflows/CI/badge.svg)](https://github.com/BodenmillerGroup/imctools/workflows/CI/badge.svg)
[![PyPI version](https://badge.fury.io/py/imctools.svg)](https://pypi.python.org/pypi/imctools)

> `imctools` v2 is now hosted in separate repository due to many changes in data output format, CLI changes, dropped Python 2 and Fiji plugins support, etc.
> For older version of the library please check [imctools](https://github.com/BodenmillerGroup/imctools) repository.
> We strongly encourage you to migrate to `imctools` v2 as all further efforts will be focused on a development of this version.

An IMC file conversion tool that aims to convert IMC raw data files (.mcd, .txt) into an intermediary ome.tiff, containing all the relevant metadata. Further it contains tools to generate simpler TIFF files that can be directly be used as input files for e.g. CellProfiller, Ilastik, Fiji etc.

For a description of the associated segmentation pipline, please visit: https://github.com/BodenmillerGroup/ImcSegmentationPipeline

Documentation: https://bodenmillergroup.github.io/imctools

## Features

- MCD lazy data access using memorymaps
- Full MCD metadata access
- TXT file loading
- OME-TIFF loading
- OME-TIFF/TIFF export (including optional compression)

## Prerequisites

- Supports Python 3.7 or newer
- External dependencies: `numpy`, `pandas`, `xmltodict`, `xtiff`.

## Installation

Preferable way to install `imctools` is via official PyPI registry. Please define package version explicitly in order to avoid incompatibilities between v1.x and v2.x versions::
```
pip install imctools==2.0.0
```

## Usage

`imctools` is often used from Jupyter as part of the pre-processing pipeline, mainly using the __converters__ wrapper functions. Please check the [following example](https://github.com/BodenmillerGroup/ImcSegmentationPipeline/blob/development/scripts/imc_preprocessing.ipynb) as a template.

Further `imctools2` can be directly used as a module:

```python
from imctools.io.mcd.mcdparser import McdParser

fn_mcd = "/home/vitoz/Data/varia/201708_instrument_comp/mcd/20170815_imccomp_zoidberg_conc5_acm1.mcd"

parser = McdParser(fn_mcd)

# Get original metadata in XML format
xml = parser.get_mcd_xml()

# Get parsed session metadata (i.e. session -> slides -> acquisitions -> channels, panoramas data)
session = parser.session

# Get all acquisition IDs
ids = parser.session.acquisition_ids

# The common class to represent a single IMC acquisition is AcquisitionData class.
# Get acquisition data for acquisition with id 2
ac_data = parser.get_acquisition_data(2)

# imc acquisitions can yield the image data by name (tag), label or index
channel_image1 = ac_data.get_image_by_name('Ir191')
channel_image2 = ac_data.get_image_by_label('Histone_phospho_125((2468))Eu153')
channel_image3 = ac_data.get_image_by_index(7)

# or can be used to save OME-TIFF files
fn_out ='/home/vitoz/temp/test.ome.tiff'
ac_data.save_ome_tiff(fn_out, names=['Ir191', 'Yb172'])

# save multiple standard TIFF files in a folder
ac_data.save_tiffs("/home/anton/tiffs", compression=0, bigtiff=False)

# as the mcd object is using lazy loading memory maps, it needs to be closed
# or used with a context manager.
parser.close()
```
