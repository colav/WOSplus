#!/usr/bin/env python3
# coding: utf-8

# Copyright (c) Juptyer Development Team.
# Distributed under the terms of the Modified BSD License.

#-----------------------------------------------------------------------------
# Minimal Python version sanity check (from IPython)
#-----------------------------------------------------------------------------

# https://packaging.python.org/guides/making-a-pypi-friendly-readme/
# See https://github.com/fhamborg/news-please/wiki/PyPI---How-to-upload-a-new-version
# python setup.py sdist
# python setup.py sdist upload

from __future__ import print_function
from setuptools import setup, find_packages

import os
import shutil
import sys


v = sys.version_info
if v[0] < (3):
    error = "ERROR: WOSplus requires Python version 3 or above."
    print(error, file=sys.stderr)
    sys.exit(1)

shell = False
if os.name in ('nt', 'dos'):
    shell = True
    warning = "WARNING: Windows is not officially supported"
    print(warning, file=sys.stderr)

def main():
    setup(
        # Application name:
        name="WOSplus",

        # Version number (initial):
        version="0.2.0",

        # Application author details:
        author="Diego Restrepo",
        author_email="restrepo@udea.edu.co",

        # Packages
        packages=find_packages(exclude=['tests']),

        # Include additional files into the package
        include_package_data=True,

        # Details
        url="https://github.com/restrepo/WOSplus",

        #
        license="BSD",
        description="WOS+ is a tool for to manage and merge bibliographic databases like Web Of Science or Scopus",
        
        long_description=open("README.md").read(),

        long_description_content_type="text/markdown",
        
        # Dependent packages (distributions)
        install_requires=[
            'configparser',
            'xlrd',
            'requests',
            'numpy',
            'pandas',
            'unidecode',
            'python-levenshtein',
        ],
    )

if __name__ == "__main__":
    main()
