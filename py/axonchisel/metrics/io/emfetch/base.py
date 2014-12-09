"""
Ax_Metrics - EMFetch (Extensible Metrics Fetch) Plugin Superclass Base

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import collections

from axonchisel.metrics.foundation.ax.obj import AxObj
from axonchisel.metrics.foundation.ax.plugin import AxPluginBase

from axonchisel.metrics.foundation.chrono.timerange import TimeRange
from axonchisel.metrics.foundation.metricdef.metricdef import MetricDef
from axonchisel.metrics.foundation.data.point import DataPoint

from .tmrange_time_t import TimeRange_time_t
from .interface import EMFetcher


# ----------------------------------------------------------------------------


class EMFetcherBase(EMFetcher, AxPluginBase):
    """
    EMFetch (Extensible Metrics Fetch) Plugin Superclass Base.

    See EMFetcher interface class for detailed docs.
    """

    def __init__(self, mdef, extinfo=None):
        """
        Initialize around specific MetricDef and optional extinfo dict.
        """

        # Default state:
        self._mdef = None      # MetricDef from config
        self._tmrange = None   # TimeRange transient storage per fetch

        # Superclass init:
        AxPluginBase.__init__(self)

        # Validate, store MetricDef in self._mdef:
        self._assert_type("mdef", mdef, MetricDef)
        mdef.validate()    # (raises TypeError, ValueError)
        self._mdef = mdef

        # Pass options to superclass:
        self.configure(options = self.mdef.emfetch_opts, extinfo = extinfo)

    #
    # Public Methods
    #

    def fetch(self, tmrange):
        """
        Invoked by MQEngine to fetch an individual data point.
        May be called multiple times to load multiple data points.
        Validates input, calls plugin_fetch(), validates, returns DataPoint.
        """
        # Validate and cache input:
        self._assert_type("tmrange", tmrange, TimeRange)
        tmrange.validate()
        self._tmrange = TimeRange_time_t(tmrange)

        # Defer to plugin abstract method to fetch:
        dpoint = self.plugin_fetch(tmrange)

        # Validate result DataPoint:
        self._assert_type("result", dpoint, DataPoint)
        return dpoint


    #
    # Public Properties
    #

    @property
    def mdef(self):
        """MetricDef we operate on (get only)."""
        return self._mdef


    #
    # Protected Methods for Subclasses
    #

    def _format_str(self, fmt, what='?', od_defaults = Exception):
        """
        Override from AxPluginBase -
        Format a string using options, extinfo, and extra context (if any).
        Protected wrapper for Python str.format.
        """
        context = dict()
        context['mdef']    = self._mdef
        context['tmrange'] = self._tmrange
        fmt = TimeRange_time_t.patch_format_str(fmt, ('tmrange',))
        return AxPluginBase._format_str(self, fmt,
            context=context, what=what, od_defaults=od_defaults)


    #
    # Internal Methods
    #

    def __unicode__(self):
        return (u"{cls}({self.mdef})"
        ).format(self=self, cls=self.__class__.__name__,
        )


# ----------------------------------------------------------------------------

