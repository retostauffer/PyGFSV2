

# GFS Reforecast V2/V12 Grib File Downloader

This package was originally defined to download gridded
Global Forecast System (GFS) reforecast version 2 data provided by the
National Oceanographic and Atmospheric Agencys (NOAA) Climate Data Center (CDC).

**Note:** Reforecast version 2 has been deprecated in September 2020 and is no 
longer updated (see [this note](https://psl.noaa.gov/forecasts/reforecast2/README.GEFS_Reforecast2.pdf)).
However, the data is still available as for September 2022, but users should
switch to the new [GFS reforecast version 12](https://noaa-gefs-retrospective.s3.amazonaws.com/index.html) data set available via amazon S3. Thus, the package has been modified
in September 2022 to allow for accessing the new version 12 data set.
The updated package now requires Python version `3.6` or above.

Some more details about the most recent changes can be found in the
[CHANGELOG.md](CHANGELOG.md) file.

### Backwards compatability; version 2 vs. 12

Take care: To ensure backwards compatability the default behaviour of many functions
is to download version 2 data.

* `GFSV2_get`: Uses version 2 by default. To get the new data set you must 
  provide `--version 12`.
* `GFSV2_bulk`: Falls back to version 2 if you are using an existing config file.
* `GFSV2_defaultconfig`: Returns a config template which includes `version = 12`,
  thus defaults to the new version if used.

By default (if not changed) the final grib files contain the version information
(starting with `GFSV2_` and `GFSV12_` respectively).

* Version 2: [_would need to look it up_]
* Version 12: Starts in the year 2000

# Installation

The [github](https://github.com/retostauffer/PyGFSV2]) repository contains the
small python package which should be ready for installation. You can simply
install the package by calling:

* `pip install git+https://github.com/retostauffer/PyGFSV2.git`

The `setup.py` script should automatically take care of the dependencies
except `wgrib2` which is used for subsetting (if configuration files with subset
settings are used in `GFSV2_bulk`; see below). After installation you can try
the installation (no subsetting) by calling:

* `GFSV2_get --version 2 --step 12 24 --level 700 850 --param tmp_pres --date 2005-01-01`

### Requirements

Requires the following python packages:

* Python version `3.6` or above.
* ``pycurl`` (and standard libs like ``datetime``, ``ConfigParser``, ``argparse``,``logging``)
* If subsetting is used (see ``GFSV2_bulk``) the ``wgrib2`` executable has to be callable
   ([see CPC wgrib2 readme](http://www.cpc.ncep.noaa.gov/products/wesley/wgrib2/)).

# Usage

The **GFSV2** python package provides a set of functions and three executables
called `GFSV2_defaultconfig`, `GFSV2_get` and `GFSV2_bulk` for convenient data processing.


### `GFSV2_get` executable

The ``GFSV2_get`` executable can be used to download specific manually defined
subsets of the reforecast. This can be handy during the development/specification
process. However, if you would like to download larger amounts of data please
have a look at the ``GFSV2_bulk`` description below!

Basic usage (shows usage help):
* ``GFSV2_get`` or ``GFSV2_get -h``

There are two required input arguments to ``GFSV2_get``. One is the ``-p/--param``
input, the other one is the ``-d/--date`` input. Both can contain one or more
values. ``--param`` specifies which parameters or variables you would like to
download, ``--date`` the dates of the model initialization. A list/description
of [all available parameters can be found here](https://www.esrl.noaa.gov/psd/forecasts/reforecast2/README.GEFS_Reforecast2.pdf).
The ``--date`` arguments have to be of type ``YYYY-mm-dd``. As an example
let's download ``tmax_2m`` for January 1 2014:

* ``GFSV2_get --version 12 --param tmax_2m --date 2014-01-01``
* ``GFSV2_get -v 12 -p tmax_2m -d 2014-01-01``

In addition, a ``-s/--steps`` argument can be given. The ``steps`` are the
forecast lead times (e.g., ``24`` for the forecast 24 hours after initialization).
Several steps can be defined:

* ``GFSV2_get -v 12 -p tmax_2m -d 2014-02-01 -s 24 48``

By default only ``mean`` and ``sprd`` files (ensemble mean and ensemble spread)
will be downloaded. If the individual members and the control run are required
(``10+1``) the ``-m/--members`` flag has to be set:

* ``GFSV2_get -v 12 -p tmax_2m -d 2014-02-05 -s 24 -m``

Downloading two different parameters for two different dates, only +24h forecast:

* ``GFSV2_get -v 12 -p tmax_2m cape_sfc -d 2014-02-01 2014-02-02 -s 24

For pressure level variables (e.g, ``ugrd_pres``, ``vgrd_pres``, ``tmp_pres``,
``hgt_pres`` and ``spfh_pres``
(for GFS version 2, check out this [Table 1](https://www.esrl.noaa.gov/psd/forecasts/reforecast2/README.GEFS_Reforecast2.pdf), for GFS version 12 have a look at the
[Description_of_reforecast_data.pdf](https://noaa-gefs-retrospective.s3.amazonaws.com/Description_of_reforecast_data.pdf))
level can be given in advance to download specific levels only. Level specification
in millibars or hecto pascal. An example:

* ``GFSV2_get -v 12 -p tmp_pres -l 500 -d 2014-03-10``

**NOTE:** The download will be skipped if the output grib file already exists!
This can be crucial if you download a data set, re-specify the settings and try
to run the script again. As the file already exists (even if containing different
subset of data) the data won't be downloaded again. In this case simply delete
the local grib files in ``data/YYYY/mm`` and re-run the job.

## `GFSV2_bulk` executable

This is the bulk download version of the ``GFSV2_get`` executable explained
above. Rather than providing a set of input arguments only one argument is
allowed and required: ``-c/--config``. ``-c/--config`` is the path to a config
file. All specifications can be set in this config file. The config file allows
to specify:

* Version.
* Specific ouptut path/file name.
* Date range for which data should be downloaded (``from`` ``to``).
* Additional ``only`` flag (download data for date range if and only if the
   date is in month ``only``) .
* The ``steps`` to download.
* A spatial subset (required ``wgrib2`` installed). Data will be subsetted after 
   downloading with respect to the specification (``lonmin``, ``lonmax``, ``latmin`` and ``latmax``).
* Parameters which have to be downloaded (each one can have it's own level/members specification).

The package contains a [default.config](https://github.com/retostauffer/PyGFSV2/blob/master/GFSV2/config/default.conf) file which can be used as a starting point to write your own custom
config file to be used alongside with `GFSV2_bulk`. Simply call:

* ``GFSV2_defaultconfig > my_config_file.conf`` 

... to get the template and adjust it according to your needs.
Once finished, call:

* ``GFSV2_bulk --config your_config_file.conf``

... to start downloading the data.

