"""
Ax_Metrics - Definition of time ranges for queries.

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


from datetime import datetime, timedelta

from axonchisel.metrics.foundation.ax.obj import AxObj


# ----------------------------------------------------------------------------


# Smallest unit of time (timedelta) that TimeRange can represent
TIMERANGE_PRECISION = timedelta(microseconds=1)


# ----------------------------------------------------------------------------


class TimeRange(AxObj):
    """
    Single time range with beginning/end time to microsecond precision
    and optional anchor point.

    Anchor point commonly refers to the beginning of the period as would
    be labeled on the X-axis of a chart, but may be inside the period
    such as when smoothing is in effect.

    Provides get/set access to beginning and end times with both inclusive
    and exclusive semantics (on same points), with properties:
      - inc_begin
      - exc_begin
      - inc_end
      - exc_end

    Optional anchor (may be None) property:
      - anchor

    TimeRange objects are initially invalid and require setting begin and end
    points before use.
    """

    def __init__(self, **kwargs):
        """
        Initialize, optionally overriding any default properties with kwargs.
        By default, the begin and end times are unspecified, resulting
        in an invalid TimeRange until those attributes are set.
        """
        # Set default state:
        self._anchor    = None  # datetime, internal optional
        self._inc_begin = None  # datetime, internal
        self._exc_end   = None  # datetime, internal

        # Apply initial values from kwargs:
        self._init_kwargs(kwargs, [
            'anchor', 'inc_begin', 'exc_begin', 'inc_end', 'exc_end'
        ])

    #
    # Public Methods
    #

    def is_valid(self):
        """
        Check T/F if TimeRange is valid (has valid begin/end).
        """
        try:
            self.validate()
            return True
        except (TypeError, ValueError) as e:
            return False

    def is_anchored(self):
        """
        Check T/F if TimeRange is valid (has valid begin/end).
        """
        return self.anchor is not None

    def validate(self):
        """
        Validate self.
        Raise TypeError, ValueError if any problems, eg begin/end unspecified.
        """
        if self._inc_begin is None:
            raise ValueError(("TimeRange {self} missing begin point")
                .format(self=self))
        if self._exc_end is None:
            raise ValueError(("TimeRange {self} missing end point")
                .format(self=self))


    #
    # Public Properties
    #

    @property
    def anchor(self):
        """Anchor datetime within range (optional, may be None)."""
        return self._anchor
    @anchor.setter
    def anchor(self, val):
        if val is not None:
            self._assert_type_datetime("anchor", val)
        self._anchor = val

    @property
    def inc_begin(self):
        """Inclusive datetime beginning of range (first moment in)."""
        return self._inc_begin
    @inc_begin.setter
    def inc_begin(self, val):
        self._assert_type_datetime("inc_begin", val)
        self._inc_begin = val

    @property
    def exc_begin(self):
        """Exclusive datetime beginning of range (last moment before)."""
        return self._inc_begin - TIMERANGE_PRECISION
    @exc_begin.setter
    def exc_begin(self, val):
        self._assert_type_datetime("exc_begin", val)
        self._inc_begin = val + TIMERANGE_PRECISION

    @property
    def inc_end(self):
        """Inclusive datetime end of range (last moment in)."""
        return self._exc_end - TIMERANGE_PRECISION
    @inc_end.setter
    def inc_end(self, val):
        self._assert_type_datetime("inc_end", val)
        self._exc_end = val + TIMERANGE_PRECISION

    @property
    def exc_end(self):
        """Exclusive datetime end of range (first moment after)."""
        return self._exc_end
    @exc_end.setter
    def exc_end(self, val):
        self._assert_type_datetime("exc_end", val)
        self._exc_end = val

    @property
    def duration(self):
        """Duration (timedelta) of range, read-only. Return 0 when invalid."""
        if self._exc_end and self._inc_begin:
            return self._exc_end - self._inc_begin
        return 0


    #
    # Internal Methods
    #

    def __unicode__(self):
        return (u"TimeRange({dur} = [{begin}..{end}) anchor {anchor})"
        ).format(
            dur=self.duration, begin=self._inc_begin, end=self._exc_end,
            anchor=self._anchor
        )


    # NOTE: Consider defining comparison operators like __lt__, __ge__, ...
    # See https://docs.python.org/2/reference/datamodel.html#object.__lt__
    # Semantics:
    #   - less/greater than should indicate entire range is older/newer than.
    #   - equal should indicate exact match including anchor point.
    # Thus a TimeRange may be none of equal, less than, or greater than
    # another TimeRange, and that's OK -- it means they overlap somewhere.













