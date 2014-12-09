"""
Ax_Metrics - EROut plugin 'geckoboard_rag'

Writes Geckoboard JSON output for various charts for use with
http://www.geckoboard.com.

Contents:
 - EROut_geckoboard_rag        - read/amber/green display of (1-)3 numbers

See:
 - https://developer.geckoboard.com/#rag

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


from .base import EROut_geckoboard

import logging
log =  logging.getLogger(__name__)


# ----------------------------------------------------------------------------


class EROut_geckoboard_rag(EROut_geckoboard):
    """
    EROut (Extensible Report Outputter) Plugin for Geckoboard RAG.
    Adds JSON-serializable output to extinfo['jout'] dict.

    Typical usage is with 1 collapsed query with 3 QMetrics,
    or several collapsed queries totalling 3 QMetrics,
    default 'LAST' reduce function, and ghosts disabled.
    This prevent needless queries from running.
    Non-collapsed queries with other reduce functions may be used too.

    The first 3 data series passed in to this EROut are reduced and used
    as the red, amber, and green values.
    If any of the colors are disabled by QFormat, then fewer than 3 
    data series are used.  I.e. if amber is disabled, the first two series
    will be treated as red and green.

    QMetric 'rag' parameter is not used, nor are 'impact', etc.
    Just raw reduced numbers and QFormat.

    QFormat support (under 'geckoboard_meter' or '_default'):
        reduce      : (optional) Function from metricdef.FUNCS to reduce
                                 series with. Default 'LAST'.
        prefix      : (optional) prefix for value, e.g. "$"
        red         : label for red value, or "OFF" (False) to skip.
        amber       : label for amber value, or "OFF" (False) to skip.
        green       : label for green value, or "OFF" (False) to skip.

    More info:
     - https://developer.geckoboard.com/#rag

    Example JSON:
        {
          "item": [
            {
              "value": 16,
              "text": "Long past due"
            },
            {
              "value": 64,
              "text": "Overdue"
            },
            {
              "value": 32,
              "text": "Due"
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
        self._qfdomain = 'geckoboard_rag'

        # Write options:
        self._write_options()

        # Write as many colors as possible given data we have:
        self._write_colors()


    #
    # Internal Methods
    #

    def _write_options(self):
        """
        Write options to jout.
        """
        if self.query:
            try:
                qformat = self.query.qformat
                self.jout['prefix'] = qformat.get(self._qfdomain, 'prefix')
            except KeyError:
                pass

    def _write_colors(self):
        """
        Write as many colors to jout as possible given data we have.
        Tries to build up the colors progressively, allowing for multiple
        metrics and/or multiple passes from multiple queries.
        """
        # Start based on how many we have so far:
        QF_RAGKEYS = ['red', 'amber', 'green']  # QFormat rag keys
        qfidx = len(self.jout['item'])

        # Keep going until we have all of the colors:
        iter_series = self.mdseries.iter_series()
        while qfidx < len(QF_RAGKEYS):

            # Identify this color:
            qfragkey = QF_RAGKEYS[qfidx]
            qfidx += 1
            label = self._qformat_get(qfragkey, "")

            # If instructed by QFormat to skip it, write an empty one:
            if label == False:
                self.jout['item'].append( {} )
                continue

            # Try to pull and write the next color from data series:
            try:
                dseries = next(iter_series)
            except StopIteration:  # No series availalable.
                # Hopefully another query will provide the rest.
                return  
            self._write_colors_series(label, dseries)

    def _write_colors_series(self, label, dseries):
        """Write the next color from given DataSeries."""

        self._dseries = dseries

        # Reduce series to single value by reduce func.
        # Usually func 'LAST' with collapsed series (Servant option),
        # but other operations can be useful too, e.g. AVG, etc.
        reduce_func = self._qformat_get('reduce', 'LAST')
        self._value = self._dseries.reduce(reduce_func)

        # Prep JSON-serializable template to fill in:
        self._jitem = {
            "text": label,
            "value": self._value,
        }
        self.jout['item'].append(self._jitem)


