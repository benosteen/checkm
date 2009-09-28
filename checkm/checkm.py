#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Checkm class library docs TODO


                [@]SourceFileOrURL  Alg     Digest  Length   ModTime   TargetFileOrURL
TOKEN NUMBER:    1                  2       3       4        5         6

"""

import os, sys
from stat import *

from collections import defaultdict

import hashlib

import codecs

import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger('checkm')

class DirectoryNotFound(Exception):
    """The directory was not found, or is not accessible."""
    def __init__(self, *arg, **kw):
        self.context = (arg, kw)
    def __repr__(self):
        return self.context.__str__()

class CheckmReporter(object):
    COLUMN_NAMES = [u'# [@]SourceFileOrURL',u'Alg',u'Digest',u'Length',u'ModTime']
    def __init__(self):
        self.scanner = CheckmScanner()

    def _get_max_len(self, report):
        cols = defaultdict(lambda : 0)
        for line in report:
            for index in xrange(len(line)):
                if len(line[index])>cols[index]:
                    cols[index] = len(line[index])
        return cols

    def _space_line(self, line, col_maxes):
        spaced_line = []
        for index in xrange(len(line)):
            spaced_line.append(line[index])
            spaces = col_maxes[index]-len(line[index])+4
            spaced_line.append(u" "*spaces)
        return u"".join(spaced_line)

    def create_checkm_file(self, scan_directory, algorithm, checkm_filename, recursive=False, columns=3):
        logger.info("Creating checkm file(%s) for dir(%s) with Alg:%s and columns: %s" % (checkm_filename,
                                                                                          scan_directory,
                                                                                          algorithm, columns))
        report = self.scanner.scan_directory(scan_directory, algorithm, recursive=recursive, columns=columns)
        col_maxes = self._get_max_len(report)
        with codecs.open(checkm_filename, encoding='utf-8', mode="w") as output:
            output.write("%s \n" % (self._space_line(CheckmReporter.COLUMN_NAMES[:columns], col_maxes)))
            for line in report:
                output.write("%s\n" % (self._space_line(line, col_maxes)))
            output.write("\n")

    def check_checkm_hashes(self, scan_directory, checkm_filename):
        logger.info("Checking files against %s checkm manifest" % checkm_filename)
        

class CheckmParser(object):
    def __init__(self, checkm_file=None):
        self.status = False
        if checkm_file:
            self.parse(checkm_file)

    def parse(self, checkm_file):
        if hasattr(checkm_file, read):
            return self._parse_filelike(checkm_file)
        else:
            # Assume dir path to file
            return self._parse_file_from_path(checkm_file)

    def _parse_filelike(self, fh):
        pass

class CheckmScanner(object):
    HASHTYPES = ['md5', 'sha1', 'sha224','sha256','sha384','sha512']
    def scan_local(self, directory_path, algorithm, columns=3):
        report = []
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            report.append(self.scan_path(item_path, algorithm, columns))
        return report

    def scan_tree(self, directory_path, algorithm, columns):
        report = []
        if os.path.exists(directory_path):
            for (dirpath, dirnames, filenames) in os.walk(directory_path):
                for item_path in [os.path.join(dirpath, x) for x in dirnames+filenames]:
                    report.append(self.scan_path(item_path, algorithm, columns))
            return report
        else:
            raise DirectoryNotFound(directory_path=directory_path, recursive=recursive)

    def scan_path(self, item_path, algorithm, columns):
        if columns<3 or not isinstance(columns, int):
            columns = 3
        try:
            line = []
            # col 1
            line.append(unicode(item_path))
            # col 2
            line.append(unicode(algorithm))
            # col 3
            if os.path.isdir(item_path):
                line.append(u'd')
            else:
                # No need to catch the ValueError from
                hash_gen = getattr(hashlib, algorithm)()
                with open(item_path, 'rb') as fh:
                    logger.info("Checking %s with algorithm %s" % (item_path, algorithm))
                    chunk = fh.read(1024*8)
                    while chunk:
                        hash_gen.update(chunk)
                        chunk= fh.read(1024*8)
                line.append(unicode(hash_gen.hexdigest()))
            if columns>3:
                # col4 - Length
                line.append(unicode(os.stat(item_path)[ST_SIZE]))
                if columns>4:
                    # col 5 - ModTime
                    line.append(unicode(os.stat(item_path)[ST_MTIME]))
            return line
        except OSError:
            raise DirectoryNotFound(directory_path=directory_path, recursive=recursive)
        except AttributeError:
            raise ValueError("This tool cannot perform hashtype %s" % algorithm)
        
    def scan_directory(self, directory_path, algorithm, recursive=False, columns=3):
        if os.path.exists(directory_path):
            if recursive:
                return self.scan_tree(directory_path, algorithm, columns)
            return self.scan_local(directory_path, algorithm, columns)
        else:
            raise DirectoryNotFound(directory_path=directory_path, recursive=recursive)

