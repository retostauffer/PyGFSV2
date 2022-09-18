# -------------------------------------------------------------------
# - NAME:        setup.py
# - AUTHOR:      Reto Stauffer
# - DATE:        2022-09-18
# -------------------------------------------------------------------
from setuptools import setup

setup(name="GFSV2",     # This is the package name
      version="2.0-0",            # Current package version, what else
      description="GFS reforecast version 2 AND version 12 downloader",
      long_description="""Small python package to simplify access to 
      NOAAs GFS reforecast ensemble data. Originally designed for GFS reforecasts
      version 2 which has been deprecated (still available) in September 2020.
      Since September 2022, this package also allows to download GFS reforecast version 12
      data. Note: For backwards compatability the default behaviour with existing config
      files and GFSV2_get is version = 2!""",
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Open Source",
        "License :: GPL2",
        "Programming Language :: Python :: 3.6+",
      ],
      keywords="GFS reforecast",
      url="https://github.com/retostauffer/GFSV2",
      author="Reto Stauffer",
      author_email="reto.stauffer@uibk.ac.at",
      license="GPL-2",
      packages=["GFSV2"],
      install_requires=[
         "ConfigParser",
         "argparse",
         "pydap",
         "pycurl"
      ],
      scripts=["bin/GFSV2_bulk",
               "bin/GFSV2_get",
               "bin/GFSV2_defaultconfig"],
      include_package_data=True,
      czip_safe=False)

