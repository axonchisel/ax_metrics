"""
Ax_Metrics - EROut plugin 'geckoboard_meter'

Writes Geckoboard JSON output for various charts for use with
http://www.geckoboard.com.

Contents:
 - EROut_geckoboard_meter        - speedometer style meter

See:
 - https://developer.geckoboard.com/#geck-o-meter

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


from .base import EROut_geckoboard

import logging
log =  logging.getLogger(__name__)


# ----------------------------------------------------------------------------


class EROut_geckoboard_meter(EROut_geckoboard):
    """
    EROut (Extensible Report Outputter) Plugin for Geckoboard "Gecko-o-meter".
    Adds JSON-serializable output to extinfo['jout'] dict.

    Typical usage is with non-collapsed query, default 'LAST' reduce function.
    If min/max is provided by QFormat, it is used as specified.
    Otherwise meter min/max is automatically determined by the min/max
    found in all data and ghost series.
    Min or max can be specified independently. E.g. min may be explicitly
    pegged at 0, while max is allowed to be auto-computed from data.

    Note that goal (if any) specified in Geckoboard widget config must be 
    in min/max range, or the widget renders as an error. Thus if explicit
    goal is used in Geckoboard, the min/max should be defined explicitly too
    (unless possible data is predictable).

    QFormat support (under 'geckoboard_meter' or '_default'):
        reduce      : (optional) Function from metricdef.FUNCS to reduce
                                 series with. Default 'LAST'.
        min         : (optional) Meter min value. Default: based on all series.
        max         : (optional) Meter max value. Default: based on all series.

    More info:
     - https://developer.geckoboard.com/#geck-o-meter

    Example JSON:
        {
          "item": 23,
          "min": {
            "value": 10
          },
          "max": {
            "value": 30
          }
        }
    """

    #
    # Abstract Method Implementations
    #

    # abstract
    def plugin_output(self, mdseries, query=None):
        """
        EROut plugins must implement this abstract method.
        Invoked to output MultiDataSeries as specified.
        Returns nothing. Output target should be configured separately.
        """
        log.debug("Outputting %s for query %s", mdseries, query)
        self._qfdomain = 'geckoboard_meter'

        # Write item from primary:
        self._write_primary()

        # Write min/max:
        self._write_min_max()


    #
    # Internal Methods
    #

    def _write_primary(self):
        """
        Write the primary value to jout.
        Reduces first DataSeries.
        """
        
        # Get primary value from first DataSeries:
        reduce_func = self._qformat_get('reduce', 'LAST')
        dseries = self.mdseries.get_series(0)
        value = dseries.reduce(reduce_func)

        # Add value:
        self.jout['item'] = value

    def _write_min_max(self):
        """
        Write the meter min/max values.
        """
        self._write_min()
        self._write_max()

    def _write_min(self):
        """
        Compute and write the meter min value.
        """
        # Initially check for explicit min:
        minval = self._qformat_get('min', None)
        
        # If no explicit minval, compute it from series:
        if minval is None:
            for dseries in self.mdseries.iter_series():
                log.warn("MINCHECK %s, %s", minval, dseries)
                ds_minval = dseries.reduce('MIN')
                if minval is None:
                    minval = ds_minval
                else:
                    minval = min(minval, ds_minval)

        # Write min val:
        self.jout['min'] = { 'value': minval }

    def _write_max(self):
        """
        Compute and write the meter max value.
        """
        # Initially check for explicit max:
        maxval = self._qformat_get('max', None)
        
        # If no explicit maxval, compute it from series:
        if maxval is None:
            for dseries in self.mdseries.iter_series():
                ds_maxval = dseries.reduce('MAX')
                if maxval is None:
                    maxval = ds_maxval
                else:
                    maxval = max(maxval, ds_maxval)

        # Write max val:
        self.jout['max'] = { 'value': maxval }


