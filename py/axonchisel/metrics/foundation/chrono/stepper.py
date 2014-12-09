"""
Ax_Metrics - Logic for generating TimeFrame steps for a query.

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


from datetime import *

from axonchisel.metrics.foundation.ax.obj import AxObj

from . import dtmath
from .timerange import TimeRange
from .framespec import FrameSpec
from .ghost import Ghost


# ----------------------------------------------------------------------------


# What we consider the first day of the week, as offset from Sunday
WEEK_FIRST_DAY = 0

# Internal: map from FrameSpec UNIT to dtmath begin_* function
_ROUND_FUNC_BY_UNIT = {
    'SECOND':   dtmath.begin_second,
    'MINUTE':   dtmath.begin_minute,
    'MINUTE5':  dtmath.begin_minute5,
    'MINUTE10': dtmath.begin_minute10,
    'MINUTE15': dtmath.begin_minute15,
    'MINUTE30': dtmath.begin_minute30,
    'HOUR':     dtmath.begin_hour,
    'DAY':      dtmath.begin_day,
    'WEEK':     dtmath.begin_week,
    'MONTH':    dtmath.begin_month,
    'QUARTER':  dtmath.begin_quarter,
    'YEAR':     dtmath.begin_year,
}

# Internal: map from FrameSpec UNIT to dtmath add_* function
_ADD_FUNC_BY_UNIT = {
    'SECOND':   dtmath.add_seconds,
    'MINUTE':   dtmath.add_minutes,
    'MINUTE5':  dtmath.add_minute5s,
    'MINUTE10': dtmath.add_minute10s,
    'MINUTE15': dtmath.add_minute15s,
    'MINUTE30': dtmath.add_minute30s,
    'HOUR':     dtmath.add_hours,
    'DAY':      dtmath.add_days,
    'WEEK':     dtmath.add_weeks,
    'MONTH':    dtmath.add_months,
    'QUARTER':  dtmath.add_quarters,
    'YEAR':     dtmath.add_years,
}


# ----------------------------------------------------------------------------


class Stepper(AxObj):
    """
    Given a FrameSpec, provides TimeRange measurement steps indicated.

    Each TimeRange step specifies the time parameters for a data point
    in a report.
    """

    def __init__(self, tmfrspec, ghost=None):
        """
        Initialize around FrameSpec and optional Ghost.
        """
        # Set valid default state:
        self._tmfrspec = None
        self._ghost = None

        # Apply initial values from args:
        self.tmfrspec = tmfrspec
        self.ghost = ghost


    #
    # Public Methods
    #

    def analyze(self):
        """
        Analyze parameters, bind data to self, and return dict.
        Invoked by steps(), but can be called manually too.
        Returned dict will have keys:
          - tmrange : TimeRange with begin/end time and anchor
        """
        self._bind_dt_funcs()
        self._bind_dtinc_start()
        self._bind_dtexc_end()
        tmrange = TimeRange(
            inc_begin=self._dtinc_start,
            exc_end=self._dtexc_end,
            anchor=self._dtwithin,
        )
        return {
            'tmrange': tmrange,
        }

    def steps(self):
        """
        Yield a series of TimeRange objects representing FrameSpec steps.
        Each TimeRange is the period over which the measurement point 
        should be queried, with its anchor representing the time label.
        """

        tmfrspec = self.tmfrspec

        # Analyze parameters and bind data to self:
        self.analyze()

        # Iterate to build and yield each step:
        dtidx = self._dtinc_start
        while dtidx < self._dtexc_end:

            # Calc anchor:
            dtidx_anchor = dtidx

            # Calc step end:
            dtidx_exc_end = self._fn_addgran(dtidx, 1)
            if not tmfrspec.allow_overflow_end:
                if dtidx_exc_end > self._dtexc_end:
                    dtidx_exc_end = self._dtexc_end

            # Calc step begin, applying optional smoothing, accumulation:
            dtidx_inc_begin = dtidx
            if tmfrspec.accumulate:
                dtidx_inc_begin = self._dtinc_start
            else:
                if tmfrspec.is_smoothed():
                    dtidx_inc_begin = self._fn_addsmooth(
                        dtidx_exc_end, -tmfrspec.smooth_val)
                if not tmfrspec.allow_overflow_begin:
                    if dtidx_inc_begin < self._dtinc_start:
                        dtidx_inc_begin = self._dtinc_start

            # Construct and yield TimeRange:
            tmrange = TimeRange(
                anchor    = dtidx_anchor,
                inc_begin = dtidx_inc_begin,
                exc_end   = dtidx_exc_end)
            yield tmrange

            # Advance to next step:
            dtidx = self._fn_addgran(dtidx, 1)


    #
    # Public Properties
    #

    @property
    def tmfrspec(self):
        """FrameSpec defining frame to step through."""
        return self._tmfrspec
    @tmfrspec.setter
    def tmfrspec(self, val):
        self._assert_type("tmfrspec", val, FrameSpec)
        self._tmfrspec = val

    @property
    def ghost(self):
        """Optional Ghost relative alias."""
        return self._ghost
    @ghost.setter
    def ghost(self, val):
        if val is not None:
            self._assert_type("ghost", val, Ghost)
        self._ghost = val
    def is_ghost(self, gtype):
        """Return True/False indicating if has Ghost of specific type."""
        return self.ghost and (self.ghost.gtype == gtype)


    #
    # Internal Methods
    #

    def _bind_dt_funcs(self):
        """Bind to self: dt funcs based on FrameSpec units"""

        tmfrspec = self.tmfrspec

        # Prep, inspecting FrameSpec and
        # binding math functions based on specified units:
        fn_round     = _ROUND_FUNC_BY_UNIT.get(tmfrspec.range_unit)
        fn_add       = _ADD_FUNC_BY_UNIT.get(tmfrspec.range_unit)
        fn_addgran   = _ADD_FUNC_BY_UNIT.get(tmfrspec.gran_unit)
        fn_addsmooth = _ADD_FUNC_BY_UNIT.get(tmfrspec.smooth_unit)

        # Any of these exceptions are implementation errors in this library,
        # as the FrameSpec should not have allowed unsupported data in
        # the first place:
        def _impl_error(msg):
            return ValueError("Implementation Error! "+msg)
        if not (fn_round and fn_add):
            raise _impl_error("FrameSpec range unit '{0}' missing add/round fn"
                .format(tmfrspec.range_unit))
        if not (fn_addgran):
            raise _impl_error("FrameSpec gran unit '{0}' missing add/round fn"
                .format(tmfrspec.gran_unit))
        if tmfrspec.is_smoothed() and not (fn_addsmooth):
            raise _impl_error("FrameSpec smooth unit '{0}' missing smooth fn"
                .format(tmfrspec.smooth_unit))

        # Bind:
        self._fn_round     = fn_round
        self._fn_add       = fn_add
        self._fn_addgran   = fn_addgran
        self._fn_addsmooth = fn_addsmooth

    def _bind_dtinc_start(self):
        """Bind to self: dtinc_start inclusive begin time and dtwithin."""

        tmfrspec = self.tmfrspec

        # Choose raw unrounded context time, either now or explicit reframed:
        dtwithin = tmfrspec.reframe_dt
        if dtwithin is None:
            dtwithin = datetime.now()

        # Round down dtwithin to range_unit:
        if tmfrspec.range_unit == 'WEEK':
            dtwithin = self._fn_round(dtwithin, day0_sunday_ofs=WEEK_FIRST_DAY)
        else:
            dtwithin = self._fn_round(dtwithin)

        # Rewind range_val range_units to find beginning of range we're in:
        dtinc_start = dtwithin
        if tmfrspec.range_val > 1:
            dtinc_start = self._fn_add(dtinc_start, -(tmfrspec.range_val - 1))

        # Handle LASTWHOLE mode to rewind to previous completed range:
        if tmfrspec.mode == 'LASTWHOLE':
            dtinc_start = self._fn_add(dtinc_start, -1)

        # Handle Ghost:
        if self.is_ghost('PREV_PERIOD1'):
            dtinc_start = self._fn_add(dtinc_start, -1)
        elif self.is_ghost('PREV_PERIOD2'):
            dtinc_start = self._fn_add(dtinc_start, -2)
        elif self.is_ghost('PREV_YEAR1'):
            dtinc_start = dtmath.add_years(dtinc_start, -1)
        elif self.is_ghost('PREV_YEAR2'):
            dtinc_start = dtmath.add_years(dtinc_start, -2)

        # Bind:
        self._dtinc_start = dtinc_start
        self._dtwithin = dtwithin


    def _bind_dtexc_end(self):
        """Bind to self: dtexc_end exclusive end time."""

        tmfrspec = self.tmfrspec

        # Calc dtend (exclusive) based on dtinc_start:
        dtexc_end = self._fn_add(self._dtinc_start, tmfrspec.range_val)

        # Bind:
        self._dtexc_end = dtexc_end

    def __unicode__(self):
        return (u"Stepper({self.tmfrspec} ghost {self.ghost}"
            ).format(self=self)

            

