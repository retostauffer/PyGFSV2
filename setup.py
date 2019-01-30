# -------------------------------------------------------------------
# - NAME:        setup.py
# - AUTHOR:      Reto Stauffer
# - DATE:        2017-02-05
# -------------------------------------------------------------------
# - DESCRIPTION: Installer for the GFSV2 python package.
# -------------------------------------------------------------------
# - EDITORIAL:   2017-02-05, RS: Created file on thinkreto.
# -------------------------------------------------------------------
# - L@ST MODIFIED: 2019-01-30 21:18 on marvin
# -------------------------------------------------------------------
from setuptools import setup

setup(name='GFSV2',     # This is the package name
      version='1.1-0',            # Current package version, what else
      description='GFS reforecast version 2 downloader',
      long_description='No long description necessary',
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Open Source',
        'License :: GPL2',
        'Programming Language :: Python :: 2.7/3+',
      ],
      keywords='GFS reforecast',
      url='https://git.uibk.ac.at/retos/GFSreforecastV2/',
      author='Reto Stauffer',
      author_email='reto.stauffer@uibk.ac.at',
      license='GPL-2',
      packages=['GFSV2'],
      install_requires=[
         'ConfigParser',
         'argparse',
         'pydap',
         'pycurl',
         'logging'
      ],
      scripts=['bin/GFSV2_bulk',
               'bin/GFSV2_get',
               'bin/GFSV2_defaultconfig'],
      include_package_data=True,
      czip_safe=False)

