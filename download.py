# -------------------------------------------------------------------
# - NAME:        download.py
# - AUTHOR:      Reto Stauffer
# - DATE:        2017-08-04
# -------------------------------------------------------------------
# - DESCRIPTION:
# -------------------------------------------------------------------
# - EDITORIAL:   2017-08-04, RS: Created file on thinkreto.
# -------------------------------------------------------------------
# - L@ST MODIFIED: 2017-08-04 19:02 on thinkreto
# -------------------------------------------------------------------

import logging
logging.basicConfig(format="# %(levelname)s %(message)s",level=logging.DEBUG)
log = logging.getLogger()

# -------------------------------------------------------------------
# Main part of the script
# -------------------------------------------------------------------
if __name__ == "__main__":

   from GFSV2 import *

   # Read config
   log.info("Read config file")
   config = readConfig("config.conf")

   import sys, os
   import subprocess as sub
   import datetime as dt

   
   # Looping over dates
   loopdate = config.data_from
   while loopdate < config.data_to:

      # Check whether we have to download this file or not
      loopdate_mon = int(loopdate.strftime("%m"))
      if not config.data_only is None:
         if not loopdate_mon == config.data_only:
            # Increase loopdate and continue
            loopdate = loopdate + dt.timedelta(1)
            continue

      # Proccessing
      log.info("Processing date {:s}".format(loopdate.strftime("%Y-%m-%d %HZ")))

      for param,members in config.data.iteritems():
         if members:   types = config.data_if_members
         else:         types = config.data_ifnot_members

         # Downloading data
         for typ in types:

            # Define output grib file
            outfile = loopdate.strftime(config.outfile).replace("<type>",typ).replace("<param>",param)
            # If file exists: skip
            if os.path.isfile(outfile): continue
            # Else: create directory of necessary
            outdir  = os.path.dirname(outfile)
            if not os.path.exists(outdir): os.makedirs( outdir )
            
            # Create the range string for curl
            log.info("Downloading inventory information data")
            inv = getInventory(config,loopdate,param,typ)
            if len(inv.entries) == 0:
               log.info("Inventory empty, skip this file")
               continue

            # Else extracting block information
            curlrange = []
            for rec in inv.entries:
               if not rec.bit_end == "END":
                  curlrange.append("{:d}-{:d}".format(rec.bit_start,rec.bit_end))
               else:
                  curlrange.append("{:d}-".format(rec.bit_start))

            # Start downloading the file
            import pycurl
            c = pycurl.Curl()
            c.setopt(pycurl.URL,inv.gribfile)
            try:
               fp=open("{:s}.tmp".format(outfile), "wb")
               c.setopt(pycurl.WRITEDATA, fp)
               c.setopt(c.NOPROGRESS, 0)
               c.setopt(pycurl.FOLLOWLOCATION, 0)
               log.info("Downloading -> {:s}.tmp".format(outfile))
               for i in range(0,len(curlrange)):
                  c.setopt(c.RANGE, curlrange[i]) 
                  c.perform()
               fp.close()
            except Exception as e:
               log.error("Problems with download")
               log.error(e)
               continue

            # Subsetting
            log.info("Subsetting -> {:s}".format(outfile))
            p = sub.Popen(["wgrib2","{:s}.tmp".format(outfile),\
                           "-small_grib",config.lonsubset,config.latsubset,outfile],
                           stdout=sub.PIPE,stderr=sub.PIPE)
            out,err = p.communicate()

            if os.path.isfile("{:s}.tmp"): os.remove("{:s}.tmp")

      # Increase date
      loopdate = loopdate + dt.timedelta(1)




























