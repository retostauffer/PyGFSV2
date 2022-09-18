
# Version 2.0-0

* Requires python version `3.6+`
* Adding support to download GFS reforecast version 12 (via S3)
* Still allows to download GFS reforecast version 2 (deprecated)
* Old config files shoudl still work (default to GFS version 2);
  need to be adjusted to allow to download the new version 2 datat set.
* If using `GFSV2_bulk` with an existing config file -> defaults to version 2 (backwards compatability).
* If using `GFSV2_get` -> defaults to version 2 (backwards compatability).
* `GFSV2_get --version 12` -> allows to download version 12 data.
* Calling `GFSV2_defaultconfig` gives you a template for a config file using version 12.

# Version 1.1-2

* Fixed a but occurring on windows (back slash instead of forward slash in URL)

# Version 0.1-3

To try go get around getting blacklisted several options have been
implemented, such as `[curl]` retry/wait/timeout options and an
overall `[main] sleeptime` option. See [README.md](README.md) for
some more information.

* Added `[curl]` options (optional).
* Added `[main] sleeptime` option (optional).

* If `[curl] logfile` is set the downloader drops some messages containing
   date/time, execution time of the pycurl call in seconds, a message,
   name of the outut file.
