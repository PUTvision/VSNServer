#!/usr/bin/env python3

from setuptools import setup, find_packages

from vsn_server import __version__

setup(
    name='VSN',
    version=__version__,
    description='Server for network of smart cameras with enhanced autonomy',
    author='PUT Vision Lab',
    url='https://github.com/PUTvision/VSNServer',
    install_requires=[
        'PyYAML',
        'quamash',
        'git+https://github.com/pyqtgraph/pyqtgraph.git@develop',
        'numpy',
    ],
    packages=find_packages(),
    scripts=['bin/VSNServer', 'bin/VSNHistoryPlotter'],
)
