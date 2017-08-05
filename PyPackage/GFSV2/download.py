# -------------------------------------------------------------------
# - NAME:        download.py
# - AUTHOR:      Reto Stauffer
# - DATE:        2017-08-05
# -------------------------------------------------------------------
# - DESCRIPTION:
# -------------------------------------------------------------------
# - EDITORIAL:   2017-08-05, RS: Created file on thinkreto.
# -------------------------------------------------------------------
# - L@ST MODIFIED: 2017-08-05 10:39 on thinkreto
# -------------------------------------------------------------------

# Initialize logger
import logging, logging.config
log = logging.getLogger("GFSV2.download")

def download( config, date ):

   import pycurl, os, sys
   from GFSV2 import getInventory

   # Loop over parameters defined
   for param in config.data.keys():

      # Get settings for this parameter
      members = config.data[param]["members"]
      levels  = config.data[param]["levels"]

      # Define what to download
      if members:   types = config.ftp_if_members
      else:         types = config.ftp_ifnot_members

      # Downloading data
      for typ in types:

         # Define output grib file
         outfile = date.strftime(config.outfile).replace("<type>",typ).replace("<param>",param)
         # If file exists: skip
         if os.path.isfile(outfile): continue
         # Else: create directory of necessary
         outdir  = os.path.dirname(outfile)
         if not os.path.exists(outdir): os.makedirs( outdir )

         # Create the range string for curl
         log.info("Downloading inventory information data")
         inv = getInventory(config,date,param,typ,levels)
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

         # Subsetting if requested
         if config.lonsubset is not None:
            import subprocess as sub
            log.info("Subsetting -> {:s}".format(outfile))
            p = sub.Popen(["wgrib2","{:s}.tmp".format(outfile),\
                           "-small_grib",config.lonsubset,config.latsubset,outfile],
                           stdout=sub.PIPE,stderr=sub.PIPE)
            out,err = p.communicate()
            # Remove temporary file (global data set)
            if os.path.isfile("{:s}.tmp".format(outfile)):
               os.remove("{:s}.tmp".format(outfile))
         # Else simply move
         else:
            os.rename("{:s}.tmp".format(outfile),outfile)



