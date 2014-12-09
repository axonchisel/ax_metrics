"""
Ax_Metrics - EMFetch (Extensible Metrics Fetch) Plugin Interface

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


from axonchisel.metrics.foundation.ax.plugin import AxPlugin


# ----------------------------------------------------------------------------


class EMFetcher(AxPlugin):
    """
    EMFetch (Extensible Metrics Fetch) Plugin Interface.

    MQEngine uses EMFetch plugins to access raw time-indexed metrics data
    for each data point.
    Implementations provide access to various data sources by overriding the
    plugin_fetch() abstract method.

    See AxPlugin and AxPluginBase for architecture details.

    Additional Parameters:

      - mdef : definition of metric to query.
        (axonchisel.metrics.foundation.metricdef.metricdef.MetricDef)
    """

    #
    # Abstract Methods
    #

    # abstract
    def __init__(self, mdef, extinfo=None):
        """
        Initialize around specific MetricDef and optional extinfo dict.
        """
        raise NotImplementedError("EMFetcher abstract superclass")

    # abstract
    def plugin_fetch(self, tmrange):
        """
        EMFetcher plugins must implement this abstract method.
        Invoked by fetch() after parameters are validated.
        
        Returns a single DataPoint.
            (axonchisel.metrics.foundation.data.point.DataPoint)

        Parameters:

          - tmrange : specification of time range to gather data for.
            (axonchisel.metrics.foundation.chrono.timerange.TimeRange)
            Also available in TimeRange_time_t format as self._tmrange.
        """
        raise NotImplementedError("EMFetcher abstract superclass")




