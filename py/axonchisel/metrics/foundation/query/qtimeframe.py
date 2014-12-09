"""
Ax_Metrics - Query component for time frame specification

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


from axonchisel.metrics.foundation.ax.obj import AxObj

from axonchisel.metrics.foundation.chrono.framespec import FrameSpec


# ----------------------------------------------------------------------------


class QTimeFrame(AxObj):
    """
    Query component for time frame specification.
    Wraps complex FrameSpec object which defines query period, granularity,
    smoothing, and more.
    """

    def __init__(self):
        self._tmfrspec = FrameSpec()


    #
    # Public Properties
    #

    @property
    def tmfrspec(self):
        """Wrapped FrameSpec."""
        return self._tmfrspec
    @tmfrspec.setter
    def tmfrspec(self, val):
        self._assert_type("tmfrspec", val, FrameSpec)
        self._tmfrspec = val


    #
    # Public Methods
    #


    #
    # Internal Methods
    #

    def __unicode__(self):
        return u"QTimeFrame({self._tmfrspec})".format(self=self)


