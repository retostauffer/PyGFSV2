
# GFS Reforecast V2 Grib File Downloader

This is a small python package to download and subset
GFS reforecast grib files. The script allows to:

* Specify steps
* Specify variables
* Specify time period (and for one specific month if required)

The data will be downloaded using ``pycurl`` which has to be installed.
After downloading ``wgrib2 --small-grib`` is used to perform the spatial
subsetting. Please have a look into the config file for more information.


