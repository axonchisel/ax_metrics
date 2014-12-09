"""
Ax_Metrics - Test foundation query package (not including MQL)

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import pytest

import axonchisel.metrics.foundation.chrono.ghost as ghost
import axonchisel.metrics.foundation.chrono.framespec as framespec
import axonchisel.metrics.foundation.query.query as query
import axonchisel.metrics.foundation.query.qdata as qdata
import axonchisel.metrics.foundation.query.qtimeframe as qtimeframe
import axonchisel.metrics.foundation.query.qformat as qformat
import axonchisel.metrics.foundation.query.qghosts as qghosts
import axonchisel.metrics.foundation.query.queryset as queryset


# ----------------------------------------------------------------------------


class TestQuery(object):
    """
    Test Query object on its own.
    """

    #
    # Setup / Teardown
    #

    def setup_method(self, method):
        self.query1 = query.Query()

    #
    # Tests
    #

    def test_validate_simple(self):
        assert self.query1.is_valid() == False
        with pytest.raises(ValueError):
            self.query1.validate()
        self.query1.qdata.add_qmetric(qdata.QMetric(metric_id='ametric'))
        assert self.query1.is_valid()
        self.query1.validate()

    def test_str(self):
        str(self.query1)

    def test_qdata(self):
        qdata1 = qdata.QData()
        self.query1.qdata = qdata1
        with pytest.raises(TypeError):
            qdata1.add_qmetric('Not QMetric')
        str(qdata1)
        qm1 = qdata.QMetric()
        qdata1.add_qmetric(qm1)
        str(qdata1)
        assert qdata1.count_qmetrics() == 1
        qm1.rag = [10, 20]
        with pytest.raises(ValueError):
            qm1.rag = [10, 20, 30]
        with pytest.raises(TypeError):
            self.query1.qdata = 'Not QData'
        qm2 = qdata.QMetric()
        qdata1.add_qmetric(qm2)
        assert list(qdata1.iter_qmetrics()) == [qm1, qm2]
        assert qdata1.get_qmetric(0) == qm1
        assert qdata1.get_qmetric(1) == qm2
        with pytest.raises(IndexError):
            assert qdata1.get_qmetric(999)

    def test_qmetric(self):
        qm1 = qdata.QMetric()
        str(qm1)
        qm1.div_metric_id = 'ametric'
        qm1.goal = 123


    def test_qtimeframe(self):
        qtimeframe1 = qtimeframe.QTimeFrame()
        str(qtimeframe1)
        qtimeframe1.tmfrspec = framespec.FrameSpec()
        assert qtimeframe1.tmfrspec
        with pytest.raises(TypeError):
            qtimeframe1.tmfrspec = 'Not FrameSpec'
        self.query1.qtimeframe = qtimeframe1
        with pytest.raises(TypeError):
            self.query1.qtimeframe = 'Not QTimeFrame'

    def test_qformat(self):
        qformat1 = qformat.QFormat()
        self.query1.qformat = qformat1
        str(qformat1)
        assert qformat1.has_domain('newdomain') == False
        dom = qformat1.get_domain('newdomain')
        assert qformat1.has_domain('newdomain') == True
        dom['k1'] = 'val1'
        dom['k2'] = (1,2,3)
        str(qformat1)
        with pytest.raises(TypeError):
            self.query1.qformat = 'Not QFormat'
        assert qformat1.get('newdomain', 'k1') == 'val1'
        assert qformat1.get('newdomain', 'BOGUS', 'def') == 'def'
        with pytest.raises(KeyError):
            assert qformat1.get('newdomain', 'BOGUS') == 'def'
        qformat1.get_domain('_default')['comkey'] = 'comval1'
        assert qformat1.get('newdomain', 'comkey') == 'comval1'

    def test_qghosts(self):
        qghosts1 = qghosts.QGhosts()
        str(qghosts1)
        self.query1.qghosts = qghosts1
        with pytest.raises(TypeError):
            self.query1.qghosts = 'Not QGhosts'
        with pytest.raises(TypeError):
            self.query1.qghosts.add_ghost('Not QGhost')
        assert self.query1.qghosts.count_ghosts() == 0
        g1 = ghost.Ghost('PREV_PERIOD1')
        g2 = ghost.Ghost('PREV_YEAR1')
        assert g2.gtype == 'PREV_YEAR1'
        self.query1.qghosts.add_ghost(g1)
        self.query1.qghosts.add_ghost(g2)
        assert self.query1.qghosts.count_ghosts() == 2
        glist = self.query1.qghosts.get_ghosts()
        assert len(glist) == 2
        assert glist[1] == g2
        assert self.query1.qghosts[1] == g2
        str(g1)
        with pytest.raises(ValueError):
            g1.gtype = 'Not valid gtype'

    #
    # Internal Helpers
    #


# ----------------------------------------------------------------------------


class TestQuerySet(object):
    """
    Test QuerySet object on its own.
    """

    #
    # Setup / Teardown
    #

    def setup_method(self, method):
        self.queryset1 = queryset.QuerySet()

    #
    # Tests
    #

    def test_str(self):
        str(self.queryset1)

    def test_validate(self, queries):
        self.queryset1.validate()
        self.queryset1.add_query(queries[2])
        self.queryset1.add_query(queries[3])
        self.queryset1.validate()

    def test_count_add(self, queries):
        assert self.queryset1.count_queries() == 0
        self.queryset1.add_query(queries[2])
        self.queryset1.add_query(queries[3])
        assert self.queryset1.count_queries() == 2
        self.queryset1.add_query(queries[4]) # (same id)
        assert self.queryset1.count_queries() == 2

    def test_get_by_id(self, queries):
        self.queryset1.add_query(queries[2])
        self.queryset1.add_query(queries[3])
        qx = self.queryset1.get_query_by_id('q2')
        assert qx == queries[2]
        with pytest.raises(KeyError):
            self.queryset1.get_query_by_id('No matching key')

    def test_bad_add(self):
        with pytest.raises(TypeError):
            self.queryset1.add_query('Not Query')

    #
    # Internal Helpers
    #


