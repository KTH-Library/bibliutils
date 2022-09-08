#!/usr/bin/env python

from setuptools import setup

setup(name='bibliutils',
      version='1.0',
      # list folders, not files
      packages=['bibliutils',
                'bibliutils.test'],
      scripts=[
            'bibliutils/bin/bibapi_script.py', 
            'bibliutils/bin/bibformat_script.py'      ]
      )
