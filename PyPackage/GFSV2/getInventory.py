# -------------------------------------------------------------------
# - NAME:        getInventory.py
# - AUTHOR:      Reto Stauffer
# - DATE:        2017-08-04
# -------------------------------------------------------------------
# - DESCRIPTION:
# -------------------------------------------------------------------
# - EDITORIAL:   2017-08-04, RS: Created file on thinkreto.
# -------------------------------------------------------------------
# - L@ST MODIFIED: 2017-08-13 22:24 on pc31-c707
# -------------------------------------------------------------------

# Initialize logger
import logging, logging.config
log = logging.getLogger("GFSV2.getInventory")

class inventry( object ):
   """!Helper object to store inventory data.
   Each inventory object represents one message or one line
   in the inventory file. Extract required information.
   @param line. String, line out of the inventory file.
   @return No return, saves information internally."""

   # ----------------------------------------------------------------
   # ----------------------------------------------------------------
   def __init__( self, line ):
      import re, sys

      # Matching line
      mtch = re.match("^[0-9]+:([0-9]+):d=([0-9]+):([^:]*):([^:]*):(anl|[0-9-]+).*$",line)

      # Extract information
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
      if self.level == None:
         lev = "sfc"
      else:
         lev = "{:d}".format(self.level)
      if not self.bit_end == "END":
         log.info("   INV {:10s} {:5s}mb {:3d}  {:10d}-{:10d}".format(self.param,lev,
                     self.step, self.bit_start,self.bit_end))
      else:
         log.info("   INV {:10s} {:5s}mb {:3d}  {:10d}-   END".format(self.param,lev,
                     self.step, self.bit_start))

class getInventory( object ):
   """!This function downloads the inventory (.inv) file from the
   ftp server and parses the information. This is used to partially
   download the grib2 files on the ftp server rather than downloading
   the whole grib file.
   @param config. Object of class @ref readConfig.
   @param date. Object of class datetime (UTC).
   @param param. String, name of the parameter to download.
   @param typ. String, typ of the grib file which has to be downloaded.
   @param level. Either NULL or a list with one or more integers to specify
      the pressure levels for pressure level variables.
   @return Returns an object of type @ref getInventory."""

   def __init__( self, config, date, param, typ, levels ):
      import sys, os, urllib

      inv = date.strftime(os.path.join(config.ftp_baseurl,config.ftp_filename))
      inv = inv.replace("<type>",typ).replace("<param>",param)
      self.gribfile = "{:s}".format(inv)
      self.invfile  = "{:s}.inv".format(inv)
      log.debug("Reading {:s}".format(self.invfile))

      try:
         uid = urllib.urlopen(self.invfile)
         content = "".join(uid.readlines()).split("\n")
         uid.close()
      except Exception as e:
         err = e.strerror.errno
         log.error( e )
         log.error("Return code:                     {:s}\n".format(err))
         log.error("Could not download inventory file! Skip this.")
         content = None

      # If we have got content
      self.entries = []
      if not content == None:
         entries = []
         for line in content:
            if len(line.strip())==0: continue
            entries.append( inventry(line) )

         # Each inventry only contains the bit where the message
         # starts, not the bit where the message ends. Save "bit where the
         # next message starts - 1" to each of them to specify the range
         for i in range(len(entries)-1,-1,-1):
            if i == (len(entries)-1):
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

         # Show (devel)
         for rec in self.entries: rec.show()












