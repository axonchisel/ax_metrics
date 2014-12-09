"""
Ax_Metrics - Test io.erout package

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import pytest
from StringIO import StringIO

import axonchisel.metrics.foundation.chrono.timerange as timerange
from axonchisel.metrics.io.erout.interface import EROut
from axonchisel.metrics.io.erout.base import EROutBase
import axonchisel.metrics.io.erout.plugins.ero_strbuf as ero_strbuf
import axonchisel.metrics.io.erout.plugins.ero_csv as ero_csv


# ----------------------------------------------------------------------------


class TestEROut(object):
    """
    Test general EROut.
    """

    #
    # Setup / Teardown
    #

    def setup_method(self, method):
        self.extinfo = {'a': 65, 'b': "LilB", 'special': { 'q': 34, 'z': 35 } }


    #
    # Tests
    #

    def test_base_not_impl(self, queries, mdseries):
        with pytest.raises(NotImplementedError):
            absbase = EROut(queries[2])
        class FakeBase(EROut):
            def __init__(self, extinfo=None):
                pass
        absbase = FakeBase(queries[2])
        with pytest.raises(NotImplementedError):
            absbase.plugin_create()
        with pytest.raises(NotImplementedError):
            absbase.plugin_destroy()
        with pytest.raises(NotImplementedError):
            absbase.plugin_output(mdseries[1], query=queries[2])

    def test_plugin_extinfo(self, queries):
        ero = ero_strbuf.EROut_strbuf(extinfo=self.extinfo)
        assert ero.plugin_extinfo('a') == 65
        assert ero.plugin_extinfo('b') == "LilB"
        with pytest.raises(KeyError):
            ero.plugin_extinfo('BOGUS')
        assert ero.plugin_extinfo('BOGUS', default="D") == "D"

    def test_basic_strbuf(self, queries, mdseries):
        ero = ero_strbuf.EROut_strbuf(extinfo=self.extinfo)
        str(ero)
        str(ero.query)
        ero.plugin_create()
        for x in range(100):
            ero.output(mdseries[1], query=queries[2])
        assert len(ero.buf_get_lines()) == 100
        assert ero.buf_get().splitlines() == ero.buf_get_lines()
        ero.buf_add_line(u"New line")
        assert len(ero.buf_get_lines()) == 101
        ero.buf_add_lines([u"New line", u"New line 2", u"New line 3"])
        assert len(ero.buf_get_lines()) == 104
        ero.plugin_destroy()

    def test_format_str(self, queries, mdseries):
        ero = ero_strbuf.EROut_strbuf(extinfo=self.extinfo)
        ero.plugin_create()
        ero.output(mdseries[1], query=queries[2])  # (to set _query)
        assert ero._format_str("plain") == "plain"
        assert ero._format_str("My {extinfo.special.q} here") == "My 34 here"
        assert ero._format_str("My {query.id} here") == "My q2 here"
        ero.plugin_destroy()


# ----------------------------------------------------------------------------


class TestEROut_csv(object):
    """
    Test EROut_csv.
    """

    #
    # Setup / Teardown
    #

    def setup_method(self, method):
        self.buf = StringIO()
        self.extinfo = {
            'fout': self.buf,
        }


    #
    # Tests
    #

    def test_plugin_basic(self, queries, mdseries):
        ero = ero_csv.EROut_csv(extinfo=self.extinfo)
        ero.plugin_create()
        ero.output(mdseries[3], query=queries[4])
        lines = self.buf.getvalue().splitlines()
        assert lines[0] == 'query_id,series_id,ghost,tm_anchor,tm_begin_inc,tm_end_exc,value'
        assert lines[1] == 'q3,s\xc3\xa9r\xc3\xaees4,,2014-02-01 00:00:00,2014-02-01 00:00:00,2014-03-01 00:00:00,42'
        assert lines[6] == 'q3,s3,PREV_PERIOD1,2014-02-14 16:30:45,2014-02-14 16:30:45,2014-04-14 16:42:45,2'
        ero.plugin_destroy()

    def test_plugin_date_format1(self, queries, mdseries):
        ero = ero_csv.EROut_csv(extinfo=self.extinfo)
        ero._format_datetime('%Y-%m-%d', None)
        ero.configure(options={'date_format': '%Y-%m-%d'})
        ero.plugin_create()
        ero.output(mdseries[3], query=queries[4])
        lines = self.buf.getvalue().splitlines()
        assert lines[6] == 'q3,s3,PREV_PERIOD1,2014-02-14,2014-02-14,2014-04-14,2'
        ero.plugin_destroy()

    def test_plugin_date_format2(self, queries, mdseries):
        ero = ero_csv.EROut_csv(extinfo=self.extinfo)
        ero.configure(options={'date_format': '%s'})
        ero.plugin_create()
        ero.output(mdseries[3], query=queries[4])
        lines = self.buf.getvalue().splitlines()
        assert lines[6] == 'q3,s3,PREV_PERIOD1,1392424245,1392424245,1397518965,2'
        ero.plugin_destroy()




