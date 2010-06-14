#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Checksumming convenience classes

TODO! Sorry!

                [@]SourceFileOrURL  Alg     Digest  Length   ModTime   TargetFileOrURL
TOKEN NUMBER:    1                  2       3       4        5         6

"""

from __future__ import with_statement

COLUMNS = { 0:"SourceFileOrURL",
            1:"Alg",
            2:"Digest",
            3:"Length",
            4:"ModTime",
            5:"TargetFileOrURL",
            }


import os, sys
from stat import *

import re

from collections import defaultdict

import hashlib

import codecs

import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger('checkm')

class NotFound(Exception):
    """The item or directory was either not found, or not accessible."""
    def __init__(self, *arg, **kw):
        """
        FIXME
        @param *arg:
        @type *arg:
        @param **kw:
        @type **kw:
        """
        self.context = (arg, kw)
    def __repr__(self):
        """
        FIXME
        """
        return self.context.__str__()
    def __str__(self):
        """
        FIXME
        """
        return self.context.__str__()

class CheckmReporter(object):
    COLUMN_NAMES = [u'# [@]SourceFileOrURL',u'Alg',u'Digest',u'Length',u'ModTime']
    def __init__(self):
        """
        FIXME
        """
        self.scanner = CheckmScanner()

    def _get_max_len(self, report):
        """
        FIXME
        @param report:
        @type report:
        """
        cols = defaultdict(lambda : 0)
        for line in report:
            for index in xrange(len(line)):
                if len(line[index])>cols[index]:
                    cols[index] = len(line[index])
        return cols

    def _space_line(self, line, col_maxes):
        """
        FIXME
        @param line:
        @type line:
        @param col_maxes:
        @type col_maxes:
        """
        spaced_line = []
        for index in xrange(len(line)):
            spaced_line.append(line[index])
            spaces = col_maxes[index]-len(line[index])+4
            spaced_line.append(u" "*spaces)
        return u"".join(spaced_line)

    def create_bagit_manifest(self, scan_directory, algorithm, recursive=False, delimiter = "  ", filename=None):
        """
        FIXME
        @param scan_directory:
        @type scan_directory:
        @param algorithm:
        @type algorithm:
        @param recursive=False:
        @type recursive=False:
        @param delimiter:
        @type delimiter:
        @param filename=None:
        @type filename=None:
        """
        if not filename:
            filename = "manifest-%s.txt" % algorithm
        logger.info("Creating bagit manifest file(%s) for dir(%s) with Alg:%s" % (filename,
                                                                                          scan_directory,
                                                                                          algorithm))
        report = self.scanner.scan_directory(scan_directory, algorithm, recursive=recursive, columns=3)
        if hasattr(filename, 'write'):
            faked_filename = "manifest-%s.txt" % algorithm
            for line in report:
                if line[2] != "d":
                    if os.path.abspath(line[0]) != os.path.abspath(faked_filename):
                        filename.write("%s%s%s\n" % (line[2], delimiter, line[0]))
                    else:
                        logger.info("Manifest file match - scan line ignored")
        else:
            with codecs.open(filename, encoding='utf-8', mode="w") as output:
                for line in report:
                    if line[2] != "d":
                        if os.path.abspath(line[0]) != os.path.abspath(filename):
                            output.write("%s%s%s\n" % (line[2], delimiter, line[0]))
                        else:
                            logger.info("Manifest file match - scan line ignored")
                output.write("\n")
        return filename
        
    def create_multilevel_checkm(self, top_directory, algorithm, checkm_filename, columns=3):
        logger.info("Creating multilevel checkm files '(%s)' from top level directory(%s) with Alg:%s and columns:%s" % (checkm_filename, top_directory, algorithm, columns))
        if not os.path.isdir(top_directory):
            raise NotFound(top_directory=top_directory)
        # Gather list of directories to scan
        # And their subdirectories
        # bottom up!
        dir_list = [(root, dirnames) for (root, dirnames, _) in os.walk(top_directory, topdown=False)]
        dirs = dict(dir_list)
        # per directory
        for (dirname,_) in dir_list:
            logger.info('creating checkm file %s in %s' % (checkm_filename, dirname))
            with codecs.open(os.path.join(dirname, checkm_filename), encoding='utf-8', mode="w") as output:
                self.create_checkm_file(dirname, 
                                        algorithm, 
                                        os.path.join(dirname, checkm_filename), 
                                        recursive=False,
                                        columns=columns,
                                        checkm_file=output)
                subdir_report = []
                for subdir in dirs[dirname]:
                    logger.info('Checking sub-checkm file and adding it to the list of hashes in %s' % dirname)
                    try:
                        line = self.scanner.scan_path(os.path.join(dirname, subdir, checkm_filename), algorithm, columns)
                        logger.info("Line - %s" % line)
                        line[0] = '@%s' % (line[0])
                        subdir_report.append(line)
                    except Exception, e:
                        print dirname, subdir, checkm_filename
                        print "Fail! %s" % e
                col_maxes = self._get_max_len(subdir_report)
                for line in subdir_report:
                    output.write('%s\n' % (self._space_line(line, col_maxes)))
                output.write('\n')

    def create_checkm_file(self, scan_directory, algorithm, checkm_filename, recursive=False, columns=3, checkm_file=None):
        logger.info("Creating checkm file for dir(%s) with Alg:%s and columns: %s" % (
                                                                                          scan_directory,
                                                                                          algorithm, columns))
        report = self.scanner.scan_directory(scan_directory, algorithm, recursive=recursive, columns=columns)
        col_maxes = self._get_max_len(report)
        if checkm_file != None and hasattr(checkm_file, 'write'):
            checkm_file.write("%s \n" % (self._space_line(CheckmReporter.COLUMN_NAMES[:columns], col_maxes)))
            for line in report:
                if os.path.abspath(line[0]) != os.path.abspath(checkm_filename):
                    checkm_file.write("%s\n" % (self._space_line(line, col_maxes)))
                else:
                    logger.info("Manifest file match - scan line ignored")
            return checkm_file
        else:
            with codecs.open(checkm_filename, encoding='utf-8', mode="w") as output:
                output.write("%s \n" % (self._space_line(CheckmReporter.COLUMN_NAMES[:columns], col_maxes)))
                for line in report:
                    if os.path.abspath(line[0]) != os.path.abspath(checkm_filename):
                        output.write("%s\n" % (self._space_line(line, col_maxes)))
                    else:
                        logger.info("Manifest file match - scan line ignored")
                output.write("\n")

    def check_bagit_hashes(self, bagit_filename, algorithm=None):
        """
        FIXME
        @param bagit_filename:
        @type bagit_filename:
        @param algorithm=None:
        @type algorithm=None:
        """
        logger.info("Checking files against '%s' bagit manifest" % bagit_filename)
        if algorithm == None:
            if hasattr(bagit_filename, 'read'):
                raise Exception("Need to supply the algorithm when passing a filelike object instead of a filename")
            m = re.search("manifest-(?P<alg>[^\.]+)\.txt", bagit_filename)
            if m != None:
                algorithm = m.groupdict()['alg']
        parser = BagitParser(bagit_filename)
        scanner = CheckmScanner()
        results = {'pass':[], 'fail':{}}
        for row in parser:
            if row:
                try:
                    scan_row = scanner.scan_path(row[1], algorithm, 3)
                    if row[0] != scan_row[2]:
                        logger.info("Failed original: %s" % row)
                        logger.info("Current scan: %s" % scan_row)
                        results['fail'][row[1]] = (row, scan_row)
                    else:
                        results['pass'].append(row[1])
                except NotFound:
                    scan_row = "File not found"
                    logger.info("Failed original: %s" % row)
                    logger.info("But file not found at this path.")
                    results['fail'][row[1]] = (row, scan_row)
        return results

    def check_checkm_hashes(self, scan_directory, checkm_filename, ignore_multilevel=True, columns=None):
        """
        FIXME
        @param scan_directory:
        @type scan_directory:
        @param checkm_filename:
        @type checkm_filename:
        """
        def _check_files_against_parser(parser, columns=None):
            scanner = CheckmScanner()
            results = {'pass':[], 'fail':{}, 'include':[]}
            for row in parser:
                if row:
                    try:
                        if row[0].startswith('@'):
                            row[0] = row[0][1:]
                            results['include'].append(row[0])
                        if not columns:
                            columns = len(row)
                        scan_row = scanner.scan_path(row[0], row[1], columns)
                        nomatch = False
                        for expected, scanned in zip(row, scan_row):
                            if expected != "-" and expected != scanned:
                                nomatch = True
                        if nomatch:
                            logger.info("Failed original: %s" % row)
                            logger.info("Current scan: %s" % scan_row)
                            results['fail'][row[0]] = (row, scan_row)
                        else:
                            results['pass'].append(row[0])
                    except NotFound:
                        scan_row = "File not found"
                        logger.info("Failed original: %s" % row)
                        logger.info("But file not found at this path.")
                        results['fail'][row[0]] = (row, scan_row)
            return results
        
        logger.info("Checking files against %s checkm manifest" % checkm_filename)
        parser = CheckmParser(checkm_filename)
        results = _check_files_against_parser(parser, columns)
        if ignore_multilevel:
            return results
        else:
            # shallow copy of the include list, as we will be pop'ing off items
            checkm_list = results['include'][:]
            while checkm_list:
                checkm_file = checkm_list.pop()
                parser = CheckmParser(checkm_file)
                additional_results = _check_files_against_parser(parser, columns)
                # Add to the passes
                results['pass'].extend(additional_results['pass'])
                # add to the overall list of 
                results['include'].extend(additional_results['include'])
                checkm_list.extend(additional_results['include'])
                # add to the fail dict
                results['fail'].update(additional_results['fail'])
            return results

class BagitParser(object):
    def __init__(self, bagit_file=None):
        """
        FIXME
        @param bagit_file=None:
        @type bagit_file=None:
        """
        self.status = False
        self.lines = []
        if bagit_file:
            self.parse(bagit_file)

    def __iter__(self):
        """
        FIXME
        """
        class Bagit_iter:
            def __init__(self, lines):
                """
                FIXME
                @param lines:
                @type lines:
                """
                self.lines = lines
                self.last = 0
            def __iter__(self):
                """
                FIXME
                """
                return self
            def next(self):
                """
                FIXME
                """
                if self.last >= len(self.lines):         # threshhold terminator
                    raise StopIteration
                elif len(self.lines) == 0:
                    raise StopIteration
                else:
                    self.last += 1
                    return self.lines[self.last-1]
        return Bagit_iter(self.lines)
    
    def parse(self, fileobj):
        """
        FIXME
        @param fileobj:
        @type fileobj:
        """
        if not hasattr(fileobj, "read"):
            with codecs.open(fileobj, encoding='utf-8', mode="r") as check_fh:
                self._parse_lines(check_fh)
        else:
            self._parse_lines(fileobj)
        return self.lines

    def _parse_lines(self, fh):
        """
        FIXME
        @param fh:
        @type fh:
        """
        self.lines = [] # clear the deck
        line_buffer = ""
        def _parse_line(line):
            """
            FIXME
            @param line:
            @type line:
            """
            if not line.startswith('#'):
                tokens = filter(lambda x: x, re.split("\s+", line, 1)) # 2 columns
                logger.info(tokens)
                if tokens:
                    # handle "\s*\*" situation
                    if tokens[1].startswith("*"):
                        tokens[1] = tokens[1][1:].strip()
                    self.lines.append(tokens)
        for chunk in fh.read(0x1000):
            line_buffer = line_buffer + chunk
            while True:
                if not line_buffer:
                    break
                fragments = line_buffer.split('\n',1)
                if len(fragments) == 1:
                    break
                _parse_line(fragments[0])
                line_buffer = fragments[1]

class CheckmParser(object):
    def __init__(self, checkm_file=None):
        """
        FIXME
        @param checkm_file=None:
        @type checkm_file=None:
        """
        self.status = False
        self.lines = []
        if checkm_file:
            self.parse(checkm_file)
    
    def __iter__(self):
        """
        FIXME
        """
        class Checkm_iter:
            def __init__(self, lines):
                """
                FIXME
                @param lines:
                @type lines:
                """
                self.lines = lines
                self.last = 0
            def __iter__(self):
                """
                FIXME
                """
                return self
            def next(self):
                """
                FIXME
                """
                if self.last >= len(self.lines):         # threshhold terminator
                    raise StopIteration
                elif len(self.lines) == 0:
                    raise StopIteration
                else:
                    self.last += 1
                    return self.lines[self.last-1]
        return Checkm_iter(self.lines)

    def parse(self, checkm_file):
        """
        FIXME
        @param checkm_file:
        @type checkm_file:
        """
        if not hasattr(checkm_file, "read"):
            if os.path.isfile(checkm_file):
                with codecs.open(checkm_file, encoding='utf-8', mode="r") as check_fh:
                    self._parse_lines(check_fh)
            else:
                raise NotFound(checkm_file=checkm_file)
        else:
            self._parse_lines(checkm_file)
        return self.lines

    def _parse_lines(self, fh):
        """
        FIXME
        @param fh:
        @type fh:
        """
        self.lines = [] # clear the deck
        line_buffer = ""
        def _parse_line(line):
            """
            FIXME
            @param line:
            @type line:
            """
            if not line.startswith('#'):
                tokens = filter(lambda x: x, re.split("\s+", line, 5)) # 6 column max defn == 5 splits
                logger.info(tokens)
                if tokens:
                    self.lines.append(tokens)

        for line in fh.readlines():
            if line.endswith("\n"):
                _parse_line(line[:-1])
            else:
                _parse_line(line)

class CheckmScanner(object):
    HASHTYPES = ['md5', 'sha1', 'sha224','sha256','sha384','sha512']
    def scan_local(self, directory_path, algorithm, columns=3):
        """
        FIXME
        @param directory_path:
        @type directory_path:
        @param algorithm:
        @type algorithm:
        @param columns=3:
        @type columns=3:
        """
        report = []
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            report.append(self.scan_path(item_path, algorithm, columns))
        return report

    def scan_tree(self, directory_path, algorithm, columns):
        """
        FIXME
        @param directory_path:
        @type directory_path:
        @param algorithm:
        @type algorithm:
        @param columns:
        @type columns:
        """
        report = []
        if os.path.exists(directory_path):
            for (dirpath, dirnames, filenames) in os.walk(directory_path):
                for item_path in [os.path.join(dirpath, x) for x in dirnames+filenames]:
                    report.append(self.scan_path(item_path, algorithm, columns))
            return report
        else:
            raise NotFound(directory_path=directory_path, recursive=True)

    def scan_path(self, item_path, algorithm, columns):
        """
        FIXME
        @param item_path:
        @type item_path:
        @param algorithm:
        @type algorithm:
        @param columns:
        @type columns:
        """
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
            logger.info("item exists? %s" % os.path.exists(item_path))
            raise NotFound(item_path=item_path)
        except IOError:
            logger.info("item exists? %s" % os.path.exists(item_path))
            raise NotFound(item_path=item_path)
        except AttributeError:
            raise ValueError("This tool cannot perform hashtype %s" % algorithm)
        
    def scan_directory(self, directory_path, algorithm, recursive=False, columns=3):
        """
        FIXME
        @param directory_path:
        @type directory_path:
        @param algorithm:
        @type algorithm:
        @param recursive=False:
        @type recursive=False:
        @param columns=3:
        @type columns=3:
        """
        if os.path.exists(directory_path):
            if recursive:
                return self.scan_tree(directory_path, algorithm, columns)
            return self.scan_local(directory_path, algorithm, columns)
        else:
            raise NotFound(directory_path=directory_path, recursive=recursive)

