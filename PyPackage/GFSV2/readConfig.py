# -------------------------------------------------------------------
# - NAME:        readConfig.py
# - AUTHOR:      Reto Stauffer
# - DATE:        2017-08-04
# -------------------------------------------------------------------
# - DESCRIPTION: Reads the config file
# -------------------------------------------------------------------
# - EDITORIAL:   2017-08-04, RS: Created file on thinkreto.
# -------------------------------------------------------------------
# - L@ST MODIFIED: 2017-08-05 10:06 on thinkreto
# -------------------------------------------------------------------

# Initialize logger
import logging, logging.config
log = logging.getLogger("GFSV2.readConfig")


class readConfig( object ):
   """!Class which reads and stores the configuration from a config
   file.
   @param file. Name of the config file."""

   # ----------------------------------------------------------------
   # Init function
   # ----------------------------------------------------------------
   def __init__( self, file=None ):

      # If input file is None: Use package internal default config
      # which contains ftp definition and default output path and stuff.
      if file is None:
         import pkg_resources
         file = pkg_resources.resource_filename(__package__, 'config/default.conf')
         log.debug("Loading default config file from package source.")

      import os, sys, re
      if not os.path.isfile(file): sys.exit("Config fil \"{:s}\" missing".format(file))

      # Import ConfigParser, read config
      from ConfigParser import ConfigParser
      CNF = ConfigParser(); CNF.read( file )
      config = {}
      self.ftp_if_members = []; self.ftp_ifnot_members = []
      try:
         self.ftp_baseurl  = CNF.get("ftp","baseurl")
         self.ftp_filename = CNF.get("ftp","filename")
         for rec in CNF.get("ftp","if_members").split(","):
            self.ftp_if_members.append( rec.strip() )
         for rec in CNF.get("ftp","ifnot_members").split(","):
            self.ftp_ifnot_members.append( rec.strip() )
      except Exception as e:
         log.error("Problems reading ftp config")
         log.error(e); sys.exit(9)

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
         try:
            mem = CNF.getboolean(sec,"members")
         except Exception as e:
            log.error(e); sys.exit(9)
         try:
            lev = []
            for rec in CNF.get(sec,"levels").split(","): lev.append( int(rec) )
         except:
            lev = None
         self.data[ mtch.group(1) ] = {"members":mem,"levels":lev}
      
      # All fine
      log.info("Config file read, return.")

   # ----------------------------------------------------------------
   # ----------------------------------------------------------------
   def show( self ):
      """!Helper function. Prints content of the config class to console."""
      log.info("- {:20s} {:s}".format("Output files:",       str(self.outfile)))
      log.info("- {:20s} {:s}".format("Date range from:",    str(self.main_from)))
      log.info("- {:20s} {:s}".format("Date range to:",      str(self.main_to)))
      log.info("- {:20s} {:s}".format("Only month nr:",      str(self.main_only)))
      log.info("- {:20s} {:s}".format("Forecast steps:",     str(self.steps)))
      log.info("- {:20s} {:s}".format("Subset lonmin:",      str(self._lonmin_)))
      log.info("- {:20s} {:s}".format("Subset lonmax:",      str(self._lonmax_)))
      log.info("- {:20s} {:s}".format("Subset latmin:",      str(self._latmin_)))
      log.info("- {:20s} {:s}".format("Subset latmax:",      str(self._latmax_)))
      log.info("- {:20s} {:s}".format("FTP base url:",       str(self.ftp_baseurl)))
      log.info("- {:20s} {:s}".format("FTP file names:",     str(self.ftp_filename)))
      log.info("- {:20s} {:s}".format("FTP if members:",     str(self.ftp_if_members)))
      log.info("- {:20s} {:s}".format("FTP if not members:", str(self.ftp_ifnot_members)))
      log.info("- {:20s} {:d}".format("[data] parameters defined:",len(self.data)))


