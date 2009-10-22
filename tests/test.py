# -*- coding: utf-8 -*-
import random, unittest, re

import os

from StringIO import StringIO

import checkm

import logging

class TestCheckm(unittest.TestCase):
    def setUp(self):
        self.reporter = checkm.CheckmReporter()
        self.scanner = checkm.CheckmScanner()
        self.checkm_p = checkm.CheckmParser()
        self.bagit_p = checkm.BagitParser()
        
        checkm.logger.setLevel(logging.ERROR)
        
    def test_empty(self):
        pass

    def test_checkmp_emptyline(self):
        s = StringIO("")
        self.checkm_p._parse_lines(s)
        # Empty string should result in an empty list
        self.assertEqual(len(self.checkm_p.lines), 0)
        self.assertFalse(self.checkm_p.lines)
        
    def test_checkmp_simpleline(self):
        s = StringIO("./filename           45aa56b8    md5\n")
        self.checkm_p._parse_lines(s)
        self.assertEqual(len(self.checkm_p.lines), 1)
        line = self.checkm_p.lines[0]
        self.assertEqual(line[0], './filename')
        self.assertEqual(line[1], '45aa56b8')
        self.assertEqual(line[2], 'md5')
        
    def test_checkmp_nospaceline(self):
        # Should 'parse' to 5 lines of 1 element each
        s = StringIO("""./filenames/in/simple/manifest/format/no/hash
./filenames/in/simple/manifest/format/no/hash
./filenames/in/simple/manifest/format/no/hash
./filenames/in/simple/manifest/format/no/hash
./filenames/in/simple/manifest/format/no/hash\n""")
        self.checkm_p._parse_lines(s)
        self.assertEqual(len(self.checkm_p.lines), 5)
        self.assertEqual(len(self.checkm_p.lines[0]), 1)

    def test_checkmp_loadsacolumns(self):
        # Should 'parse' to 5 lines of 1 element each
        s = StringIO("""one two three four five six six_still six_again\n""")
        self.checkm_p._parse_lines(s)
        self.assertEqual(len(self.checkm_p.lines), 1)
        self.assertEqual(len(self.checkm_p.lines[0]), 6)
        self.assertEqual(self.checkm_p.lines[0][5], "six six_still six_again")


if __name__ == '__main__':
    unittest.main()
