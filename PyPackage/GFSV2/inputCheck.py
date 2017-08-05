# -------------------------------------------------------------------
# - NAME:        inputCheck.py
# - AUTHOR:      Reto Stauffer
# - DATE:        2017-08-05
# -------------------------------------------------------------------
# - DESCRIPTION:
# -------------------------------------------------------------------
# - EDITORIAL:   2017-08-05, RS: Created file on thinkreto.
# -------------------------------------------------------------------
# - L@ST MODIFIED: 2017-08-05 10:50 on thinkreto
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
      Downloading GFS reforecast V2 grib file data from the NOAA CDC
      data servers. This script can be used to download smaller manually
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
      parser.add_argument("-m","--members",default=False,action="store_true",
            help="If True the individual members (plus control forecast) will " + \
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






