# -------------------------------------------------------------------
# - NAME:        getInventory.py
# - AUTHOR:      Reto Stauffer
# - DATE:        2017-08-04
# -------------------------------------------------------------------
# - DESCRIPTION:
# -------------------------------------------------------------------
# - EDITORIAL:   2017-08-04, RS: Created file on thinkreto.
# -------------------------------------------------------------------
# - L@ST MODIFIED: 2020-06-05 11:03 on marvin
# -------------------------------------------------------------------

# Initialize logger
import logging, logging.config
log = logging.getLogger("GFSV2.getInventory")

class inventry:
   """Helper object to store inventory data.
   Each inventory object represents one message or one line
   in the inventory file. Extract required information.

   Params
   ------
   gribfile : str
        URL of the file which contains the content specified by 'line'.
   line : str
        String read from the inventory file.

   Return
   ------
   No return, saves information internally.
   """

   # ----------------------------------------------------------------
   # ----------------------------------------------------------------
   def __init__(self, gribfile, line):

      assert isinstance(gribfile, str), TypeError("Argument 'gribfile' must be string")
      assert isinstance(line, str), TypeError("Argument 'line' must be string")

      # Matching line
      import re
      mtch = re.match("^[0-9]+:([0-9]+):d=([0-9]+):([^:]*):([^:]*):(anl|[0-9-]+).*$",line)

      # Extract information
      self.gribfile  = gribfile
      self.bit_start = int(mtch.group(1)) 
      self.bit_end   = None
      self.date      = int(mtch.group(2))
      self.param     = mtch.group(3)

      # Contains level information
      self.desc      = mtch.group(4)
      lv = re.match("^([0-9]+)\smb$",self.desc)
      if lv:
         self.level = int(lv.group(1))
      else:
         self.level = None

      # Convert step. If step range: end of stpe is used
      self.step      = mtch.group(5)
      if re.match("^[0-9]+-[0-9]+$",self.step):
         self.step = int(self.step.split("-")[1])
      elif re.match("^[0-9]+$",self.step):
         self.step = int(self.step)
      elif re.match("^anl$",self.step):
         self.step = 0
      else:
         log.error("Cannot decode \"{:s}\"".format(self.step))
         sys.exit(9)

   # ----------------------------------------------------------------
   # Devel method
   # ----------------------------------------------------------------
   def show(self):
      from os.path import basename

      if self.level == None:
         lev = "sfc"
      else:
         lev = "{:d}".format(self.level)

      if not self.bit_end == "END":
         log.info(f"   INV {self.param:10s} {lev:5s}mb {self.step:3d}  {self.bit_start:10d}-{self.bit_end:10d}  in  {self.gribfile}")
      else:
         log.info(f"   INV {self.param:10s} {lev:5s}mb {self.step:3d}  {self.bit_start:10d}-   END  in  {self.gribfile}")

class getInventory:
   """This function downloads the inventory (.inv) file from the
   ftp server and parses the information. This is used to partially
   download the grib2 files on the ftp server rather than downloading
   the whole grib file.

   Params
   ------
   config : GFSV2.readConfig.readConfig
        Object as returned by the readConfig function.
   date : datetime.datetime
        Object of class datetime.datetime.
   param : str
        Name of the parameter to be downloaded.
   typ : str
        Type of the grib file which has to be downloaded.
   level : None or list
        Either None or a list with one or more integers to specify
        the pressure levels for pressure level variables.

   Return
   ------
   getInventory : Returns an object of type @ref getInventory.
   """

   def __init__(self, config, date, param, typ, levels):
      import sys
      import os
      import urllib
      from datetime import datetime as dt
      from GFSV2.readConfig import readConfig

      assert isinstance(config, readConfig), TypeError("Argument 'config' must be of type GFSV2.readConfig.readConfig")
      assert isinstance(date, dt), TypeError("Argument 'date' must be of type datetime.datetime")
      assert isinstance(param, str), TypeError("Argument 'param' must be string")
      assert isinstance(typ, str), TypeError("Argument 'typ' must be string")
      assert isinstance(levels, (type(None), list)), TypeError("Argument 'level' must be None or list")

      if config.version == 2:
          inv = [date.strftime("{:s}/{:s}".format(config.ftp_baseurl, config.ftp_filename))]
          inv_postfix = "inv"
      elif config.version == 12:
          inv = [date.strftime("{:s}/{:s}".format(config.s3_baseurl, config.s3_filename)),
                 date.strftime("{:s}/{:s}".format(config.s3_baseurl, config.s3_filename))]
          inv[0] = inv[0].replace("<days>", "Days:1-10")
          inv[1] = inv[1].replace("<days>", "Days:10-16")
          inv_postfix = "idx"
      else:
          raise NotImplementedError(f"No implementation for handling GFS version {config.version}")

      inv = [x.replace("<type>",typ).replace("<param>",param) for x in inv]
      self.gribfile = inv
      self.invfile  = [f"{x}.{inv_postfix}" for x in inv]

      log.debug(f"Reading inventory files {', '.join(self.invfile)}")

      # List to store elements needed
      self.entries = []

      # Reading inventory file(s). In case of GFS reforecast version 12
      # there are two separate files, one for Days:1-10 and one for Days:10-16
      for i in range(len(self.invfile)):

        try:
           from urllib.request import urlopen
           uid = urlopen(self.invfile[i])
           content = [x.decode("UTF-8").replace("\\n", "") for x in uid.readlines()]
           uid.close()
        except Exception as e:
           if hasattr(e, "reason"):
              log.error(f"Problems reading {url}, reason: \"{e.reason}\"")
           else:
              log.error(e)
              log.error(f"Return code:                     ({e.strerror}:{e.errno})")
           log.error("Could not download inventory file! Skip this.")
           content = None

        # If we have got content
        if not content == None:
           entries = []
           for line in content:
              if len(line.strip()) == 0: continue
              entries.append(inventry(self.gribfile[i], line))

           # Each inventry only contains the bit where the message
           # starts, not the bit where the message ends. Save "bit where the
           # next message starts - 1" to each of them to specify the range
           for i in range(len(entries) -1, -1, -1):
              if i == (len(entries) - 1):
                 entries[i].bit_end = "END" # go to the end
              else:
                 entries[i].bit_end = entries[i+1].bit_start - 1

           # Drop the steps we dont need!
           for rec in entries:
              if levels is None:
                 # If no step-subset is defined: append
                 if config.steps is None:
                    self.entries.append(rec)
                 # Else only append if step matches user specification
                 elif rec.step in config.steps:
                    self.entries.append(rec)
              else:
                 # If no step-subset is defined: append
                 if rec.level in levels and config.steps is None:
                    self.entries.append(rec)
                 # Else only append if step matches user specification
                 elif rec.level in levels and rec.step in config.steps:
                    self.entries.append(rec)

      # Show entries/fields to be downloaded
      for rec in self.entries: rec.show()












