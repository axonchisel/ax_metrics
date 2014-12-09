"""
Ax_Metrics - EROut plugin 'geckoboard_bullet'

Writes Geckoboard JSON output for various charts for use with
http://www.geckoboard.com.

Contents:
 - EROut_geckoboard_bullet       - bullet chart

See:
 - https://developer.geckoboard.com/#bullet-graph

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import time

from axonchisel.metrics.foundation.ax.dictutil import OrderedDict
from axonchisel.metrics.foundation.chrono.stepper import Stepper

from .base import EROut_geckoboard

import logging
log =  logging.getLogger(__name__)


# ----------------------------------------------------------------------------


class EROut_geckoboard_bullet(EROut_geckoboard):
    """
    EROut (Extensible Report Outputter) Plugin for Geckoboard bullet charts.
    Adds JSON-serializable output to extinfo['jout'] dict.

    Supports multiple invocations to include multiple bullets in one output,
    for use with 2x2 Geckoboard tile that can handle up to 4 bullets.

    Typical usage is with collapsed query, default 'LAST' reduce function,
    and ghosts disabled.  This prevent needless queries from running.
    Non-collapsed queries with other reduce functions may be used too.

    Compatibility note:
    Targets Geckoboard bullet chart v1 ~2014-11 including workarounds for
    some of their bugs. GB intends to release a new bullet chart version soon
    for which a new EROut should be written.

    QFormat support (under 'geckoboard_bullet' or '_default'):
        reduce      : Function from metricdef.FUNCS to reduce series with
        title       : (optional) Title for bullet
        subtitle    : (optional) Subtitle for bullet
        orientation : (Optional) 'horizontal' or 'vertical'

    More info:
     - https://developer.geckoboard.com/#bullet-graph
     - http://www.perceptualedge.com/articles/misc/Bullet_Graph_Design_Spec.pdf
     - http://en.wikipedia.org/wiki/Bullet_graph

    Example JSON:
        {
          "orientation": "horizontal",
          "item": {
            "label": "Revenue 2014 YTD",
            "sublabel": "(U.S. $ in thousands)",
            "axis": {
              "point": ["0", "200", "400", "600", "800", "1000"]
            },
            "range": {
              "red": {
                "start": 0,
                "end": 400
              },
              "amber": {
                "start": 401,
                "end": 700
              },
              "green": {
                "start": 701,
                "end": 1000
              }
            },
            "measure": {
              "current": {
                "start": "0",
                "end": "500"
              },
              "projected": {
                "start": "100",
                "end": "900"
              }
            },
            "comparative": {
              "point": "600"
            }
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
        self._qfdomain = 'geckoboard_bullet'

        # Set orientation (may override previous query's):
        if self.query:
            try:
                orientation = self.query.qformat.get(
                    'geckoboard_bullet', 'orientation')
                self.jout['orientation'] = orientation
            except KeyError:
                pass

        # Iterate MDS, writing each series:
        for dseries in mdseries.iter_series():
            self._write_series(dseries)


    #
    # Internal Methods
    #

    def _write_series(self, dseries):
        """
        Write the current DataSeries to output as a bullet chart.
        (Geckoboard supports up to 4 bullet charts in the JSON,
        so up to 4 DataSeries can be used)
        """

        # Prep:
        self._dseries = dseries
        self._write_series_prep()

        # Calculate details:
        self._write_series_query_adjust()
        self._write_series_calc_axis()
        self._write_series_calc_rag()

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
            "label": "",
            "sublabel": "",
            "axis": {
                "point": []
            },
            # Note: Due to Geckoboard bullet specification design flaw,
            # we must use OrderedDict to ensure the ranges are in order.
            "range": OrderedDict([
                ("red",   { "start":  0,  "end":  0  }),
                ("amber", { "start":  0,  "end":  0  }),
                ("green", { "start":  0,  "end":  0  })
            ]),
            "measure": {
                "current":   { "start":  0,  "end":  0 },
                # "projected": { "start":  0,  "end":  0 }
            },
            # "comparative": { "point":  0 }
        }

        # Prep initial data:
        self._minval = 0
        self._maxval = self._value
        self._is_int = self._is_round(self._maxval)
        self._qmetric = None

        # Set known jitem data:
        self._jitem['measure']['current']['begin'] = self._minval
        self._jitem['measure']['current']['end']   = self._value

    def _write_series_query_adjust(self):
        """Adjust settings based on Query (if provided)."""

        if not self.query:
            return
        
        # Check format labels:
        qformat = self.query.qformat
        domain = 'geckoboard_bullet'
        self._jitem['label'] = qformat.get(domain, 'title', "")
        self._jitem['sublabel'] = qformat.get(domain, 'subtitle', "")

        # Check qmetric:
        self._qmetric = self.query.qdata.get_qmetric(0)

        # If goal specified, handle it:
        if self._qmetric.goal is not None:
            self._jitem['comparative'] = {'point': self._qmetric.goal}
            self._maxval = max(self._maxval, self._qmetric.goal)
            if self._is_int:
                self._is_int = self._is_round(self._maxval)

        # Projected value based on current relative to query time frame:
        if self.query.qtimeframe.tmfrspec.mode == 'CURRENT':
            dseries = self._dseries
            stepper = Stepper(dseries.tmfrspec, ghost=dseries.ghost)
            tmrange = stepper.analyze()['tmrange']

            # Calc tfrac as how far into time period we are, [0..1]
            t0 = time.mktime(tmrange.inc_begin.timetuple())
            t1 = time.mktime(tmrange.exc_end.timetuple())
            tnow = time.time()
            tfrac = 1.0 * (tnow - t0) / (t1 - t0)

            if 0.0 <= tfrac <= 1.0:
                # Calculate projected value based on current value and tfrac:
                proj = self._minval + ((self._value - self._minval) / tfrac)
                self._maxval = max(self._maxval, proj)
                self._jitem['measure']['projected'] = {}
                self._jitem['measure']['projected']['start'] = self._minval
                self._jitem['measure']['projected']['end']   = proj
            else:
                # May have been reframed, etc., so just skip projection
                pass

    def _write_series_calc_axis(self):
        """Calculate user-friendly axis values based on data."""

        AXIS_MAX_MULTIPLIER = 1.25  # some breathing room above max value
        AXIS_SIG_DIGS       = 3     # how many significant digits to round to
        AXIS_POINTS         = 5     # how many axis points to label

        # Calc initial axis min/max values and step size:
        aminval = self._minval
        amaxval = self._round_sigdigs((self._maxval * AXIS_MAX_MULTIPLIER),
            AXIS_SIG_DIGS)
        axis_step = (amaxval - aminval) / (AXIS_POINTS - 1)

        # Some rounding if we're operating on ints:
        if self._is_int:
            if not (self._is_round(axis_step) and self._is_round(amaxval)):
                axis_step = round(axis_step)
                amaxval = aminval + (axis_step * (AXIS_POINTS - 1))

        # Calc axis points:
        for n in range(AXIS_POINTS):
            aval = aminval + (n * axis_step)
            aval = self._round_sigdigs(aval, AXIS_SIG_DIGS)
            if self._is_int:
                aval = "%d" % (aval)
            else:
                aval = "%.*f" % (AXIS_SIG_DIGS-1, aval)
            self._jitem['axis']['point'].append(aval)


    def _write_series_calc_rag(self):
        """Calculate red/amber/green cutoffs."""

        # Prep with default cutoff points based on data range:
        od_range = self._jitem['range']
        rag_c1 = self._minval + ((self._maxval - self._minval) / 3.0 * 1)
        rag_c2 = self._minval + ((self._maxval - self._minval) / 3.0 * 2)

        # If negative impact (e.g. expenses, bugs, ...), invert RAG:
        if self.query and (self._qmetric.impact == 'NEGATIVE'):

            # Reverse RAG order in dict (GB bug workaround):
            od_range = OrderedDict(reversed(list(od_range.iteritems())))
            self._jitem['range'] = od_range

            # Apply cutoff points:
            if self._qmetric.rag:
                (rag_c2, rag_c1) = self._qmetric.rag
            od_range['green'] = { "start": self._minval, "end": rag_c1 }
            od_range['amber'] = { "start": rag_c1,       "end": rag_c2 }
            od_range['red']   = { "start": rag_c2,       "end": self._maxval }

        # Else normal positive impact (e.g. revenue, sales, ...):
        else:
            assert self._qmetric.impact == 'POSITIVE'

            # Apply cutoff points:
            if self.query and (self._qmetric.rag):
                (rag_c1, rag_c2) = self._qmetric.rag
            od_range['red']   = { "start": self._minval, "end": rag_c1 }
            od_range['amber'] = { "start": rag_c1,       "end": rag_c2 }
            od_range['green'] = { "start": rag_c2,       "end": self._maxval }



