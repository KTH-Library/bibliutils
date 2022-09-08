#!/usr/bin/env python

"""
test code for bibapi module

can be run with py.test
"""

import os
from pathlib import Path
import pytest
from bibliutils import bibapi

def test_01():
    MyClient = bibapi.BibAPI()
    Result1 = MyClient.altmetric(path='doi/10.1002/ijc.11382')
    assert True is True

