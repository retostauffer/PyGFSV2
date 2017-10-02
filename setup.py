# -------------------------------------------------------------------
# - NAME:        setup.py
# - AUTHOR:      Reto Stauffer
# - DATE:        2017-02-05
# -------------------------------------------------------------------
# - DESCRIPTION: Installer for the GFSV2 python package.
# -------------------------------------------------------------------
# - EDITORIAL:   2017-02-05, RS: Created file on thinkreto.
# -------------------------------------------------------------------
# - L@ST MODIFIED: 2017-10-02 15:25 on thinkreto
# -------------------------------------------------------------------
from setuptools import setup

setup(name='GFSV2',     # This is the package name
      version='1.0-0',            # Current package version, what else
      description='GFS reforecast version 2 downloader',
      long_description='No long description necessary',
      classifiers=[
        #'Development Status :: 3 - Alpha',
        'Development Status :: 4 - Beta',
        'Closed source',
        'Programming Language :: Python :: 2.7',
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
               'bin/GFSV2_get'],
      include_package_data=True,
      czip_safe=False)

