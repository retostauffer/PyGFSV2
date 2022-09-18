# -------------------------------------------------------------------
# - NAME:        download.py
# - AUTHOR:      Reto Stauffer
# - DATE:        2022-09-18
# -------------------------------------------------------------------
# - DESCRIPTION: Main functions to download the data sets.
# -------------------------------------------------------------------

# Initialize logger
import logging, logging.config
log = logging.getLogger("GFSV2.download")

# -------------------------------------------------------------------
# Function for downloading reforecast data
# -------------------------------------------------------------------
def download(config, date):
   """download(config, date)

   Params
   ------
   config : GFSV2.readConfig.readConfig
        Object as returned by the readConfig() function of this package.
   date : datetime.datetime
        Specifies the date for which the data should be downloaded.

   Return
   ------
   No return, fails if anything goes wrong.
   """

   import pycurl, os, sys, time
   from datetime import datetime as dt
   from GFSV2 import getInventory
   from GFSV2.readConfig import readConfig

   assert isinstance(config, readConfig), TypeError("argument 'config' of must be GFSV2.readConfig.readConfig")
   assert isinstance(date, dt), TypeError("argument 'date' must be of type 'datetime.datetime'")

   # Openftp logfile if set
   if config.curl_logfile:
      curllog = open(config.curl_logfile, "a")
   else: curllog = None

   # Loop over parameters defined
   for param in config.data.keys():

      # Get settings for this parameter
      members = config.data[param]["members"]
      levels  = config.data[param]["levels"]

      # Define what to download
      if config.version == 2:
        if members:   types = config.ftp_if_members
        else:         types = config.ftp_ifnot_members
      elif config.version == 12:
        types = config.s3_members
      # Just in case ...
      else:
        raise NotImplementedError(f"No implementation for handling GFS version {config.version}")

      # Downloading data
      for typ in types:

         # Define output grib file
         outfile = date.strftime(config.outfile).replace("<type>",typ).replace("<param>",param).replace("<version>", f"{config.version:d}")

         # If file exists: skip
         if os.path.isfile(outfile): continue

         # Else: create directory of necessary
         outdir  = os.path.dirname(outfile)
         if not os.path.exists(outdir): os.makedirs(outdir)

         # Create the range string for curl
         log.info("Downloading inventory information data")
         inv = getInventory(config, date, param, typ, levels)
         if len(inv.entries) == 0:
            log.info("Inventory empty, skip this file")
            continue

         # Loopingg over all inventory entries to set up curl calls
         curlrange = {}
         for rec in inv.entries:
            if not rec.bit_end == "END":
               tmp = f"{rec.bit_start:d}-{rec.bit_end:d}"
            else:
               tmp = f"{rec.bit_start:d}-"
            if not rec.gribfile in curlrange:
                curlrange[rec.gribfile] = []
            curlrange[rec.gribfile].append(tmp)

         # 'curlrange' may now have one or multiple entries if
         # we have to fetch data from multiple grib files (might
         # be the case when using version = 12 and fetching data
         # for forecast steps in the range of Days:1-10 but also
         # at the same time for steps in the range of Days:10-16).
         # Thus, loop, download, store.

         # Open binary file connection (temporary file)
         fp = open("{:s}.tmp".format(outfile), "wb")

         # Setting curl options
         timer = dt.now()
         success = True
         c = pycurl.Curl()
         c.setopt(pycurl.WRITEDATA, fp)
         c.setopt(c.NOPROGRESS, 0)

         # Looping over curlrange, start downloading
         for grb,bitrange in curlrange.items():
            retries_left = config.curl_retries # resetting retries
            c.setopt(pycurl.URL, grb)
            log.info(f"Downloading field(s) from {grb}")

            # Download with retries if set
            while retries_left >= 0:
               log.info("Retries left: {:d}".format(retries_left))
               try:
                  if config.curl_timeout:
                     log.info("Curl timeout is {:d}".format(config.curl_timeout))
                     c.setopt(pycurl.CONNECTTIMEOUT, config.curl_timeout)
                  c.setopt(pycurl.FOLLOWLOCATION, 0)
                  log.info("Downloading -> {:s}.tmp".format(outfile))
                  for i in range(0, len(bitrange)):
                     c.setopt(c.RANGE, bitrange[i])
                     c.perform()
                  if curllog: 
                     now    = dt.now()
                     nowstr = now.strftime("%Y-%m-%d %H:%M:%S")
                     curllog.write(" {:s}; {:6d}; {:16s}; {:s}\n".format( nowstr,
                        int((now-timer).seconds),"success",outfile))
                  break
               except Exception as e:
                  log.error("Problems with download")
                  log.error(e)
                  retries_left -= 1
                  if curllog:
                     now    = dt.now()
                     nowstr = now.strftime("%Y-%m-%d %H:%M:%S")
                     curllog.write(" {:s}; {:6d}; {:16s}; {:s}\n".format(nowstr,
                        int((now-timer).seconds), "error-{:d}".format(e[0]),outfile))
                  if config.curl_sleeptime:
                     log.info("Sleeping {:.0f} seconds and retry download".format(config.curl_sleeptime))
                     time.sleep(config.curl_sleeptime)
                  success = False

         # Only if download was successful:
         fp.close()
         if success:
            log.debug(f"Finished downloading, moving {outfile}.tmp to {outfile}")
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


