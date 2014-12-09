"""
Ax_Metrics - Series of single data points and their context

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


from axonchisel.metrics.foundation.ax.obj import AxObj

from axonchisel.metrics.foundation.chrono.ghost import Ghost
from axonchisel.metrics.foundation.metricdef.metricdef import MetricDef, FUNCS
from axonchisel.metrics.foundation.chrono.framespec import FrameSpec

from .point import DataPoint


# ----------------------------------------------------------------------------


class DataSeries(AxObj):
    """
    Series of single DataPoints and context: Metric, FrameSpec, Ghost.

    Multiple DataSeries may be represented by a MultiDataSeries.
    """

    def __init__(self, **kwargs):
        """
        Initialize, optionally overriding any default properties with kwargs.
        """
        # Set default state:
        self.id       = ''
        self.query_id = ''
        self.mdef     = MetricDef()
        self.tmfrspec = FrameSpec()
        self.ghost    = None
        self.label    = ""
        self._points  = list()

        # Apply initial values from kwargs:
        self._init_kwargs(kwargs, [
            'id', 'query_id', 'mdef', 'tmfrspec', 'ghost', 'label',
        ])


    #
    # Public Methods
    #

    def count_points(self):
        """Return number of DataPoints."""
        return len(self._points)

    def reset_points(self):
        """Reset DataPoints to empty list."""
        self._points = list()

    def add_point(self, dpoint):
        """Add a valid DataPoint."""
        self._assert_type("dpoint", dpoint, DataPoint)
        dpoint.validate()
        self._points.append(dpoint)

    def add_points(self, dpoints):
        """Add a list of valid DataPoint."""
        for dpoint in dpoints:
            self.add_point(dpoint)

    def get_point(self, idx):
        """
        Return specific 0-based indexed DataPoint.
        Supports negative indexes from tail (-1 = last).
        Raise IndexError if out of range.
        """
        return self._points[idx]

    def iter_points(self):
        """Return an iterator over DataPoints."""
        return iter(self._points)

    def count_missing(self):
        """Return number of points missing data."""
        return sum(1 if dp.is_missing() else 0 for dp in self._points)

    def div_series(self, dseries2):
        """
        Divide each point value by value from same point in other series.
        If either point's value is None, the resulting value will be None.
        If dseries2 is shorter, all unmatched values will be None.
        """
        for i, dp in enumerate(self._points):
            try:
                dp2 = dseries2.get_point(i)
            except IndexError:
                dp2 = None
            if (dp2 is None) or (dp2.value is None):
                dp.value = None
            if dp.value is not None:
                dp.value /= dp2.value

    def reduce(self, mdef_func):
        """
        Reduce the series to a single value by MetricDef func specified.
        Returns value.
        func is a string from:
          axonchisel.metrics.foundation.metricdef.metricdef.FUNCS
        """
        self._assert_type_string("reduce mdef_func", mdef_func)
        self._assert_value("reduce mdef_func", mdef_func, FUNCS.keys())
        vals = [dp.value for dp in self._points]
        func = FUNCS[mdef_func]['reduce']
        return func(vals)


    #
    # Public Properties
    #

    @property
    def id(self):
        """Id of the series."""
        return self._id
    @id.setter
    def id(self, val):
        self._assert_type_string("id", val)
        self._id = val

    @property
    def query_id(self):
        """Optional query_id of the query that produced the series."""
        return self._query_id
    @query_id.setter
    def query_id(self, val):
        self._assert_type_string("query_id", val)
        self._query_id = val

    @property
    def mdef(self):
        """Wrapped MetricDef."""
        return self._mdef
    @mdef.setter
    def mdef(self, val):
        self._assert_type("mdef", val, MetricDef)
        self._mdef = val

    @property
    def tmfrspec(self):
        """Wrapped FrameSpec."""
        return self._tmfrspec
    @tmfrspec.setter
    def tmfrspec(self, val):
        self._assert_type("tmfrspec", val, FrameSpec)
        self._tmfrspec = val

    @property
    def ghost(self):
        """Wrapped Ghost, optional."""
        return self._ghost
    @ghost.setter
    def ghost(self, val):
        if val is not None:
            self._assert_type("ghost", val, Ghost)
        self._ghost = val

    @property
    def label(self):
        """Optional human-readable label for the series."""
        return self._label
    @label.setter
    def label(self, val):
        self._assert_type_string("label", val)
        self._label = val


    #
    # Internal Methods
    #

    def __unicode__(self):
        return (u"{cls}('{self.label}' #{self.id} (Q#{self.query_id}) "+
            "of {self._mdef} over {self._tmfrspec} ghost {self.ghost} "+
            "with {cnt} points: [{points}])"
        ).format(self=self, cls=self.__class__.__name__,
            cnt=self.count_points(),
            points=u", ".join("{0}".format(p.value) for p in self._points)
        )

            

# ----------------------------------------------------------------------------


