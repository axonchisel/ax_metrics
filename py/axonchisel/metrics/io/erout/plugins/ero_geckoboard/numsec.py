"""
Ax_Metrics - EROut plugins for Geckoboard Number + Secondary and variants.

Writes Geckoboard JSON output for various charts for use with
http://www.geckoboard.com.

Contents:
 - EROut_geckoboard_numsec       - basic number with text (and superclass)
 - EROut_geckoboard_numsec_comp  - number plus comparison
 - EROut_geckoboard_numsec_trend - number plus trend sparkline

See:
 - https://developer.geckoboard.com/#number-and-secondary-stat

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


from .base import EROut_geckoboard

import logging
log =  logging.getLogger(__name__)


# ----------------------------------------------------------------------------


class EROut_geckoboard_numsec(EROut_geckoboard):
    """
    EROut (Extensible Report Outputter) Plugin for Geckoboard number+secondary
    basic usage type and superclass for advanced number+secondary EROuts.
    Adds JSON-serializable output to extinfo['jout'] dict.

    Typical usage is with collapsed query and default 'LAST' reduce function.
    Non-collapsed queries with other reduce functions may be used too.

    QFormat support (under 'geckoboard_numsec' or '_default'):
        reduce      : (optional) Function from metricdef.FUNCS to reduce
                                 series with. Default 'LAST'.
        title       : (optional) Text field, shown only if no comparison
        prefix      : (Optional) prefix for value, e.g. "$"

    More info:
     - https://developer.geckoboard.com/#number-and-secondary-stat

    Example JSON:
        {
          "item": [
            {
              "text": "Revenue yesterday",
              "value": 123,
              "prefix": "$"
            }
          ]
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
        self._qfdomain = 'geckoboard_numsec'

        # Write options:
        self._write_options()

        # Write item from primary:
        reduce_func = self._qformat_get('reduce', 'LAST')
        self._write_primary(reduce_func=reduce_func)

    #
    # Protected Methods for Subclasses
    #

    def _write_options(self):
        """
        Write options to jout.
        Note that we support options here useful to our subclasses but 
        not necessarily to this class itself.
        """
        if self.query:
            if self.query.qdata.get_qmetric(0).impact == 'NEGATIVE':
                self.jout['reverse'] = True
            if self._qformat_get('absolute', False):
                self.jout['absolute'] = True
            try:
                qformat = self.query.qformat
                self.jout['prefix'] = qformat.get(self._qfdomain, 'prefix')
            except KeyError:
                pass

    def _write_primary(self, reduce_func):
        """
        Write the primary value to jout.
        Uses last point of first DataSeries.
        """
        
        # Get primary value from first DataSeries:
        dseries = self.mdseries.get_series(0)
        value = dseries.reduce(reduce_func)

        # Add value:
        item = { 'value': value }
        item['text'] = self._qformat_get('title', "")
        self.jout['item'].append(item)



# ----------------------------------------------------------------------------


class EROut_geckoboard_numsec_comp(EROut_geckoboard_numsec):
    """
    EROut (Extensible Report Outputter) Plugin for Geckoboard number+secondary
    stat with comparison.
    Adds JSON-serializable output to extinfo['jout'] dict.

    Two values are attempted, first the primary value, then the comparison.
    Item values are obtained first from first DataSeries (reduced),
    then from the first Ghost DataSeries (reduced).
    Geckoboard only wants to see 1 or 2 values, so either invoke with a single
    query with ghosts, or invoke with 2 queries without ghosts.
    Once 2 values are obtained, additional values are ignored.

    Typical usage is with collapsed query and default 'LAST' reduce function.
    Non-collapsed queries with other reduce functions may be used too.

    QFormat support (under 'geckoboard_numsec_comp' or '_default'):
        reduce      : (optional) Function from metricdef.FUNCS to reduce
                                 series with. Default 'LAST'.
        title       : (optional) Text field, shown only if no comparison
        absolute    : (optional) true for absolute comparison
        prefix      : (Optional) prefix for value, e.g. "$"

    More info:
     - https://developer.geckoboard.com/#number-and-secondary-stat
     - https://developer.geckoboard.com/#comparison-example

    Example JSON:
        {
          "item": [
            {
              "value": 142
            },
            {
              "value": 200
            }
          ]
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
        self._qfdomain = 'geckoboard_numsec_comp'

        # Write options:
        self._write_options()

        # Write item from primary and ghost (as long as we're not maxed):
        if self._has_max_items():
            return
        reduce_func = self._qformat_get('reduce', 'LAST')
        self._write_primary(reduce_func=reduce_func)
        if self._has_max_items():
            return
        self._write_comparison()

    #
    # Internal Methods
    #

    def _has_max_items(self):
        """Return bool indicating if we've accumulated max (2) item values."""
        return len(self.jout['item']) >= 2

    def _write_comparison(self):
        """
        Write the comparison value to jout.
        Reduces first Ghost DataSeries.
        If no ghosts found, no comparison value is written at this point,
        but if subsequent query outputs are fed through this same
        EROut instance, the next one may provide comparison via its 
        actual data.
        """
        
        # Find first ghost series:
        try:
            ds_ghost = next(self.mdseries.iter_ghost_series())
        except StopIteration:
            # No additional (ghost) series, so leave it at that.
            return

        # Reduce ghost series:
        reduce_func = self._qformat_get('reduce', 'LAST')
        value = ds_ghost.reduce(reduce_func)

        # Add value:
        item = { 'value': value }
        self.jout['item'].append(item)


# ----------------------------------------------------------------------------


class EROut_geckoboard_numsec_trend(EROut_geckoboard_numsec):
    """
    EROut (Extensible Report Outputter) Plugin for Geckoboard number+secondary
    stat with trendline.
    Adds JSON-serializable output to extinfo['jout'] dict.

    Item value is obtained first first DataSeries, reduced.
    Trend values are obtained from entire first DataSeries.
    Only first DataSeries is used.
    The default reduce function is SUM, which presents the primary stat
    as the sum of the trend points.  For some situations this may not
    be appropriate, and LAST or other reduce funcs may be provided.

    Unlike most other numsec EROuts, collapse mode should not be enabled,
    since we actually care about the data points here.
    Ghosts however should typically be disabled, since they are ignored.

    QFormat support (under 'geckoboard_numsec_trend' or '_default'):
        reduce      : (optional) Function from metricdef.FUNCS to reduce
                                 series with. Default 'SUM'.
        title       : (optional) Text field, shown only if no comparison
        prefix      : (optional) prefix for value, e.g. "$"

    More info:
     - https://developer.geckoboard.com/#number-and-secondary-stat
     - https://developer.geckoboard.com/#trendline-example

    Example JSON:
        {
          "item": [
            {
              "text": "Past 7 days",
              "value": "274057"
            },
            [
              "38594",
              "39957",
              "35316",
              "35913",
              "36668",
              "45660",
              "41949"
            ]
          ]
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
        self._qfdomain = 'geckoboard_numsec_trend'

        # Write options:
        self._write_options()

        # Write item from primary:
        reduce_func = 'SUM'
        if self.query:
            reduce_func = self._qformat_get('reduce', reduce_func)
        self._write_primary(reduce_func=reduce_func)

        # Write trend values:
        self._write_trend()

    #
    # Internal Methods
    #

    def _write_trend(self):
        """
        Write the trend values to jout.
        Uses all the data points of the first DataSeries.
        """

        # Get all values from first DataSeries:
        values = [dp.value for dp in self.mdseries.get_series(0).iter_points()]

        # Add values:
        self.jout['item'].append(values)


# ----------------------------------------------------------------------------






