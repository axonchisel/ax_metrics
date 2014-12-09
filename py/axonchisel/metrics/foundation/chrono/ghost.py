"""
Ax_Metrics - Relative "ghost" alias specification

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


from axonchisel.metrics.foundation.ax.obj import AxObj


# ----------------------------------------------------------------------------


# Ghost alowed types
GHOST_TYPES = {
    'PREV_PERIOD1': {}, # previous period
    'PREV_PERIOD2': {}, # period before previous period
    'PREV_YEAR1': {},   # same period 1 year ago
    'PREV_YEAR2': {},   # same period 2 years ago
}


# ----------------------------------------------------------------------------


class Ghost(AxObj):
    """
    Specification of relative "ghost" time.

    Usually used 

    """
    
    def __init__(self, gtype='PREV_PERIOD1'):
        """
        Initialize, optionally overriding any default properties with kwargs.
        """
        # Set valid default state:
        self.gtype       = 'PREV_PERIOD1'

        # Apply initial values from kwargs:
        self.gtype = gtype


    #
    # Public Properties
    #

    @property
    def gtype(self):
        """Ghost type."""
        return self._gtype
    @gtype.setter
    def gtype(self, val):
        self._assert_type_string("gtype", val)
        self._assert_value("gtype", val, GHOST_TYPES)
        self._gtype = val


    #
    # Internal Methods
    #

    def __unicode__(self):
        return (u"Ghost({self.gtype})").format(self=self)


