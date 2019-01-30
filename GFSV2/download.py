# -------------------------------------------------------------------
# - NAME:        download.py
# - AUTHOR:      Reto Stauffer
# - DATE:        2017-08-05
# -------------------------------------------------------------------
# - DESCRIPTION:
# -------------------------------------------------------------------
# - EDITORIAL:   2017-08-05, RS: Created file on thinkreto.
# -------------------------------------------------------------------
# - L@ST MODIFIED: 2019-01-30 21:16 on marvin
# -------------------------------------------------------------------

# Initialize logger
import logging, logging.config
log = logging.getLogger("GFSV2.download")

def download( config, date ):

   import pycurl, os, sys, time
   from datetime import datetime as dt
   from GFSV2 import getInventory

   # Openftp logfile if set
   if config.curl_logfile:
      curllog = open( config.curl_logfile, "a" )
   else: curllog = None

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
         timer = dt.now()
         c = pycurl.Curl()
         c.setopt(pycurl.URL,inv.gribfile)

         retries_left = config.curl_retries
         success = False
         # Download with retries if set
         while retries_left >= 0:
            log.info("Retries left: {:d}".format(retries_left))
            try:
               fp=open("{:s}.tmp".format(outfile), "wb")
               c.setopt(pycurl.WRITEDATA, fp)
               c.setopt(c.NOPROGRESS, 0)
               if config.curl_timeout:
                  log.info("Curl timeout is {:d}".format(config.curl_timeout))
                  c.setopt(pycurl.CONNECTTIMEOUT, config.curl_timeout)
               c.setopt(pycurl.FOLLOWLOCATION, 0)
               log.info("Downloading -> {:s}.tmp".format(outfile))
               for i in range(0,len(curlrange)):
                  c.setopt(c.RANGE, curlrange[i])
                  c.perform()
               if curllog: 
                  now    = dt.now()
                  nowstr = now.strftime("%Y-%m-%d %H:%M:%S")
                  curllog.write(" {:s}; {:6d}; {:16s}; {:s}\n".format( nowstr,
                     int((now-timer).seconds),"success",outfile))
               fp.close()
               success = True
               break
            except Exception as e:
               log.error("Problems with download")
               log.error(e)
               retries_left -= 1
               if curllog:
                  now    = dt.now()
                  nowstr = now.strftime("%Y-%m-%d %H:%M:%S")
                  curllog.write(" {:s}; {:6d}; {:16s}; {:s}\n".format( nowstr,
                     int((now-timer).seconds),"ftp-error-{:d}".format(e[0]),outfile))
               if config.curl_sleeptime:
                  log.info("Sleeping {:.0f} seconds and retry download".format(config.curl_sleeptime))
                  time.sleep( config.curl_sleeptime )

         # Only if download was successful:
         if success:
            # Subset if requested
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
               os.rename("{:s}.tmp".format(outfile), outfile)

         # Sleep if set
         if config.main_sleeptime:
            log.debug("Sleeping \"{:.0f}\" seconds before starting next download")
            time.sleep( config.main_sleeptime )

   # Close ftp logfile if opened beforehand
   if curllog: curllog.close()


