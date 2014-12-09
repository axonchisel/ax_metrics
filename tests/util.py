"""
Ax_Metrics - Common testing utility functions.

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import os
from datetime import datetime
import logging

import axonchisel.metrics.foundation.metricdef.mdefl as mdefl
import axonchisel.metrics.foundation.query.mql as mql


# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------
# Utility Functions


def dt(dtstr):  # (parse datetime str)
    """
    Return datetime parsed from str of various accepted formats, eg:
      - '2014-02-14 16:30:45 001234'
      - '2014-02-14 16:30:45'
      - '2014-02-14 16:30'
      - '2014-02-14'
    Raise ValueError if not recognizable.
    """
    FORMATS = (
        '%Y-%m-%d %H:%M:%S %f',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y-%m-%d',
    )
    for fmt in FORMATS:
        try:
            dt1 = datetime.strptime(dtstr, fmt)
            return dt1
        except ValueError as e:
            pass
    raise ValueError("time data '{dtstr}' does not match any format"
        .format(dtstr=dtstr))


def load_test_asset(fname):
    """
    Load a test file from assets directory, returning contents as str.
    """
    path = os.path.dirname(os.path.realpath(__file__))
    fname = os.path.join(path, 'assets', fname)
    with open(fname, 'r') as f:
        return f.read()

def load_metset(asset):
    """Helper to load test asset and parse as MetSet, returning."""
    yaml_metset1 = load_test_asset(asset)
    parser1 = mdefl.MetSetParser()
    return parser1.parse_ystr_metset(yaml_metset1)

def load_queryset(asset):
    """Helper to load test asset and parse as QuerySet, returning."""
    yaml_queryset1 = load_test_asset(asset)
    parser1 = mql.QuerySetParser()
    return parser1.parse_ystr_queryset(yaml_queryset1)

def load_query(asset):
    """Helper to load test asset and parse as Query, returning."""
    yaml_query1 = load_test_asset(asset)
    parser1 = mql.QueryParser()
    return parser1.parse_ystr_query(yaml_query1)

def log_config(level=logging.DEBUG):
    """
    Configure logging.
    Hackily colors log output if 'colorlog' is installed.
    See: https://pypi.python.org/pypi/colorlog/
    """

    format  = ("%(asctime)s %(levelname)-8s [%(name)s]  %(message)s")
    cformat = ("%(bg_black)s%(asctime)s "+
        "%(log_color)s%(levelname)-8s [%(name)-50s] %(reset)s "+
        "%(log_color)s%(bold)s%(message)s")

    def color_if_possible():
        try:
            from colorlog import ColoredFormatter
        except ImportError:
            return  # optional lib not available, so don't color
        formatter = ColoredFormatter(cformat)
        logging.getLogger().handlers[0].formatter = formatter

    logging.basicConfig(level=level, format=format)
    color_if_possible()





