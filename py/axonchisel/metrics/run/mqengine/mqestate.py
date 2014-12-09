"""
Ax_Metrics - MQEngine State encapsulation

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import copy
from datetime import datetime

from axonchisel.metrics.foundation.ax.obj import AxObj

from axonchisel.metrics.foundation.chrono.framespec import FrameSpec
from axonchisel.metrics.foundation.metricdef.metset import MetSet
from axonchisel.metrics.foundation.data.point import DataPoint
from axonchisel.metrics.foundation.data.series import DataSeries 
from axonchisel.metrics.foundation.data.multi import MultiDataSeries 
from axonchisel.metrics.foundation.query.query import Query


# ----------------------------------------------------------------------------


class MQEState(AxObj):
    """
    MQEngine state encapsulation.
    Lifecycle: Should be reset() before each query.
    """

    def __init__(self, mqe):
        """Init with back pointer to parent MQEngine."""
        # Set valid default state:
        self._mqe = None
        self.reset()

        # Apply initial values from args:
        self.mqe = mqe


    #
    # Public Methods
    #

    def reset(self, query=None):
        """Reset state, to allow new queries."""
        self.mdseries  = MultiDataSeries()  # current results accumulation
        self._query    = None
        self._tmfrspec = None
        if query:
            self.query    = query              # current Query obj

    def pin_tmfrspec(self):
        """
        Saves pinned (fixed reframe_dt) copy of Query's FrameSpec.
        Ensures all step sequences run over same time frame even if some
        take a long time to execute (because "now" doesn't change).
        """
        tmfrspec = copy.deepcopy(self.query.qtimeframe.tmfrspec)
        if tmfrspec.reframe_dt is None:
            tmfrspec.reframe_dt = datetime.now()
        self.tmfrspec = tmfrspec


    #
    # Public Properties
    #

    @property
    def query(self):
        """Query currently working on."""
        return self._query
    @query.setter
    def query(self, val):
        self._assert_type("query", val, Query)
        self._query = val

    @property
    def tmfrspec(self):
        """Pinned FrameSpec (adjusted from Query)."""
        return self._tmfrspec
    @tmfrspec.setter
    def tmfrspec(self, val):
        self._assert_type("tmfrspec", val, FrameSpec)
        self._tmfrspec = val

    @property
    def mdseries(self):
        """MultiDataSeries accumulating data into."""
        return self._mdseries
    @mdseries.setter
    def mdseries(self, val):
        self._assert_type("mdseries", val, MultiDataSeries)
        self._mdseries = val


    #
    # Internal Methods
    #

    def __unicode__(self):
        return (u"MQEState()"
        ).format(self=self)


