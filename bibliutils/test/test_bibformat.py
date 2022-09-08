#!/usr/bin/env python

"""
test code for bibformat module

can be run with py.test
"""

import os
import requests
from pathlib import Path
import pytest
from bibliutils import bibformat

def test_01():
    res = bibformat.fix_doi("Random_string!?")
    assert res == ""
