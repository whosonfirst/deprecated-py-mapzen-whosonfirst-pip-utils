#!/usr/bin/env python

# Remove .egg-info directory if it exists, to avoid dependency problems with                                                                                                                 
# partially-installed packages (20160119/dphiffer)                                                                                                                                           

import os, sys
from shutil import rmtree

cwd = os.path.dirname(os.path.realpath(sys.argv[0]))
egg_info = cwd + "/mapzen.whosonfirst.pip.utils.egg-info"
if os.path.exists(egg_info):
    rmtree(egg_info)

from setuptools import setup, find_packages

packages = find_packages()
desc = open("README.md").read(),
version = open("VERSION").read()

setup(
    name='mapzen.whosonfirst.pip.utils',
    namespace_packages=['mapzen', 'mapzen.whosonfirst', 'mapzen.whosonfirst.pip', 'mapzen.whosonfirst.pip.utils'],
    version=version,
    description='Python utility methods for making Who\'s On First documents play nicely with the go-whosonfirst-pip server',
    author='Mapzen',
    url='https://github.com/mapzen/py-mapzen-whosonfirst-pip-utils',
    install_requires=[
        'mapzen.whosonfirst.pip>=0.04',
        'mapzen.whosonfirst.placetypes>=0.11',
        'shapely',
        ],
    dependency_links=[
        'https://github.com/whosonfirst/py-mapzen-whosonfirst-pip/tarball/master#egg=mapzen.whosonfirst.pip-0.04',
        'https://github.com/whosonfirst/py-mapzen-whosonfirst-placetypes/tarball/master#egg=mapzen.whosonfirst.placetypes-0.11',
        ],
    packages=packages,
    scripts=[
        ],
    download_url='https://github.com/mapzen/py-mapzen-whosonfirst-pip-utils/releases/tag/' + version,
    license='BSD')
