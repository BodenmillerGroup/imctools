# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.4] - 2021-02-01
- Proper parsing of invalid MCD files when some acquisitions offset are outside the file's size 

## [2.1.3] - 2021-01-21
- Option to force usage of TXT files in `mcdfolder_to_imcfolder` when dealing with partially corrupted MCD files 

## [2.1.2] - 2021-01-21
- Prevent crash on corrupted MCD acquisitions in order to keep valid ones

## [2.1.1] - 2021-01-20
- Update `xtiff` package
- FIX: Wrong ROI coordinates for new Fluidigm software versions #104
- FIX: Extra 161 bytes extracted on all image buffers #102

## [2.0.1] - 2020-08-14
- Fix Path instance file name when dealing with `xtiff`

## [2.0.0] - 2020-08-12
- Initial release
