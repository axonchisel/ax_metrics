"""
Ax_Metrics - EROut plugin 'csv'

Writes CSV output.

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import csv

from ..base import EROutBase


# ----------------------------------------------------------------------------


# Ordered list of CSV field names to write:
FIELDNAMES = [
    'query_id',
    'series_id',
    'ghost',
    'tm_anchor',
    'tm_begin_inc',
    'tm_end_exc', 
    'value',
]


# ----------------------------------------------------------------------------


class EROut_csv(EROutBase):
    """
    EROut (Extensible Report Outputter) Plugin 'csv'.
    Writes CSV output to extinfo['fout'] file-like object.
    """

    #
    # Abstract Method Implementations
    #

    # abstract
    def plugin_create(self):
        """
        Invoked once to allow plugin to setup what it needs.
        """
        self._wrote_header = False

    # abstract
    def plugin_destroy(self):
        """
        Invoked once to allow plugin to clean up after itself.
        """
        pass

    # abstract
    def plugin_output(self, mdseries, query=None):
        """
        EROut plugins must implement this abstract method.
        Invoked to output MultiDataSeries as specified.
        
        Returns nothing. Output target should be configured separately.

        Parameters:

          - mdseries : MultiDataSeries query result with data to output.
                    (axonchisel.metrics.foundation.data.multi.MultiDataSeries)

          - query : optional Query source with more formatting details, etc.
                    Optional. Plugins should work without access to Query.
                    (axonchisel.metrics.foundation.query.query.Query)
        """
        # Prep CSV:
        fout = self.plugin_extinfo('fout')
        self._csvw = csv.DictWriter(fout, FIELDNAMES, dialect='excel')

        # Write header (but only once):
        self._write_header_row()

        # Iterate MDS, writing each series:
        for dseries in mdseries.iter_series():
            self._write_series(dseries)

    #
    # Internal Methods
    #

    def _write_header_row(self):
        """Write CSV header row, but only once."""
        if self._wrote_header:
            return
        row = dict(zip(FIELDNAMES, FIELDNAMES))
        self._write_row(row)
        self._wrote_header = True

    def _write_series(self, dseries):
        """Write the current DataSeries to CSV writer."""
        for dpoint in dseries.iter_points():
            row = self._make_row(dseries, dpoint)
            self._write_row(row)

    def _make_row(self, dseries, dpoint):
        """Given current DataSeries and DataPoint, return row dict for CSV."""
        datefmt = self.plugin_option('date_format', '%Y-%m-%d %H:%M:%S')
        row = {
            'query_id'    : self._query.id if self._query else None,
            'series_id'   : dseries.id,
            'ghost'       : dseries.ghost.gtype if dseries.ghost else None,
            'tm_anchor'   : self._format_datetime(datefmt, dpoint.tmrange.anchor),
            'tm_begin_inc': self._format_datetime(datefmt, dpoint.tmrange.inc_begin),
            'tm_end_exc'  : self._format_datetime(datefmt, dpoint.tmrange.exc_end),
            'value'       : dpoint.value,
        }
        return row

    def _write_row(self, row):
        """Encode and write CSV dict row to open writer."""
        row = self._encode_row(row)
        self._csvw.writerow(row)

    def _encode_row(self, row):
        """Given row dict, return version with all strings utf8 encoded."""
        row2 = dict()
        for k, v in row.iteritems():
            if isinstance(v, unicode):
                v = v.encode('utf-8')
            row2[k] = v
        return row2




# ----------------------------------------------------------------------------


