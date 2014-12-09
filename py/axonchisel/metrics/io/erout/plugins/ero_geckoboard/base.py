"""
Ax_Metrics - EROut geckoboard base plugin

Superclass for Geckoboard JSON output for various charts for use with
http://www.geckoboard.com.

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import time

from axonchisel.metrics.foundation.ax.dictutil import OrderedDict
from axonchisel.metrics.foundation.chrono.stepper import Stepper

from axonchisel.metrics.io.erout.base import EROutBase

import logging
log =  logging.getLogger(__name__)


# ----------------------------------------------------------------------------


class EROut_geckoboard(EROutBase):
    """
    Superclass EROut (Extensible Report Outputter) Plugin for geckoboard.
    Adds JSON-serializable output to extinfo['jout'] dict.

    Subclasses should define plugin_output() and immediately set
    self._qfdomain to the str name of the key in QFormat under which
    its format can be found.
    """

    #
    # Abstract Method Implementations
    #

    # abstract
    def plugin_create(self):
        """
        Invoked once to allow plugin to setup what it needs.
        """
        self._prep_output()

    # abstract
    def plugin_destroy(self):
        """
        Invoked once to allow plugin to clean up after itself.
        """
        pass


    #
    # Protected Methods for Subclasses
    #

    def _prep_output(self):
        """Prepare jout output."""
        self.jout = self.plugin_extinfo('jout')
        if self.jout.get('item') is None:
            self.jout['item'] = []

    def _qformat_get(self, key, default):
        """Proxy for QFormat.get that allows for missing Query."""
        if not self.query:
            return default
        return self.query.qformat.get(self._qfdomain, key, default)

    @staticmethod
    def _round_sigdigs(val, ndigits):
        """Round float value to specified number of significant digits."""
        fmt = "%%.%de" % (ndigits - 1)
        return float(fmt % val)

    @staticmethod
    def _is_round(val):
        """Return bool indicating if float val is a round integer."""
        return (int(val) == val)


# ----------------------------------------------------------------------------
