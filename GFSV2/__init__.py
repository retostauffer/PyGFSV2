 
# Default: setting time zone to UTC
import os, pkg_resources
os.environ["TZ"] = "UTC"

version = pkg_resources.require(__package__)[0].version

print """
              This is {:s} version {:s} 
""".format( __package__, version )



## Import Classes
from .readConfig         import readConfig
from .getInventory       import getInventory
from .inputCheck         import inputCheck
from .download           import download
