#!/usr/bin/env python

from setuptools import setup
from common.version import __version__

with open('./requirements.txt') as requirements_txt:
    requirements = [line for line in requirements_txt]

setup(name='VSN',
      version=__version__,
      description='Network of smart cameras with enhanced autonomy',
      author='PUT VISION LAB',
      url='https://github.com/sepherro/cam_network',
      install_requires=requirements,
      packages=['server', 'client', 'common', 'connectivity'],
      scripts=['VSNClientCV', 'VSNClientPiCamera', 'VSNServer', 'VSNHistoryPlotter', 'VSNUpdater'],
      )
