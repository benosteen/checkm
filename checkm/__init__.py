#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Checkm
======

Implementation of the Checkm specifications at http://www.cdlib.org/inside/diglib/checkm/checkmspec.html

NOTICE
======

The Checkm specification on which this implementation is based is (c) 2009 UC Regents.

This implementation is released under the Apache licence

checkm - cli script
===================

Usage: checkm [options] command filenames

Commands:

checkm write [checkm filename (default:checkm.txt) [filepath (default='.')]]
    - writes a checkm manifest file to disc for the files in the given filepath. 
      Use -r to include all files under a given path in a single manifest.
      
checkm print [filepath (default='.')]
    - As for 'write', but will print the manifest to the screen.
      
checkm multi [checkm filename (default:checkm.txt) [filepath (default='.')]]
    - writes a checkm manifest file to disc for the files in the given filepath, recursively creating a manifest file within each subdirectory and using the '@' designation in the parent checkm files above it.
      
checkm check [checkm filename (default:checkm.txt)]
    - checks the given checkm manifest against the files on disc.
      Use -m to recursively scan through any multilevel checkm files it finds in this manifest as well.

checkm remove_multi [checkm filename (default:checkm.txt)]
    - scans through the checkm file, recursively gathering a list of all included checkm manifests, returning the list of files.
      Use the option '-f' or '--force' to cause the tool to try to delete these checkm files.

checkm - tool to create, check and remove checkm manifests

Options:
  -h, --help            show this help message and exit
  -a ALG, --algorithm=ALG
                        Algorithm to use to hash files
  -v, --verbose         Log information to stdin as it goes
  -r, --recursive       Recursively scan through child directories
  -m, --multi           Recursively scan through @Checkm manifests as well
  -f, --force           Required when recursively deleting multilevel checkm
                        files - if not added, the command will lsit the files
                        it would've deleted

bagitmanifest - cli script
==========================

Usage: bagitmanifest [options] command filenames

Commands:

bagitmanifest write [bagit manifest filename (default:manifest-md5.txt) [filepath (default='.')]]
    - writes a bagit manifest file to disc for the files in the given filepath. 
      Use -r to include all files under a given path in a single manifest.
      
bagitmanifest print [filepath (default='.')]
    - As for 'write', but will print the manifest to the screen.
      
bagitmanifest check [bagit manifest filename (default:manifest-md5.txt)]
    - checks the given bagit manifest against the files on disc.


Options:
  -h, --help            show this help message and exit
  -a ALG, --algorithm=ALG
                        Algorithm to use to hash files
  -v, --verbose         Log information to stdin as it goes
  -r, --recursive       Recursively scan through child directories
  -d DELIMITER, --delimiter=DELIMITER
                        State the delimiter to use to separate checksum from
                        filepath


API documentation - TODO!
"""

__version__ = "0.2.7"

from checkm import *
