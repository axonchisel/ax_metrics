"""
Ax_Metrics - EROut (Extensible Report Outputter) Plugin Superclass Base

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import collections
import time
from datetime import datetime

from axonchisel.metrics.foundation.ax.obj import AxObj
from axonchisel.metrics.foundation.ax.plugin import AxPluginBase

from axonchisel.metrics.foundation.query.query import Query
from axonchisel.metrics.foundation.data.multi import MultiDataSeries

from .interface import EROut


# ----------------------------------------------------------------------------


class EROutBase(EROut, AxPluginBase):
    """
    ERout (Extensible Report Outputter) Plugin Superclass Base.

    See EROut interface class for detailed docs.
    """

    def __init__(self, extinfo=None):
        """
        Initialize around optional extinfo dict.
        """

        # Default state:
        self._query = None    # Query transient storage per output
        self._mdseries = None # MultiDataSeries transient storage per output

        # Superclass init:
        AxPluginBase.__init__(self)

        # Pass options to superclass:
        self.configure(extinfo = extinfo)


    #
    # Public Methods
    #

    def output(self, mdseries, query=None):
        """
        Invoked to output MultiDataSeries as specified, in optional 
        query context.
        May be called multiple times to output multiple MultiDataSeries.
        Validates input, calls plugin_output(), validates, returns DataPoint.
        """
        # Validate and cache input:
        self._assert_type("mdseries", mdseries, MultiDataSeries)
        self._mdseries = mdseries
        if query is not None:
            self._assert_type("query", query, Query)
            query.validate()    # (raises TypeError, ValueError)
        self._query = query

        # Defer to plugin abstract method to output:
        self.plugin_output(mdseries, query=query)


    #
    # Public Properties
    #

    @property
    def query(self):
        """Query our data originally came from (get only). May be None."""
        return self._query

    @property
    def mdseries(self):
        """MultiDataSeries we are outputting (get only)."""
        return self._mdseries


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
        context['query']   = self._query
        return AxPluginBase._format_str(self, fmt,
            context=context, what=what, od_defaults = od_defaults)

    def _format_datetime(self, fmt, dt):
        """
        Helper to format a datetime obj using strftime.
        If dt is None, returns empty string ("").
        Handles "%s" format (time_t) manually since this is not supported
        on all platforms.
        """
        if dt is None:
            return ""
        self._assert_type("datetime", dt, datetime)
        if fmt == "%s":
            return int(time.mktime(dt.timetuple()))  # datetime to time_t
        return dt.strftime(fmt)


    #
    # Internal Methods
    #

    def __unicode__(self):
        return (u"{cls}({self._mdseries})"
        ).format(self=self, cls=self.__class__.__name__,
        )


# ----------------------------------------------------------------------------

