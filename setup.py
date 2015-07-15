#!/usr/bin/env python

import sys
from setuptools import setup

try:
    import PyQt4
except ImportError:
    sys.exit('PyQt4 is required to install this package')

with open('./requirements.txt') as requirements_txt:
    requirements = [line for line in requirements_txt]

setup(name='VSN',
      version='0.1',
      description='Network of smart cameras with enhanced autonomy',
      author='PUT VISION LAB',
      url='https://github.com/sepherro/cam_network',

      install_requires=requirements,

      packages=['server', 'client', 'common', 'connectivity'],
      scripts=['VSNClientCV', 'VSNClientPiCamera', 'VSNServer', 'VSNHistoryPlotter'],
      )
