"""
Ax_Metrics - Test MQEngine

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import pytest

import axonchisel.metrics.foundation.chrono.framespec as framespec
import axonchisel.metrics.foundation.metricdef.mdefl as mdefl
import axonchisel.metrics.foundation.query.query as query
import axonchisel.metrics.foundation.query.qdata as qdata
import axonchisel.metrics.foundation.query.qtimeframe as qtimeframe
import axonchisel.metrics.foundation.query.qformat as qformat
import axonchisel.metrics.foundation.query.qghosts as qghosts
import axonchisel.metrics.foundation.query.queryset as queryset
import axonchisel.metrics.foundation.query.mql as mql
import axonchisel.metrics.run.mqengine.mqengine as mqengine

from .util import dt, log_config, load_metset, load_query

import logging


# ----------------------------------------------------------------------------


# Enable TEST_EXTRA_HTTP to run a more complex HTTP stat through MQEngine.
# This can add significant time to the test run!
# The HTTP components are already tested separately, so this test is more
# for testing HTTP receivers and whole system throughput.
TEST_EXTRA_HTTP = False


# ----------------------------------------------------------------------------


def setup_module(module):
    log_config(level=logging.INFO)
    # log_config(level=logging.DEBUG)


# ----------------------------------------------------------------------------


class TestMQEngine(object):
    """
    Test MQEngine running Querys.
    """

    #
    # Setup / Teardown
    #

    def setup_method(self, method):
        self.metset1 = load_metset( 'mqe-metset1.yml' )
        self.query1 = load_query( 'mqe-query1.yml' )
        self.mqe1 = mqengine.MQEngine( self.metset1 )

    #
    # Tests
    #

    def test_query_1(self):
        mds = self.mqe1.query( self.query1 )

    def test_extinfo(self):
        emfetch_extinfo = { 'foo': 'bar' }
        mqe2 = mqengine.MQEngine( self.metset1, emfetch_extinfo )
        mds = mqe2.query( self.query1 )

    def test_nodiv(self):
        assert self.query1.qdata.get_qmetric(0).div_metric_id is not None
        self.query1.qdata.get_qmetric(0).div_metric_id = None
        mds = self.mqe1.query( self.query1 )

    def test_reframe_dt(self):
        self.query1.qtimeframe.tmfrspec.reframe_dt = dt('2013-08-15')
        mds = self.mqe1.query( self.query1 )

    def test_str(self):
        mds = self.mqe1.query( self.query1 )
        str(self.mqe1)
        str(self.mqe1._state)

    @pytest.mark.skipif("not TEST_EXTRA_HTTP")
    def test_real_http_backend(self):
        metset1 = load_metset('mqe-metset2.yml')
        query1  = load_query('mqe-query2.yml')
        query1.qtimeframe.tmfrspec.reframe_dt = dt('2013-08-15')
        emfetch_extinfo = {
            'http': {
                'api_url': 'http://localhost/stats/KPI/reduce/',
                'api_key': 'TestKey',
                'table_prefix': 'tm_',
            }
        }
        mqe = mqengine.MQEngine(metset1, emfetch_extinfo)
        mds = mqe.query(query1)


