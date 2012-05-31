#!/usr/bin/env python

from distutils.core import setup

readme = open("README.md")

setup(name="samsung", 
      version="0.1.0",
      description='network remote library for Samsung C, D and E-Series devices',
      long_description=readme.read(),
      author='David Poisl',
      author_email='david@poisl.at',
      url='https://github.com/dpoisl/pySamsung/',
      platforms=("any",)
      packages=('samsung',),
      scripts=("scripts/samsung_remote",),
      classifiers=("Development Status :: 3 - Alpha",
                   "Intended Audience :: Developers",
                   "Programming Language :: Python",
                   "Programming Language :: Python :: 3",
                   "Operating System :: OS Independent",
                   "Topic :: Software Development :: Libraries",
                   "Topic :: Multimedia",
                   "Topic :: Home Automation",
                   "Topic :: Internet",
                   )
     )

readme.close()
