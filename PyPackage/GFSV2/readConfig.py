# -------------------------------------------------------------------
# - NAME:        readConfig.py
# - AUTHOR:      Reto Stauffer
# - DATE:        2017-08-04
# -------------------------------------------------------------------
# - DESCRIPTION: Reads the config file
# -------------------------------------------------------------------
# - EDITORIAL:   2017-08-04, RS: Created file on thinkreto.
# -------------------------------------------------------------------
# - L@ST MODIFIED: 2017-08-04 18:28 on thinkreto
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
   def __init__( self, file ):

      import os, sys, re
      if not os.path.isfile(file): sys.exit("Config fil \"{:s}\" missing".format(file))

      # Import ConfigParser, read config
      from ConfigParser import ConfigParser
      CNF = ConfigParser(); CNF.read("config.conf")
      config = {}
      try:
         self.ftp_baseurl  = CNF.get("ftp","baseurl")
         self.ftp_filename = CNF.get("ftp","filename")
      except Exception as e:
         log.error(e); sys.exit(9)

      # Date range
      from datetime import datetime as dt
      try:
         self.data_from = dt.strptime(CNF.get("data","from"),"%Y-%m-%d")
         self.data_to   = dt.strptime(CNF.get("data","to"),"%Y-%m-%d")
      except Exception as e:
         print e; sys.exit(9)
      try:
         self.data_only = CNF.getint("data","only")
      except:
         self.data_only = None
      if not self.data_only is None:
         if self.data_only < 1 or self.data_only > 12:
            sys.exit("Misspecification of [main][only] in config file.")

      # Areal subset for wgrib2 --small-grib
      try:
         self.lonmin = CNF.getfloat("data","lonmin")
         self.lonmax = CNF.getfloat("data","lonmax")
         self.latmin = CNF.getfloat("data","latmin")
         self.latmax = CNF.getfloat("data","latmax")
      except Exception as e:
         log.error(e); sys.exit(9)
      if self.lonmin >= self.lonmax or self.latmin >= self.latmax:
         log.error("lonmin/lonmax/latmin/latmax wrong! Please check your config file")
         sys.exit()
      self.lonsubset = "{:.2f}:{:.2f}".format(self.lonmin,self.lonmax)
      self.latsubset = "{:.2f}:{:.2f}".format(self.latmin,self.latmax)

      # Output file name
      try:
         self.outfile = CNF.get("data","outfile")
      except Exception as e:
         log.error(e); sys.exit(9)
      

      # Steps to download
      self.steps = []
      try:
         for rec in CNF.get("data","steps").split(","):
            self.steps.append( int(rec) )
      except Exception as e:
         log.error(e); sys.exit(9)

      # Reading type config
      self.data_if_members = []; self.data_ifnot_members = []
      try:
         for rec in CNF.get("data","if_members").split(","):
            self.data_if_members.append( rec.strip() )
         for rec in CNF.get("data","ifnot_members").split(","):
            self.data_ifnot_members.append( rec.strip() )
      except Exception as e:
         log.error(e); sys.exit(9)

      # Reading variable config
      secs = CNF.sections()
      self.data = {}
      for sec in secs:
         mtch = re.match("^data\s+(\w+)$",sec)
         if not mtch: continue
         log.info("Reading config for \"{:s}\"".format(sec))
         try:
            self.data[ mtch.group(1) ] = CNF.getboolean(sec,"members")
         except Exception as e:
            log.error(e); sys.exit(9)
      

      # All fine
      log.info("Config file read, return.")



