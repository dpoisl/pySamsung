#!/usr/bin/env python

from setuptools import setup, find_packages

with open('README.md') as readme:
    description = readme.read()

setup(name='samsung',
      version='0.1.0',
      description='network remote library for Samsung C, D and E-Series devices',
      long_description=description,
      author='David Poisl',
      author_email='david@poisl.at',
      url='https://github.com/dpoisl/pySamsung/',
      platforms=('any',),
      packages=find_packages(),
      entry_points={
          'console_scripts': [
              'sstv_remote = samsung.cli:remote',
              'sstv_listener = samsung.cli:listener',
          ]
      },
      classifiers=('Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 3',
                   'Operating System :: OS Independent',
                   'Topic :: Software Development :: Libraries',
                   'Topic :: Multimedia',
                   'Topic :: Home Automation',
                   'Topic :: Internet',
                   )
     )
