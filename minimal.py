#!/usr/bin/python
# -------------------------------------------------------------------
# - NAME:        minimal.py
# - AUTHOR:      Reto Stauffer
# - DATE:        2020-05-26
# -------------------------------------------------------------------
# - DESCRIPTION: Minimal for 'manual' download not using the
#                executables GFSV2_get and GFSV2_bulk shipped with
#                the package.
# -------------------------------------------------------------------

import logging
logging.basicConfig(format = "# %(levelname)s %(message)s", level = logging.DEBUG)
log = logging.getLogger()

# -------------------------------------------------------------------
# Main part of the script
# -------------------------------------------------------------------
if __name__ == "__main__":

   # ----------------------------------------------------------------
   # Read config file now
   # ----------------------------------------------------------------
   import datetime as dt
   from GFSV2 import *

   # Read default config file. If no in put is set, the package
   # default config file (config/default.conf) will be used.
   config = readConfig()

   # Define parameters to download; dictionary.
   # - dict key:  Parameter short name as in the grib files.
   # - 'members': Boolean. If True, all members will be downloaded,
   #              else only the ensemble mean and standard deviation are processed.
   # - 'levels':  None for surface variables, or a list of pressure levels.
   config.data  = {"pres_msl": {"members": False, "levels": None},
                   "tmp_pres": {"members": True,  "levels": [700, 900]}}

   # Forecast steps to download. List of integers.
   config.steps = [6, 12]

   # Define three dates. Will be processed sequentially.
   # Needs to be a list with dt.date or dt.datetime objects.
   dates = ["2000-01-01", "2000-01-02", "2000-01-03"]
   dates = [dt.datetime.strptime(x, "%Y-%m-%d") for x in dates]

   for date in dates:

      # Proccessing
      log.info("Processing date {:s}".format(date.strftime("%Y-%m-%d %HZ")))

      download(config, date)

