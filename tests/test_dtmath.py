"""
Ax_Metrics - Test foundation chrono dtmath package

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import pytest

from .util import dt

import axonchisel.metrics.foundation.chrono.dtmath as dtmath


# ----------------------------------------------------------------------------


class TestMathBegin(object):
    """
    Test datetime math begin functions.
    """

    #
    # Setup / Teardown
    #

    #
    # Tests
    #

    def test_begin(self, dts):
        def t(dt1, check):
            assert dt1 == dt(check)
        t(dtmath.begin_second(dts[5]),   '2014-04-14 16:42:45 000000')
        t(dtmath.begin_minute(dts[5]),   '2014-04-14 16:42:00 000000')
        t(dtmath.begin_minute5(dts[5]),  '2014-04-14 16:40:00 000000')
        t(dtmath.begin_minute10(dts[5]), '2014-04-14 16:40:00 000000')
        t(dtmath.begin_minute15(dts[5]), '2014-04-14 16:30:00 000000')
        t(dtmath.begin_minute30(dts[5]), '2014-04-14 16:30:00 000000')
        t(dtmath.begin_hour(dts[5]),     '2014-04-14 16:00:00 000000')
        t(dtmath.begin_day(dts[5]),      '2014-04-14 00:00:00 000000')
        t(dtmath.begin_week(dts[5]),     '2014-04-13 00:00:00 000000')
        t(dtmath.begin_month(dts[5]),    '2014-04-01 00:00:00 000000')
        t(dtmath.begin_quarter(dts[5]),  '2014-04-01 00:00:00 000000')
        t(dtmath.begin_year(dts[5]),     '2014-01-01 00:00:00 000000')

    #
    # Internal Helpers
    #


# ----------------------------------------------------------------------------


class TestMathAdd(object):
    """
    Test datetime math add functions.
    """

    #
    # Setup / Teardown
    #

    #
    # Tests
    #

    def test_add_microseconds(self, dts):
        def t(delta, check):
            assert dtmath.add_microseconds(dts[4], delta) == dt(check)
        t(+1000022, '2014-02-14 16:30:46 001256')
        t(-2000,    '2014-02-14 16:30:44 999234')

    def test_add_seconds(self, dts):
        def t(delta, check):
            assert dtmath.add_seconds(dts[4], delta) == dt(check)
        t(+5,           '2014-02-14 16:30:50 001234')
        t(-5,           '2014-02-14 16:30:40 001234')
        t(+1816,        '2014-02-14 17:01:01 001234')
        t(-1850,        '2014-02-14 15:59:55 001234')
        t(-3600*24*120, '2013-10-17 16:30:45 001234')
        t(+3600*24*120, '2014-06-14 16:30:45 001234')

    def test_add_minutes(self, dts):
        def t(delta, check):
            assert dtmath.add_minutes(dts[4], delta) == dt(check)
        t(+5,       '2014-02-14 16:35:45 001234')
        t(-5,       '2014-02-14 16:25:45 001234')
        t(+1450,    '2014-02-15 16:40:45 001234')
        t(-1450,    '2014-02-13 16:20:45 001234')
        t(-1440*60, '2013-12-16 16:30:45 001234')
        t(+1440*60, '2014-04-15 16:30:45 001234')

    def test_add_minute5s(self, dts):
        def t(delta, check):
            assert dtmath.add_minute5s(dts[4], delta) == dt(check)
        t(+1,       '2014-02-14 16:35:45 001234')
        t(-1,       '2014-02-14 16:25:45 001234')
        t(+290,     '2014-02-15 16:40:45 001234')
        t(-290,     '2014-02-13 16:20:45 001234')
        t(-288*60,  '2013-12-16 16:30:45 001234')
        t(+288*60,  '2014-04-15 16:30:45 001234')

    def test_add_minute10s(self, dts):
        def t(delta, check):
            assert dtmath.add_minute10s(dts[4], delta) == dt(check)
        t(+1,       '2014-02-14 16:40:45 001234')
        t(-1,       '2014-02-14 16:20:45 001234')
        t(+145,     '2014-02-15 16:40:45 001234')
        t(-145,     '2014-02-13 16:20:45 001234')
        t(-144*60,  '2013-12-16 16:30:45 001234')
        t(+144*60,  '2014-04-15 16:30:45 001234')

    def test_add_minute15s(self, dts):
        def t(delta, check):
            assert dtmath.add_minute15s(dts[4], delta) == dt(check)
        t(+1,       '2014-02-14 16:45:45 001234')
        t(-1,       '2014-02-14 16:15:45 001234')
        t(+100,     '2014-02-15 17:30:45 001234')
        t(-100,     '2014-02-13 15:30:45 001234')
        t(-144*60,  '2013-11-16 16:30:45 001234')
        t(+144*60,  '2014-05-15 16:30:45 001234')

    def test_add_minute30s(self, dts):
        def t(delta, check):
            assert dtmath.add_minute30s(dts[4], delta) == dt(check)
        t(+1,       '2014-02-14 17:00:45 001234')
        t(-1,       '2014-02-14 16:00:45 001234')
        t(+100,     '2014-02-16 18:30:45 001234')
        t(-100,     '2014-02-12 14:30:45 001234')
        t(-144*60,  '2013-08-18 16:30:45 001234')
        t(+144*60,  '2014-08-13 16:30:45 001234')

    def test_add_hours(self, dts):
        def t(delta, check):
            assert dtmath.add_hours(dts[4], delta) == dt(check)
        t(+5,    '2014-02-14 21:30:45 001234')
        t(-5,    '2014-02-14 11:30:45 001234')
        t(+44,   '2014-02-16 12:30:45 001234')
        t(-44,   '2014-02-12 20:30:45 001234')

    def test_add_days(self, dts):
        def t(delta, check):
            assert dtmath.add_days(dts[4], delta) == dt(check)
        t(+5,    '2014-02-19 16:30:45 001234')
        t(-5,    '2014-02-09 16:30:45 001234')
        t(+700,  '2016-01-15 16:30:45 001234')
        t(-700,  '2012-03-16 16:30:45 001234')

    def test_add_weeks(self, dts):
        def t(delta, check):
            assert dtmath.add_weeks(dts[4], delta) == dt(check)
        t(+5,    '2014-03-21 16:30:45 001234')
        t(-5,    '2014-01-10 16:30:45 001234')
        t(+200,  '2017-12-15 16:30:45 001234')
        t(-200,  '2010-04-16 16:30:45 001234')

    def test_add_months(self, dts):
        def t(delta, check):
            assert dtmath.add_months(dts[4], delta) == dt(check)
        t(+5,    '2014-07-14 16:30:45 001234')
        t(-5,    '2013-09-14 16:30:45 001234')
        t(+100,  '2022-06-14 16:30:45 001234')
        t(-100,  '2005-10-14 16:30:45 001234')

    def test_add_quarters(self, dts):
        def t(delta, check):
            assert dtmath.add_quarters(dts[4], delta) == dt(check)
        t(+2,    '2014-08-14 16:30:45 001234')
        t(-2,    '2013-08-14 16:30:45 001234')
        t(+40,   '2024-02-14 16:30:45 001234')
        t(-40,   '2004-02-14 16:30:45 001234')

    def test_add_years(self, dts):
        def t(delta, check):
            assert dtmath.add_years(dts[4], delta) == dt(check)
        t(+2,    '2016-02-14 16:30:45 001234')
        t(-2,    '2012-02-14 16:30:45 001234')
        t(+150,  '2164-02-14 16:30:45 001234')
        t(-150,  '1864-02-14 16:30:45 001234')

    def test_add_macro(self, dts):
        dt2 = dtmath.add(dts[4],
            years=1, quarters=2, months=3, weeks=4, days=5,
            hours=6,
            minutes5=7, minutes10=8, minutes15=9, minutes30=10,
            minutes=11,
            seconds=12, milliseconds=13, microseconds=14
        )
        assert dt2 == dt('2015-12-20 07:51:57 014248')

    #
    # Internal Helpers
    #


