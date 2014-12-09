"""
Ax_Metrics - Spec for time frame, measurement granularity, and smoothing

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


from datetime import datetime

from axonchisel.metrics.foundation.ax.obj import AxObj


# ----------------------------------------------------------------------------


# FrameSpec allowed modes
MODES = {
    'CURRENT': {},    # current period (or incl reframe), possibly incomplete
    'LASTWHOLE': {},  # previous completed period
}

# FrameSpec allowed time units
TIME_UNITS = {
    'SECOND': {},
    'MINUTE': {},
    'MINUTE5': {},
    'MINUTE10': {},
    'MINUTE15': {},
    'MINUTE30': {},
    'HOUR': {},
    'DAY': {},
    'WEEK': {},
    'MONTH': {},
    'QUARTER': {},
    'YEAR': {},
}


# ----------------------------------------------------------------------------


class FrameSpec(AxObj):
    """
    Specification of time frame, measurement granularity, and smoothing,
    such as for use in specifying a query.

    A Stepper can take a FrameSpec and yield TimeRanges for each data point.

    Examples representable by FrameSpecs:
      - Last whole month, daily measurements.
      - Current quarter to date, weekly measurements.
      - Last 5 days, hourly measurements.
      - 24 hour period on specific date in past, measurements every 15 minutes.
      - Current month to date, smoothed daily measurements of trailing 7 days.

    Attributes:

      - range_unit:
            Determines rounding granularity of start and stop 
            times and the interpretation of range_val to specify overall 
            duration. Value from TIME_UNITS, e.g. 'MONTH'.

      - range_val:
            Specifies how many range_units are in the period.

      - gran_unit:
            Determines granularity of data points within the range.
            Value from TIME_UNITS, e.g. 'DAY'.
            Without smoothing, each measurement step covers 1 gran_unit
            beginning at each step point.

      - smooth_unit:
            Unit of time used for smoothing extended by smooth_val.
            Ignored if smooth_val is 0.

      - smooth_val:
            If 0, no smoothing is done.  If positive int is specified,
            each measurement step time frame will have the same end it 
            would have otherwise, but the beginning will be
            smooth_val smooth_units back from there (instead of just
            1 gran_unit back).
            Smoothing will be ignored if accumulate is enabled.
            Option allow_overflow_begin affects early steps.

      - mode:
            Determine whether range includes current time (ie "X to date"),
            or previous completed period.
            Value from MODES: 'CURRENT' or 'LASTWHOLE'.

      - reframe_dt:
            If specified, changes period calc to execute as if "now"
            was the datetime specified here.

      - accumulate: True/False  (default = False)
            If True, all steps have their beginning locked to the
            beginning of the overall frame, each growing in size.
            If False (default), each step through the frame is roughly
            the same size and proceeds mostly linearly.
            Accumulate is not compatible with and will override smoothing.

      - allow_overflow_begin: True/False  (default = True)
            If False, steps will never extend beyond the beginning
            of the period, but early steps may be shorter than full frames.
            If True (default), early steps may extend beyond the beginning
            of the period, such as with 30 DAY smoothing combined 
            with WEEK granularity.
            Default is True because reports (especially smoothed) would 
            otherwise see significant initial noise before full size
            smoothing frame existed.

      - allow_overflow_end: True/False    (default = False)
            If False (default), steps will never extend beyond the end
            of the period, but late steps may be shorter than full frames.
            If True, steps may extend beyond the end of the period,
            such as the final step when using WEEK granularity 
            where a QUARTER ends mid-week.
            Default is False because we don't want to report on data
            past the period.  Adding smoothing (even identical to 
            gran_unit) should address lower last frame issues by
            forcing a full size frame (at cost of re-covering part
            of end of previous period).
    """
    
    def __init__(self, **kwargs):
        """
        Initialize, optionally overriding any default properties with kwargs.
        """
        # Set valid default state:
        self.range_unit  = 'MONTH'
        self.range_val   = 1
        self.gran_unit   = 'DAY'
        self.smooth_unit = 'DAY'
        self.smooth_val  = 0
        self.mode        = 'CURRENT'
        self.reframe_dt  = None
        self.accumulate  = False
        self.allow_overflow_begin = True
        self.allow_overflow_end   = False

        # Apply initial values from kwargs:
        self._init_kwargs(kwargs, [
            'range_unit', 'range_val',
            'gran_unit',
            'smooth_unit', 'smooth_val',
            'mode',
            'reframe_dt',
            'accumulate',
            'allow_overflow_begin', 'allow_overflow_end',
        ])


    #
    # Public Methods
    #

    def is_reframed(self):
        return self.reframe_dt is not None

    def is_smoothed(self):
        return self.smooth_val > 0


    #
    # Public Properties
    #

    @property
    def range_unit(self):
        """Duration unit and rounding granularity of start/stop times."""
        return self._range_unit
    @range_unit.setter
    def range_unit(self, val):
        self._assert_type_string("range_unit", val)
        self._assert_value("range_unit", val, TIME_UNITS)
        self._range_unit = val

    @property
    def range_val(self):
        """Specifies how many range_units are in the period. """
        return self._range_val
    @range_val.setter
    def range_val(self, val):
        self._assert_type_int("range_val", val)
        self._range_val = val

    @property
    def gran_unit(self):
        """Granularity of data points within the range."""
        return self._gran_unit
    @gran_unit.setter
    def gran_unit(self, val):
        self._assert_type_string("gran_unit", val)
        self._assert_value("gran_unit", val, TIME_UNITS)
        self._gran_unit = val

    @property
    def smooth_unit(self):
        """Unit of time used for smoothing extended by smooth_val."""
        return self._smooth_unit
    @smooth_unit.setter
    def smooth_unit(self, val):
        self._assert_type_string("smooth_unit", val)
        self._assert_value("smooth_unit", val, TIME_UNITS)
        self._smooth_unit = val

    @property
    def smooth_val(self):
        """Specifies amount of smooth_units to smooth data by, 0=none."""
        return self._smooth_val
    @smooth_val.setter
    def smooth_val(self, val):
        self._assert_type_int("smooth_val", val)
        self._smooth_val = val

    @property
    def mode(self):
        """How to relate to current/reframed time."""
        return self._mode
    @mode.setter
    def mode(self, val):
        self._assert_type_string("mode", val)
        self._assert_value("mode", val, MODES)
        self._mode = val

    @property
    def reframe_dt(self):
        """Reframe "now" as given datetime, or None for real now."""
        return self._reframe_dt
    @reframe_dt.setter
    def reframe_dt(self, val):
        if val is not None:
            self._assert_type_datetime("reframe_dt", val)
        self._reframe_dt = val

    @property
    def accumulate(self):
        """Lock all steps to beginnining time frame?"""
        return self._accumulate
    @accumulate.setter
    def accumulate(self, val):
        self._assert_type_bool("accumulate", val)
        self._accumulate = val

    @property
    def allow_overflow_begin(self):
        """Allow steps to extend beyond beginning of period?"""
        return self._allow_overflow_begin
    @allow_overflow_begin.setter
    def allow_overflow_begin(self, val):
        self._assert_type_bool("allow_overflow_begin", val)
        self._allow_overflow_begin = val

    @property
    def allow_overflow_end(self):
        """Allow steps to extend beyond end of period?"""
        return self._allow_overflow_end
    @allow_overflow_end.setter
    def allow_overflow_end(self, val):
        self._assert_type_bool("allow_overflow_end", val)
        self._allow_overflow_end = val


    #
    # Internal Methods
    #

    def __unicode__(self):
        return (u"FrameSpec(every {self.gran_unit} "+
            "for {self.range_val} {self.range_unit}s, "+
            "{self.mode}, reframe {self.reframe_dt}, "+
            "smooth {smooth}, accum {accum})"
            ).format(self=self, smooth=(
                "{self.smooth_val} {self.smooth_unit}s".format(self=self)
                ) if self.smooth_val else "None",
                accum=("Y" if self.accumulate else "N"),
        )


