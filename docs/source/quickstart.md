# Quickstart

> `imctools` v2.x has many changes in IMC data output format, available CLI commands, dropped Python 2 and Fiji plugins support, etc.
> If you are using `imctools` in pre-processing pipelines, please install v1.x version until your pipeline is modified accordingly!
> We strongly encourage you to migrate to `imctools` v2.x as all further efforts will be focused on a development of this version.

An IMC file conversion tool that aims to convert IMC raw data files (.mcd, .txt) into an intermediary ome.tiff, containing all the relevant metadata. Further it contains tools to generate simpler TIFF files that can be directly be used as input files for e.g. CellProfiller, Ilastik, Fiji etc.

For a description of the associated segmentation pipline, please visit: https://github.com/BodenmillerGroup/ImcSegmentationPipeline

Version 2.x documentation: https://bodenmillergroup.github.io/imctools

Version 1.x documentation (deprecated): https://imctools.readthedocs.io

## Features

- MCD lazy data access using memorymaps
- Full MCD metadata access
- TXT file loading
- OME-TIFF loading
- OME-TIFF/TIFF export (including optional compression)

## Prerequisites

- Supports Python 3.7 or newer
- External dependencies: `imagecodecs`, `pandas`, `xmltodict`, `xtiff`.

## Installation

Preferable way to install `imctools` is via official PyPI registry. Please define package version explicitly in order to avoid incompatibilities between v1.x and v2.x versions:
```
pip install imctools==2.1.4
```
In old IMC segmentation pipelines versions 1.x should be used!
```
pip install imctools==1.0.8
```

## Usage of version 2.x

`imctools` is often used from Jupyter as part of the pre-processing pipeline, mainly using the __converters__ wrapper functions. Please check the [following example](https://github.com/BodenmillerGroup/ImcSegmentationPipeline/blob/development/scripts/imc_preprocessing.ipynb) as a template.

Further `imctools` can be directly used as a module:

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

## Usage of version 1.x

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
