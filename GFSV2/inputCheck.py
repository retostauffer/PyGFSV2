# -------------------------------------------------------------------
# - NAME:        inputCheck.py
# - AUTHOR:      Reto Stauffer
# - DATE:        2022-09-18
# -------------------------------------------------------------------
# - DESCRIPTION: Parsing input arguments for console tools.
# -------------------------------------------------------------------

# Initialize logger
import logging, logging.config
log = logging.getLogger("GFSV2.inputCheck")

class inputCheck( object ):
   """!Small helper class to parse and handle input arguments to the
   scripts used in GFSV2 python package. No inputs, reads user inputs
   by using argparse."""

   # ----------------------------------------------------------------
   # ----------------------------------------------------------------
   def __init__( self ):

      helptext = """
      Downloading GFS reforecast grib file data. Originally designed
      to download GFS reforecast V2 from from the NOAA CDC data servers.

      The script has been adjusted in September 2022 to allow downloading GFS
      reforecasts version 12 via an amazon S3 bucket. The version to be
      downloaded can be specified via -v/--version (GFSV2_get) or is retrieved
      via the config file when using GFSV2_bulk, see description provided by
      GFSV2_bulk -h.

      This script can be used to download smaller manually
      specified sets of data. Please have a look at GFSV2_bulk if you
      need to download larger amounts of data. The bulk script allows for
      more detailed specifications based on a simple config file.
      """
      import argparse, sys

      parser = argparse.ArgumentParser(description=helptext)
      # Verbosity on or off (boolean)
      parser.add_argument("--verbose", action="store_true",default=False,
            help="Increase output verbosity.")
      # Parameter name, multiple are allowed
      parser.add_argument("-v", "--version", default = None, type = int,
            help="Specify the version of the GFS reforecast ensemble. " + \
                 "Either '2' or '12', defaults to '2' for backwards compatability.")
      parser.add_argument("-m","--members",default=False,action="store_true",
            help="Only available for --version 2. Version 12 will always return the individual " + \
                 "members and the control run (mean/sprd not available). " + \
                 "If True the individual members (plus control forecast) will " + \
                 "be downloaded. If False only mean/sprd will be downloaded. ")
      parser.add_argument("-l","--levels",nargs="+",type=int, default=None,
            help="Integer, levels which should be downloaded. If not set surface variables " + \
                 "will be downloaded. Input e.g., 500 700 (for 500 and 700 hPa levels.")
      parser.add_argument("-s","--steps",nargs="+",type=int, default=None, 
            help="Integer, steps for which the data should be downloaded (forecast lead time, " + \
                 "e.g., 3 6 9 12 24 48).")

      required = parser.add_argument_group('required arguments')
      required.add_argument("-p","--param",nargs="+",type=str,
            help="Name of the parameter which should be downloaded")
      required.add_argument("-d","--dates",nargs="+",type=str,
            help="Date. Format YYYY-mm-dd. Multiple dates can be given.")

      # Parse and store
      args = parser.parse_args()
      self._inputs_ = args

      # Version specification
      if not args.version:
          log.warning("-v/--version not specified, defaulting to version 2 (consider using the newer version 12 by specifying --version 12")
          args.version = 2

      # Set members to True if version is 12
      if args.version == 12 and not args.members:
          log.warning("--version 12 always uses --members True, mean/sprd not available")
          args.members = True

      # Check required inputs
      check = self._check_req_()
      if not check:
         parser.print_help()
         sys.exit(1)

      # Convert dates
      from datetime import datetime as dt
      tmp = []
      try:
         for rec in self.get("dates"): tmp.append( dt.strptime(rec,"%Y-%m-%d") )
         args.dates = tmp
      except:
         log.error("Input -d/--date: wrong format!")
         parser.print_help()
         sys.exit(1)

      # Create the dict array for the parameter/members/level options
      # as specified by the user. Will be used to overwrite config.data
      data = {}
      for rec in self.get("param"):
         data[rec] = {"members":self.get("members"),"levels":self.get("levels")}

      args.data = data

   # ----------------------------------------------------------------
   # ----------------------------------------------------------------
   def _check_req_( self ):

      if self.get("param") is None:          return False
      if self.get("dates") is None:          return False
      return True      

   # ----------------------------------------------------------------
   # ----------------------------------------------------------------
   def get( self, key ):
      """!Helps to access the parsed input arguments. If they attribute
      does not exist None will be returned.
      @param key. String with the name of the attribute.
      @return Returns whatever is on the argument 'key' if existing.
         Else None will be returned."""

      if hasattr(self._inputs_,key):
         return getattr(self._inputs_,key)
      else:
         return None






