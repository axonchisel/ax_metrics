"""
Ax_Metrics - Test foundation MQL parsing

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import pytest
import yaml

import axonchisel.metrics.foundation.query.mql as mql

from .util import dt, load_test_asset


# ----------------------------------------------------------------------------


class TestQueryParse(object):
    """
    Test Query parsing.
    """

    #
    # Setup / Teardown
    #

    def setup_method(self, method):
        self.yaml_query1 = load_test_asset('query1.yml')
        self.parser1 = mql.QueryParser()

    #
    # Tests
    #

    def test_parse_simple(self):
        query2 = self.parser1.parse_ystr_query(self.yaml_query1)
        query2.validate()
        query3 = self.parser1.get_query()
        assert query2 == query3
        query3.validate()

    def test_str(self):
        str(self.parser1)

    def test_parse_qdata(self):
        q = self.parser1.parse_ystr_query(self.yaml_query1)
        assert q.qdata.count_qmetrics() == 1
        qmetric1 = q.qdata.get_qmetric(0)
        assert qmetric1.metric_id == 'num_new_paid_accounts'
        assert qmetric1.div_metric_id == 'num_total_paid_accounts'
        assert qmetric1.goal == 0.2
        assert qmetric1.goal_mode == 'CONSTANT'

    def test_parse_qtimeframe(self):
        q = self.parser1.parse_ystr_query(self.yaml_query1)
        tmfrspec1 = q.qtimeframe.tmfrspec
        assert tmfrspec1.range_unit == 'MONTH'
        assert tmfrspec1.range_val == 3
        assert tmfrspec1.gran_unit == 'DAY'
        assert tmfrspec1.smooth_unit == 'DAY'
        assert tmfrspec1.smooth_val == 30
        assert tmfrspec1.mode == 'CURRENT'
        assert tmfrspec1.reframe_dt == dt('2014-11-01')
        assert tmfrspec1.accumulate == True
        assert tmfrspec1.allow_overflow_begin == False
        assert tmfrspec1.allow_overflow_end == True

    def test_parse_missing_ok(self):
        missing_ok = [
            'id', 'format', 'ghosts',
        ]
        for m in missing_ok:
            yaml = self._yaml1_minus_section(m)
            query2 = self.parser1.parse_ystr_query(yaml)
            query2.validate()

    def test_parse_missing_not_ok(self):
        missing_bad = [
            'data', 'timeframe'
        ]
        for m in missing_bad:
            yaml = self._yaml1_minus_section(m)
            with pytest.raises(mql.MQLParseError):
                self.parser1.parse_ystr_query(yaml)

    def test_parse_bad_qmetrics(self):
        qobj = yaml.load(self.yaml_query1)
        qobj['data']['metrics'] = [12345] # list of non-dicts
        with pytest.raises(mql.MQLParseError):
            self.parser1.parse_ystr_query(yaml.dump(qobj))
        qobj['data']['metrics'] = 12345 # not list
        with pytest.raises(mql.MQLParseError):
            self.parser1.parse_ystr_query(yaml.dump(qobj))
        del(qobj['data']['metrics'])
        with pytest.raises(mql.MQLParseError):
            self.parser1.parse_ystr_query(yaml.dump(qobj))

    def test_parse_bad_qtimeframe(self):
        qobj = yaml.load(self.yaml_query1)
        qobj['timeframe']['reframe_dt'] = 12345 # not datetime
        with pytest.raises(mql.MQLParseError):
            self.parser1.parse_ystr_query(yaml.dump(qobj))
        qobj['timeframe'] = 12345 # not dict
        with pytest.raises(mql.MQLParseError):
            self.parser1.parse_ystr_query(yaml.dump(qobj))

    def test_parse_bad_qformat(self):
        qobj = yaml.load(self.yaml_query1)
        qobj['format']['domain'] = 12345 # not dict
        with pytest.raises(mql.MQLParseError):
            self.parser1.parse_ystr_query(yaml.dump(qobj))
        qobj['format'] = 12345 # not dict
        with pytest.raises(mql.MQLParseError):
            self.parser1.parse_ystr_query(yaml.dump(qobj))

    def test_parse_bad_qghosts(self):
        qobj = yaml.load(self.yaml_query1)
        qobj['ghosts'] = 12345 # not list
        with pytest.raises(mql.MQLParseError):
            self.parser1.parse_ystr_query(yaml.dump(qobj))

    def test_reset(self):
        query2 = self.parser1.parse_ystr_query(self.yaml_query1)
        self.parser1.reset()
        self.parser1.reset(base=query2)
        with pytest.raises(TypeError):
            self.parser1.reset(base='Not Query')

    #
    # Internal Helpers
    #

    def _yaml1_minus_section(self, section, srcstr=None):
        """
        Return yaml but without the top level section named as indicated.
        If srcstr not specified, uses self.yaml_query1.
        """
        if srcstr is None:
            srcstr = self.yaml_query1
        obj = yaml.load(srcstr)
        del(obj[section])
        outstr = yaml.dump(obj)
        return outstr


# ----------------------------------------------------------------------------


class TestQuerySetParse(object):
    """
    Test QuerySet parsing.
    """

    #
    # Setup / Teardown
    #

    def setup_method(self, method):
        self.yaml_queryset1 = load_test_asset('queryset1.yml')
        self.parser1 = mql.QuerySetParser()

    #
    # Tests
    #

    def test_parse_simple(self):
        queryset2 = self.parser1.parse_ystr_queryset(self.yaml_queryset1)
        queryset2.validate()
        queryset3 = self.parser1.get_queryset()
        assert queryset2 == queryset3
        queryset3.validate()

    def test_str(self):
        str(self.parser1)

    def test_parse_verify(self):
        queryset2 = self.parser1.parse_ystr_queryset(self.yaml_queryset1)
        queryset2.validate()
        assert queryset2.count_queries() == 2
        q1 = queryset2.get_query_by_id('pct_new_paid_accounts_rolling_30d')
        assert q1.qdata.get_qmetric(0).metric_id == 'num_new_paid_accounts'
        assert q1.qdata.get_qmetric(0).div_metric_id == 'num_total_paid_accounts'
        assert q1.qtimeframe.tmfrspec.accumulate == False
        q2 = queryset2.get_query_by_id('num_new_paid_accounts_month_to_date')
        assert q2.qdata.get_qmetric(0).metric_id == 'num_new_paid_accounts'
        assert q2.qtimeframe.tmfrspec.accumulate == True

    def test_parse_bad_queries(self):
        qobj = yaml.load(self.yaml_queryset1)
        qobj['queries'] = list()
        self.parser1.parse_ystr_queryset(yaml.dump(qobj))
        qobj['queries'] = 12345 # not list
        with pytest.raises(mql.MQLParseError):
            self.parser1.parse_ystr_queryset(yaml.dump(qobj))
        del qobj['queries']
        with pytest.raises(mql.MQLParseError):
            self.parser1.parse_ystr_queryset(yaml.dump(qobj))

    #
    # Internal Helpers
    #


