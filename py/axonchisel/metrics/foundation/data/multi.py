"""
Ax_Metrics - Container for multiple DataSeries

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


from axonchisel.metrics.foundation.ax.obj import AxObj

from .series import DataSeries


# ----------------------------------------------------------------------------


class MultiDataSeries(AxObj):
    """
    Data container for multiple DataSeries.
    Each DataSeries contains context and multiple 2D DataPoints.
    """
    def __init__(self):
        self._series        = list()  # list of DataSeries


    #
    # Public Methods
    #
    
    def add_series(self, series1):
        """
        Add DataSeries to list.
        """
        self._assert_type("series", series1, DataSeries)
        self._series.append(series1)

    def count_series(self):
        """
        Returns total number of seriess in list.
        """
        return len(self._series)

    def iter_series(self):
        """
        Return an iterator over series.
        """
        return iter(self._series)

    def iter_primary_series(self):
        """
        Return an iterator over primary (non-ghost) series.
        """
        return (ds for ds in self._series if ds.ghost is None)

    def iter_ghost_series(self):
        """
        Return an iterator over ghost series.
        """
        return (ds for ds in self._series if ds.ghost is not None)

    def get_series(self, idx):
        """
        Return specific 0-based indexed DataSeries.
        Supports negative indexes from tail (-1 = last).
        Raise IndexError if out of range.
        """
        return self._series[idx]

    def get_series_by_id(self, id):
        """
        Returns specified DataSeries, or raise KeyError if not found.
        """
        for s in self._series:
            if s.id == id:
                return s
        raise KeyError("Series #{id} not in {set}".format(id=id, set=self))


    #
    # Internal Methods
    #

    def __unicode__(self):
        return (u"MultiDataSeries('{len} DataSeries: [{series}]')"
        ).format(len=len(self._series),
            series=u", ".join(map(unicode, self._series))
        )





