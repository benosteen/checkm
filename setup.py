from setuptools import setup, find_packages
import sys, os

setup(name="Checkm",
      version="0.4",
      description="Checkm - create reports on the checksums of sets of files or URLs resources.",
      long_description="""\
From - http://www.cdlib.org/inside/diglib/checkm/checkmspec.html - Checkm is a general-purpose text-based file manifest format. Each line of a Checkm manifest is a set of whitespace-separated tokens, the first of which identifies the corresponding digital content by filename or URL. Other tokens identify digest algorithm, checksum, content length, and modification time. Tokens may be left unspecified with '-', the degenerate case being a simple file list. It is up to tools that use the Checkm format to specify any further restrictions on tokens (e.g., allowed defaults and digest algorithms) and overall manifest completeness and coherence. Checkm is designed to support tools that verify the bit-level integrity of groups of files in support of such things as content fixity, replication, import, and export. A manifest may be single-level or multi-level (hierarchical), the latter being useful, for example, in harvesting material from very large web sites (cf. sitemaps). 

This is aiming to support Checkm v0.7
""",
      author="Ben O'Steen",
      author_email='bosteen@gmail.com',
      url="http://packages.python.org/Checkm/",
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      scripts = ['bin/checkm', 'bin/bagitmanifest'],
      test_suite = "tests.test.TestCheckm",
      )

