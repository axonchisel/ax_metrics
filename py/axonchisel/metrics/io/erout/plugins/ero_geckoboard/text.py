"""
Ax_Metrics - EROut plugin 'geckoboard_text'

Writes Geckoboard JSON output for various charts for use with
http://www.geckoboard.com.

Contents:
 - EROut_geckoboard_text        - pages of text, optionally flagged

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


# Type numbers used by Geckoboard Text widget:
_GB_TEXT_TYPE_NORMAL  = 0   # no flag
_GB_TEXT_TYPE_INFO    = 2   # small gray "i" flag
_GB_TEXT_TYPE_ALERT   = 1   # serious orange "!" flag
_GB_TEXT_TYPE_BY_COLOR = {    # map color to GB text type
    'GREEN': _GB_TEXT_TYPE_NORMAL,
    'AMBER': _GB_TEXT_TYPE_INFO,
    'RED'  : _GB_TEXT_TYPE_ALERT,
}

_QFORMAT_RAG_KEY_BY_COLOR = {  # map color to QFormat format key name
    'GREEN': 'green',
    'AMBER': 'amber',
    'RED':   'red',
}


# ----------------------------------------------------------------------------


class EROut_geckoboard_text(EROut_geckoboard):
    """
    EROut (Extensible Report Outputter) Plugin for Geckoboard Text.
    Adds JSON-serializable output to extinfo['jout'] dict.

    Typical usage is with collapsed query, default 'LAST' reduce function,
    and ghosts disabled.  This prevent needless queries from running.
    Non-collapsed queries with other reduce functions may be used too.

    Each data series of each query processed by this EROut will result in
    an additional text page which Geckoboard cycles through automatically.

    If the QMetric 'rag' parameter is specified, the text may be flagged
    as either important (amber) or very important (red).  Otherwise text
    is displayed without any flag.

    QMetric NEGATIVE 'impact' is addressed properly to support negative
    data (e.g. bugs, expenses, etc.).

    The QFormat format strings (red, amber, green) support these params:
        - qmlabel - label from QMetric
        - value   - actual value
        - amber   - amber value cutoff
        - red     - red value cutoff
    Example formats:
        red:   "DANGER: SENSOR {qmlabel} - {value} OVER LIMIT!"
        amber: "Notice: Sensor {qmlabel} - {value} near limit ({red})"
        green: "Sensor {qmlabel} OK"

    QFormat support (under 'geckoboard_meter' or '_default'):
        reduce      : (optional) Function from metricdef.FUNCS to reduce
                                 series with. Default 'LAST'.
        red         : (optional) Format str for red mode.
                        Only required if 'rag' specified in QMetric.
        amber       : (optional) Format str for amber mode.
                        Only required if 'rag' specified in QMetric.
        green       : Format str for green mode.

    More info:
     - https://developer.geckoboard.com/#text

    Example JSON:
        {
          "item": [
            {
              "text": "Unfortunately, as you probably already know, people",
              "type": 0
            },
            {
              "text": "As you might know, I am a full time Internet",
              "type": 1
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
        self._qfdomain = 'geckoboard_text'

        # Iterate MDS, writing each series:
        for dseries in mdseries.iter_series():
            self._write_series(dseries)


    #
    # Internal Methods
    #

    def _write_series(self, dseries):
        """
        Write the current DataSeries to output as an item.
        (Geckoboard supports up to 10 items (pages of text) in the JSON,
        so up to 10 DataSeries can be used, including spread among multiple
        queries)
        """

        # Prep:
        self._dseries = dseries
        self._write_series_prep()

        # Calculate details:
        self._write_series_identify_color()
        self._write_series_set_type()
        self._write_series_format_text()

        # Add overall item to jout:
        self.jout['item'].append(self._jitem)

    def _write_series_prep(self):
        """Prepare internal data for new DataSeries."""

        # Reduce series to single value by reduce func.
        # Usually func 'LAST' with collapsed series (Servant option),
        # but other operations can be useful too, e.g. AVG, etc.
        reduce_func = self._qformat_get('reduce', 'LAST')
        self._value = self._dseries.reduce(reduce_func)

        # Prep JSON-serializable template to fill in:
        self._jitem = {
            "text": "",
            "type": _GB_TEXT_TYPE_NORMAL,
        }

    def _write_series_identify_color(self):
        """Set self._color to GREEN,AMBER,RED based on value."""
        
        # Default to GREEN:
        self._color = 'GREEN'
        if not self.query:
            return  # no Query, so stay GREEN

        # Find first QMetric in QData with metric_id matching series metric:
        # (reverse engineering since QData is not passed through MQEngine)
        try:
            self._qmetric = next(qm for qm in
                self.query.qdata.iter_qmetrics() 
                if qm.metric_id == self._dseries.mdef.id
            )
        except StopIteration:
            return  # no QMetric, so stay GREEN (this is not likely)
        if not self._qmetric.rag:
            return  # no 'rag' set on QMetric, so stay GREEN
        (rag_c1, rag_c2) = self._qmetric.rag

        # If negative impact (e.g. expenses, bugs, ...):
        if self._qmetric.impact == 'NEGATIVE':
            if self._value >= rag_c1:
                self._color = 'RED'
            elif self._value >= rag_c2:
                self._color = 'AMBER'
        # Else normal positive impact (e.g. revenue, sales, ...):
        else:
            assert self._qmetric.impact == 'POSITIVE'
            if self._value <= rag_c1:
                self._color = 'RED'
            elif self._value <= rag_c2:
                self._color = 'AMBER'

    def _write_series_set_type(self):
        """Set jitem type based on color."""
        self._jitem['type'] = _GB_TEXT_TYPE_BY_COLOR[self._color]

    def _write_series_format_text(self):
        """Format jitem text based on color, value, etc.."""
        # Default:
        self._jitem['text'] = "{0}".format(self._value)
        if not self.query or not self._qmetric:
            return  # no query or QMetric

        # Get color format str:
        fmtkey = _QFORMAT_RAG_KEY_BY_COLOR[self._color]
        fmt = self._qformat_get(fmtkey, None)
        if not fmt:
            return  # no matching color key in QFormat

        # Build format params:
        params = {
            'qmlabel' : self._qmetric.label,
            'value'   : self._value,
            'amber'   : "?",
            'red'     : "?",
        }
        if self._qmetric.rag:
            params['red']   = self._qmetric.rag[0]
            params['amber'] = self._qmetric.rag[1]

        # Format string:
        text = fmt.format(**params)
        self._jitem['text'] = text
