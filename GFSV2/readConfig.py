# -------------------------------------------------------------------
# - NAME:        readConfig.py
# - AUTHOR:      Reto Stauffer
# - DATE:        2017-08-04
# -------------------------------------------------------------------
# - DESCRIPTION: Reads the config file
# -------------------------------------------------------------------
# - EDITORIAL:   2017-08-04, RS: Created file on thinkreto.
# -------------------------------------------------------------------
# - L@ST MODIFIED: 2019-01-30 21:01 on marvin
# -------------------------------------------------------------------

# Initialize logger
import logging, logging.config
log = logging.getLogger("GFSV2.readConfig")


class readConfig:

   # ----------------------------------------------------------------
   # Init function
   # ----------------------------------------------------------------
   def __init__(self, file = None, force_version = None):
      """readConfig(file)

      Params
      ------
      file : str
        Name of the config file to be read.
      force_version : None or int
        Kept to ensure backwards compatability. If set None the version
        is extracted from the config file and set to 'version = 2' if the
        config file does not contain a config specification. Can be used
        to overrule this.

      Return
      ------
      No return, initializes an object of class readConfig.
      """

      # Used to keep backwards compatability with existing
      # config files not having the "version = 2" flag in there.
      assert isinstance(force_version, (type(None), int)), TypeError("Argument force_version must be None or integer")
      if force_version:
          assert force_version in [2, 12], ValueError("Argument force_version must be '2' or '12' if set")

      # If input file is None: Use package internal default config
      # which contains ftp definition and default output path and stuff.
      if file is None:
         import pkg_resources
         file = pkg_resources.resource_filename(__package__, f"config/default.conf")
         log.debug("Loading default config file from package source.")

      import os
      import sys
      import re
      from configparser import RawConfigParser as ConfigParser

      assert os.path.isfile(file), FileNotFoundError(f"Required config file \"{file}\" not found inside installed package.")

      # Read the config file
      log.info(f"Reading config file {file}")
      CNF = ConfigParser(); CNF.read(file)
      config                 = {}

      # If called with argument force_version this is the version we are going with.
      # Else we try to read it from the config file itself.
      if force_version:
          self.version = force_version
      else:
          # GFS version. If not set we assume it is version 2 for backwards compatability.
          try:
             self.version        = CNF.getint("main", "version")
          except:
             self.version        = 2
          if not self.version in [2, 12]:
              raise ValueError("Argument 'version' must be either 2, or 12.")

      # Reading FTP config (used for GFS v2; depricated)
      if self.version == 2:
        self.ftp_if_members    = []
        self.ftp_ifnot_members = []
        try:
           self.ftp_baseurl  = CNF.get("ftp","baseurl")
           self.ftp_filename = CNF.get("ftp","filename")
           for rec in CNF.get("ftp","if_members").split(","):
              self.ftp_if_members.append( rec.strip() )
           for rec in CNF.get("ftp","ifnot_members").split(","):
              self.ftp_ifnot_members.append( rec.strip() )
        except Exception as e:
           log.error("Problems reading ftp config")
           raise Exception(e)

      # Reading Amazon S3 bucket config (used for GFS v12)
      else:
        self.s3_members    = []
        try:
           self.s3_baseurl  = CNF.get("s3", "baseurl")
           self.s3_filename = CNF.get("s3", "filename")
           for rec in CNF.get("s3", "members").split(","):
              self.s3_members.append( rec.strip() )
        except Exception as e:
           log.error("Problems reading s3 config")
           raise Exception(e)

      # Check if curl logfile is set (logging ftp return codes)
      try:
         self.curl_logfile    = CNF.get("curl","logfile")
      except:
         self.curl_logfile   = None
      try:
         self.curl_timeout    = CNF.getint("curl","timeout")
      except:
         self.curl_timeout   = None
      try:
         self.curl_retries    = CNF.getint("curl","retries")
      except:
         self.curl_retries   = 0
      try:
         self.curl_sleeptime  = CNF.getfloat("curl","sleeptime")
      except:
         self.curl_sleeptime = 0

      # Date range
      from datetime import datetime as dt
      try:
         self.main_from = dt.strptime(CNF.get("main","from"),"%Y-%m-%d")
         self.main_to   = dt.strptime(CNF.get("main","to"),"%Y-%m-%d")
      except:
         self.main_from = None; self.main_to = None
      try:
         self.main_only = CNF.getint("main","only")
      except:
         self.main_only = None
      if not self.main_only is None:
         if self.main_only < 1 or self.main_only > 12:
            sys.exit("Misspecification of [main][only] in config file.")

      try:
         self.main_sleeptime = CNF.getfloat("main","sleeptime")
      except:
         self.main_sleeptime = None

      # Areal subset for wgrib2 --small-grib
      try:
         self._lonmin_ = CNF.getfloat("main","lonmin")
         self._lonmax_ = CNF.getfloat("main","lonmax")
         self._latmin_ = CNF.getfloat("main","latmin")
         self._latmax_ = CNF.getfloat("main","latmax")
      except:
         self._lonmin_  = None;    self._lonmax_  = None;
         self._latmin_  = None;    self._latmax_  = None;
         self.lonsubset = None;    self.latsubset = None;
      if self._lonmin_ is not None:
         if self._lonmin_ >= self._lonmax_ or self._latmin_ >= self._latmax_:
            log.error("lonmin/lonmax/latmin/latmax wrong! Please check your config file")
            sys.exit()
         self.lonsubset = "{:.2f}:{:.2f}".format(self._lonmin_,self._lonmax_)
         self.latsubset = "{:.2f}:{:.2f}".format(self._latmin_,self._latmax_)

      # Output file name
      try:
         self.outfile = CNF.get("main","outfile")
      except Exception as e:
         log.error(e); sys.exit(9)

      # Steps to download
      self.steps = []
      try:
         for rec in CNF.get("main","steps").split(","):
            self.steps.append( int(rec) )
      except:
         self.steps = None


      # Reading parameter or variable config
      secs = CNF.sections()
      self.data = {}
      for sec in secs:
         mtch = re.match("^data\s+(\w+)$",sec)
         if not mtch: continue
         # Only available for GFS reforecat version 2
         if self.version == 2:
            try:
               mem = CNF.getboolean(sec, "members")
            except Exception as e:
               log.error(e); sys.exit(9)
         else:
             mem = True
         # Level configuration
         try:
            lev = []
            for rec in CNF.get(sec,"levels").split(","): lev.append(int(rec))
         except:
            lev = None
         self.data[ mtch.group(1) ] = {"members": mem, "levels": lev}

      # All fine
      log.info("Config file read, return.")

   # ----------------------------------------------------------------
   # ----------------------------------------------------------------
   def show( self ):
      """!Helper function. Prints content of the config class to console."""
      log.info("- {:20s} {:s}".format("Reforecast version:", str(self.version)))
      log.info("- {:20s} {:s}".format("Output files:",       str(self.outfile)))
      log.info("- {:20s} {:s}".format("Date range from:",    str(self.main_from)))
      log.info("- {:20s} {:s}".format("Date range to:",      str(self.main_to)))
      log.info("- {:20s} {:s}".format("Only month nr:",      str(self.main_only)))
      log.info("- {:20s} {:s}".format("Forecast steps:",     str(self.steps)))
      log.info("- {:20s} {:s}".format("Subset lonmin:",      str(self._lonmin_)))
      log.info("- {:20s} {:s}".format("Subset lonmax:",      str(self._lonmax_)))
      log.info("- {:20s} {:s}".format("Subset latmin:",      str(self._latmin_)))
      log.info("- {:20s} {:s}".format("Subset latmax:",      str(self._latmax_)))
      if self.version == 2:
          log.info("- {:20s} {:s}".format("FTP base url:",       str(self.ftp_baseurl)))
          log.info("- {:20s} {:s}".format("FTP file names:",     str(self.ftp_filename)))
          log.info("- {:20s} {:s}".format("FTP if members:",     str(self.ftp_if_members)))
          log.info("- {:20s} {:s}".format("FTP if not members:", str(self.ftp_ifnot_members)))
      else:
          log.info("- {:20s} {:s}".format("S3 base url:",        str(self.s3_baseurl)))
          log.info("- {:20s} {:s}".format("S3 file names:",      str(self.s3_filename)))
          log.info("- {:20s} {:s}".format("S3 members:",         str(self.s3_members)))
      log.info("- {:20s} {:d}".format("[data] parameters defined:",len(self.data)))
      for k,settings in self.data.items(): log.info(f"  {k} {settings=}")


