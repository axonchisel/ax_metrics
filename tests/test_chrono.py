"""
Ax_Metrics - Test foundation chrono package

See test_dtmath.py for chrono.dtmath test suite.

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import pytest
from datetime import datetime, timedelta

from .util import dt

import axonchisel.metrics.foundation.chrono.timerange as timerange
import axonchisel.metrics.foundation.chrono.framespec as framespec
import axonchisel.metrics.foundation.chrono.ghost as ghost
import axonchisel.metrics.foundation.chrono.stepper as stepper


# ----------------------------------------------------------------------------


class TestTimeRange(object):
    """
    Test TimeRange object.
    """

    #
    # Setup / Teardown
    #

    #
    # Tests
    #

    def test_str(self):
        tmrange = timerange.TimeRange()
        str(tmrange)

    def test_initial_invalid(self, dts):
        tmrange = timerange.TimeRange()
        assert not tmrange.is_valid()
        with pytest.raises(ValueError):
            tmrange.validate()
        tmrange = timerange.TimeRange(inc_begin=dts[4])
        assert not tmrange.is_valid()
        tmrange = timerange.TimeRange(exc_end=dts[4])
        assert not tmrange.is_valid()

    def test_anchor(self, dts):
        tmrange = timerange.TimeRange(inc_begin=dts[4], inc_end=dts[5],
            anchor=dts[5] - timedelta(days=5))
        assert tmrange.is_anchored()
        assert tmrange.is_valid()

    def test_init_inc(self, dts):
        tmrange = timerange.TimeRange(inc_begin=dts[4], inc_end=dts[5])
        assert tmrange.is_valid()
        assert tmrange.inc_begin == dts[4]
        assert tmrange.inc_end == dts[5]
        assert tmrange.exc_begin == (dts[4] - timerange.TIMERANGE_PRECISION)
        assert tmrange.exc_end == (dts[5] + timerange.TIMERANGE_PRECISION)

    def test_init_exc(self, dts):
        tmrange = timerange.TimeRange(exc_begin=dts[4], exc_end=dts[5])
        assert tmrange.is_valid()
        assert tmrange.exc_begin == dts[4]
        assert tmrange.exc_end == dts[5]
        assert tmrange.inc_begin == (dts[4] + timerange.TIMERANGE_PRECISION)
        assert tmrange.inc_end == (dts[5] - timerange.TIMERANGE_PRECISION)

    def test_set_get_inc(self, dts):
        tmrange = timerange.TimeRange()
        tmrange.inc_begin = dts[4]
        tmrange.inc_end = dts[5]
        assert tmrange.is_valid()
        assert tmrange.exc_begin == (dts[4] - timerange.TIMERANGE_PRECISION)
        assert tmrange.exc_end == (dts[5] + timerange.TIMERANGE_PRECISION)

    def test_set_get_exc(self, dts):
        tmrange = timerange.TimeRange()
        tmrange.exc_begin = dts[4]
        tmrange.exc_end = dts[5]
        assert tmrange.is_valid()
        assert tmrange.inc_begin == (dts[4] + timerange.TIMERANGE_PRECISION)
        assert tmrange.inc_end == (dts[5] - timerange.TIMERANGE_PRECISION)

    def test_duration(self, dts):
        tmrange = timerange.TimeRange(inc_begin=dts[4], exc_end=dts[5])
        assert tmrange.duration == timedelta(days=59, seconds=720)

    #
    # Internal Helpers
    #


# ----------------------------------------------------------------------------


class TestFrameSpec(object):
    """
    Test FrameSpec object on its own.
    """

    #
    # Setup / Teardown
    #

    #
    # Tests
    #

    def test_simple(self):
        tmfrspec = framespec.FrameSpec()

    def test_str(self):
        tmfrspec = framespec.FrameSpec()
        str(tmfrspec)

    def test_reframe(self, dts, tmfrspecs):
        assert tmfrspecs[0].is_reframed() == False
        tmfrspecs[0].reframe_dt = dts[4]
        assert tmfrspecs[0].is_reframed() == True
        tmfrspec = framespec.FrameSpec(reframe_dt=dts[4])
        assert tmfrspec.is_reframed() == True

    def test_smooth(self):
        tmfrspec = framespec.FrameSpec(smooth_val=4, smooth_unit='HOUR')
        assert tmfrspec.smooth_val == 4

    def test_invalid(self):
        tmfrspec = framespec.FrameSpec()
        with pytest.raises(ValueError):
            framespec.FrameSpec(range_unit='BOGUSUNIT')
        with pytest.raises(TypeError):
            framespec.FrameSpec(range_val='not an int')
        with pytest.raises(ValueError):
            framespec.FrameSpec(gran_unit='BOGUSUNIT')
        with pytest.raises(ValueError):
            framespec.FrameSpec(mode='BOGUSMODE')
        with pytest.raises(TypeError):
            framespec.FrameSpec(reframe_dt='not a datetime')

    #
    # Internal Helpers
    #


# ----------------------------------------------------------------------------


class TestStepper(object):
    """
    Test Stepper object.
    """

    #
    # Setup / Teardown
    #

    #
    # Tests
    #

    def test_simple(self, dts):
        steps = self._steps({
            'range_unit' : 'MONTH',
            'range_val'  :  1,
            'gran_unit'  :  'DAY',
            'mode'       : 'CURRENT',
            'reframe_dt' : dts[4],
        })
        assert len(steps) == 28
        assert steps[5].inc_begin == dt('2014-02-06 00:00:00 000000')

    def test_str(self, dts):
        tmfrspec_dict = {
            'range_unit' : 'MONTH',
            'range_val'  :  1,
            'gran_unit'  :  'DAY',
            'mode'       : 'CURRENT',
        }
        frspec = framespec.FrameSpec(**tmfrspec_dict)
        step1 = stepper.Stepper(frspec)
        str(step1)

    def test_impl_error_base_ok(self, tmfrspecs):
        list(stepper.Stepper(tmfrspecs[1]).steps())

    def test_impl_error_range_unit(self, tmfrspecs):
        tmfrspecs[1]._range_unit = 'BOGUS'
        with pytest.raises(ValueError):
            list(stepper.Stepper(tmfrspecs[1]).steps())

    def test_impl_error_gran_unit(self, tmfrspecs):
        tmfrspecs[1]._gran_unit = 'BOGUS'
        with pytest.raises(ValueError):
            list(stepper.Stepper(tmfrspecs[1]).steps())

    def test_impl_error_smooth_unit(self, tmfrspecs):
        tmfrspecs[1]._smooth_unit = 'BOGUS'
        with pytest.raises(ValueError):
            list(stepper.Stepper(tmfrspecs[1]).steps())

    def test_quarters1(self, dts):
        steps = self._steps({
            'range_unit' : 'QUARTER',
            'range_val'  : 1,
            'gran_unit'  : 'DAY',
            'mode'       : 'LASTWHOLE',
            'reframe_dt' : dts[5],
        })
        assert len(steps) == 90
        assert steps[5].inc_begin == dt('2014-01-06 00:00:00 000000')

    def test_quarters_overflow_begin(self, dts):
        tmfrspec_dict = {
            'range_unit' : 'QUARTER',
            'range_val'  : 1,
            'gran_unit'  : 'WEEK',
            'smooth_unit': 'DAY',
            'smooth_val' : 14,     # causes first week to overflow before period
            'mode'       : 'CURRENT',
            'reframe_dt' : dts[4],
        }
        steps = self._steps(tmfrspec_dict)
        assert len(steps) == 13
        assert steps[0].inc_begin == dt('2013-12-25 00:00:00 000000')
        assert steps[0].duration == timedelta(days=14)
        tmfrspec_dict['allow_overflow_begin'] = False
        steps = self._steps(tmfrspec_dict)
        assert len(steps) == 13
        assert steps[0].inc_begin == dt('2014-01-01 00:00:00 000000')
        assert steps[0].duration == timedelta(days=7)

    def test_quarters_overflow_end(self, dts):
        tmfrspec_dict = {
            'range_unit' : 'QUARTER',
            'range_val'  : 1,
            'gran_unit'  : 'WEEK',   # last week to overflows past end by 1 day
            'mode'       : 'CURRENT',
            'reframe_dt' : dts[4],
        }
        steps = self._steps(tmfrspec_dict)
        assert len(steps) == 13
        assert steps[-1].exc_end == dt('2014-04-01 00:00:00 000000')
        assert steps[-1].duration == timedelta(days=6)
        tmfrspec_dict['allow_overflow_end'] = True
        steps = self._steps(tmfrspec_dict)
        assert len(steps) == 13
        assert steps[-1].exc_end == dt('2014-04-02 00:00:00 000000')
        assert steps[-1].duration == timedelta(days=7)

    def test_week1(self, dts):
        steps = self._steps({
            'range_unit' : 'WEEK',
            'range_val'  : 1,
            'gran_unit'  : 'DAY',
            'mode'       : 'CURRENT',
            'reframe_dt' : dts[5],
        })
        assert len(steps) == 7
        assert steps[5].inc_begin == dt('2014-04-18 00:00:00 000000')

    def test_day1(self, dts):
        steps = self._steps({
            'range_unit' : 'DAY',
            'range_val'  : 7,
            'gran_unit'  : 'HOUR',
            'mode'       : 'CURRENT',
            'reframe_dt' : dts[5],
        })
        assert len(steps) == 7*24
        assert steps[5].inc_begin == dt('2014-04-08 05:00:00 000000')

    def test_day2(self, dts):
        steps = self._steps({
            'range_unit' : 'DAY',
            'range_val'  : 1,
            'gran_unit'  : 'MINUTE15',
            'mode'       : 'CURRENT',
            'reframe_dt' : dts[5],
        })
        assert len(steps) == 4*24
        assert steps[5].inc_begin == dt('2014-04-14 01:15:00 000000')

    def test_quarters_smooth1(self, dts):
        tmfrspec_dict = {
            'range_unit' : 'QUARTER',
            'range_val'  : 1,
            'gran_unit'  : 'WEEK',
            'smooth_unit': 'DAY',
            'smooth_val' : 14,
            'mode'       : 'CURRENT',
            'reframe_dt' : dts[4],
        }
        steps = self._steps(tmfrspec_dict)
        assert len(steps) == 13
        assert steps[0].anchor ==    dt('2014-01-01 00:00:00 000000')
        assert steps[1].anchor ==    dt('2014-01-08 00:00:00 000000')
        assert steps[5].anchor ==    dt('2014-02-05 00:00:00 000000')
        assert steps[5].inc_begin == dt('2014-01-29 00:00:00 000000')
        assert steps[5].exc_end ==   dt('2014-02-12 00:00:00 000000')

    def test_accumulate(self, dts):
        steps = self._steps({
            'range_unit' : 'MONTH',
            'range_val'  : 1,
            'gran_unit'  : 'DAY',
            'mode'       : 'CURRENT',
            'reframe_dt' : dts[5],
            'accumulate' : True,
        })
        assert len(steps) == 30
        assert steps[ 5].inc_begin == dt('2014-04-01 00:00:00 000000')
        assert steps[ 5].exc_end ==   dt('2014-04-07 00:00:00 000000')
        assert steps[20].inc_begin == dt('2014-04-01 00:00:00 000000')
        assert steps[20].duration == timedelta(days=21)

    def test_ghosts(self, dts):
        tmfrspec_dict = {
            'range_unit' : 'QUARTER',
            'range_val'  : 1,
            'gran_unit'  : 'WEEK',
            'smooth_unit': 'DAY',
            'smooth_val' : 14,
            'mode'       : 'CURRENT',
            'reframe_dt' : dt('2014-02-14 16:30:45 001234'),
        }
        tmfrspec = framespec.FrameSpec(**tmfrspec_dict)
        #
        steps = list(stepper.Stepper(tmfrspec, ghost=None).steps())
        assert steps[0].anchor == dt('2014-01-01 00:00:00 000000')
        #
        g1 = "Not a Ghost"
        with pytest.raises(TypeError):
            steps = list(stepper.Stepper(tmfrspec, ghost=g1).steps())
        #
        g1 = ghost.Ghost('PREV_PERIOD1')
        str(g1)
        steps = list(stepper.Stepper(tmfrspec, ghost=g1).steps())
        assert steps[0].anchor == dt('2013-10-01 00:00:00 000000')
        #
        g1 = ghost.Ghost('PREV_PERIOD2')
        steps = list(stepper.Stepper(tmfrspec, ghost=g1).steps())
        assert steps[0].anchor == dt('2013-07-01 00:00:00 000000')
        #
        g1 = ghost.Ghost('PREV_YEAR1')
        steps = list(stepper.Stepper(tmfrspec, ghost=g1).steps())
        assert steps[0].anchor == dt('2013-01-01 00:00:00 000000')
        #
        g1 = ghost.Ghost('PREV_YEAR2')
        steps = list(stepper.Stepper(tmfrspec, ghost=g1).steps())
        assert steps[0].anchor == dt('2012-01-01 00:00:00 000000')


    #
    # Internal Helpers
    #

    def _steps(self, tmfrspec_dict, options=dict()):
        """Given dict of FrameSpec attrs, return list of steps."""
        tmfrspec = framespec.FrameSpec(**tmfrspec_dict)
        step1 = stepper.Stepper(tmfrspec)
        for o, v in options.iteritems():
            step1.set_option(o, v)
        steps = list(step1.steps())
        # print "steps=", len(steps), "\n", "\n".join([str(s) for s in steps])
        return steps


