# -*- coding: utf-8 -*-
"""
Ax_Metrics - Common pytest configuration.

Main tests and conftest.py are in tests/ directory.
This is a top level conftest to allow more flexible running of tests,
e.g. by executing "tests/RUN.py" from this directory.

Note: 'conftest.py' is a magic filename used by py.test.

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


collect_ignore = [
    'dist',   # don't descend into built versions in 'dist'
]
