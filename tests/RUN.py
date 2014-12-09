#!/usr/bin/env python
"""
Ax_Metrics - Unit testing runner

Runs all unit tests using py.test, passing through cmdline args as if
py.test had been run directly.

On failures, ring terminal bell.

Optionally specify specific test(s) on cmdline via expression to be
passed to py.test -k.  (See py.test help for more info)

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import os
import sys

import pytest


# ----------------------------------------------------------------------------


def add_app_python_path():
    """Add our app's python code to system python path."""
    app_py_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '../py'
    )
    sys.path.append(app_py_path)

def run_tests():
    """Run tests, returning py.test numeric exit code (0=success)."""
    rescode = pytest.main(sys.argv[1:])
    if rescode != 0:
        alert_fail()
    return rescode

def alert_fail():
    """Called when tests fail. Ring bell."""
    print '\x07'  # ring terminal bell


# ----------------------------------------------------------------------------


if __name__ == "__main__":
    add_app_python_path()
    rescode = run_tests()
    sys.exit(rescode)

