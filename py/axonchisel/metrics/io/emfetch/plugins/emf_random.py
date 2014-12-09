"""
Ax_Metrics - EMFetch plugin 'random'

Mostly for testing purposes. Provides random data values.

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import random

from axonchisel.metrics.foundation.data.point import DataPoint

from ..base import EMFetcherBase


# ----------------------------------------------------------------------------


class EMFetcher_random(EMFetcherBase):
    """
    EMFetch (Extensible Metrics Fetch) Plugin 'random'.
    Mostly for testing purposes. Provides random data values.
    """

    #
    # Abstract Method Implementations
    #

    # abstract
    def plugin_create(self):
        """
        Invoked once by MQEngine to allow plugin to setup what it needs.
        Always called before any fetch() invocations.
        """
        pass

    # abstract
    def plugin_destroy(self):
        """
        Invoked once by MQEngine to allow plugin to clean up after itself.
        Always called after create() and any fetch() invocations, assuming
        no fatal errors occurred.
        """
        pass

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
        dpoint = DataPoint(tmrange=tmrange)
        vmin = self.plugin_option('random.min', 0)
        vmax = self.plugin_option('random.max', 100)
        val = vmin + (random.random() * (vmax-vmin))
        if self.plugin_option('random.round', False):
            val = int(round(val))
        dpoint.value = val
        return dpoint


# ----------------------------------------------------------------------------


