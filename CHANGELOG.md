
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
