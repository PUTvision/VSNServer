#!/usr/bin/env python3

from setuptools import setup

from vsn_server import __version__

setup(
      name='VSN',
      version=__version__,
      description='Network of smart cameras with enhanced autonomy ui',
      author='PUT Vision Lab',
      url='https://github.com/PUTvision/VSNServer',
      install_requires=[
          'PyYAML',
          'quamash',
          'git+https://github.com/pyqtgraph/pyqtgraph.git@develop',
          'numpy',
      ],
      packages=['vsn_server.ui', 'vsn_server.common', 'vsn_server.connectivity'],
      scripts=['bin/VSNServer', 'bin/VSNHistoryPlotter', 'bin/VSNUpdater'],
)
