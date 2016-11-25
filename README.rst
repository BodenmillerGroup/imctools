imctools
========================

This repository contains scripts to handle IMC data.

There are several usecases:

## As Imagej Plugin
If the subfolder 'imctools' is dropped into the FIJI plugin folder or linked with a system link,
the package allows to load and convert mcd files as well as correctly visualize multichannel ome.tiff in FIJI.

## To use as part of the segmentation pipline
The pipline needs the following components:
- the images in a compatible format (.ome.tiff, .txt, .mcd)
- a pannel.csv file that contains at least 2 columns:
    - the metal
    - a 0/1 column which channels to use for ilastik
- A copy of the pipline.ipynb file from the notebooks
