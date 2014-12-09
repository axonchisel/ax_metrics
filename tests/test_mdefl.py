"""
Ax_Metrics - Test foundation MDefL parsing

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import pytest
import re
import yaml

import axonchisel.metrics.foundation.metricdef.metricdef as metricdef
import axonchisel.metrics.foundation.metricdef.mdefl as mdefl

from .util import load_test_asset


# ----------------------------------------------------------------------------


class TestMetricDefParse(object):
    """
    Test MetricDef parsing.
    """

    #
    # Setup / Teardown
    #

    def setup_method(self, method):
        self.yaml_metric1 = load_test_asset('metricdef1.yml')
        self.parser1 = mdefl.MetricDefParser()
        
    #
    # Tests
    #

    def test_parse_simple(self):
        mdef2 = self.parser1.parse_ystr_metric(self.yaml_metric1)
        mdef2.validate()
        mdef3 = self.parser1.get_metricdef()
        assert mdef2 == mdef3
        mdef3.validate()

    def test_str(self):
        str(self.parser1)

    def test_parse_missing_ok(self):
        missing_ok = [
            'data_field', 'data_type', 'emfetch_opts',
        ]
        for m in missing_ok:
            qobj = yaml.load(self.yaml_metric1)
            del(qobj[m])
            mdef2 = self.parser1.parse_ystr_metric(yaml.dump(qobj))
            mdef2.validate()

    def test_parse_missing_filters(self):
        qobj = yaml.load(self.yaml_metric1)
        qobj['filters'] = 12345 # not list
        with pytest.raises(mdefl.MDefLParseError):
            self.parser1.parse_ystr_metric(yaml.dump(qobj))
        del(qobj['filters'])
        mdef2 = self.parser1.parse_ystr_metric(yaml.dump(qobj))
        mdef2.validate()

    def test_parse_verify(self):
        mdef2 = self.parser1.parse_ystr_metric(self.yaml_metric1)
        mdef2.validate()
        assert mdef2.emfetch_id == 'mysql'
        assert mdef2.emfetch_opts.get('db') == 'mydb1'
        assert mdef2.table == 'first_sales'
        assert mdef2.func == 'COUNT'
        assert mdef2.time_field == 'timeCreated'
        assert mdef2.time_type == 'TIME_EPOCH_SECS'
        assert mdef2.data_field == 'myfield'
        assert mdef2.data_type == 'NUM_INT'
        assert mdef2.filters.count_filters() == 2
        filter2 = metricdef.Filter(field='foo', op='EQ', value=123)
        assert mdef2.filters.get_filters()[0] == filter2

    def test_reset(self):
        mdef2 = self.parser1.parse_ystr_metric(self.yaml_metric1)
        self.parser1.reset()
        self.parser1.reset(base=mdef2)
        with pytest.raises(TypeError):
            self.parser1.reset(base='Not MetricDef')

    #
    # Internal Helpers
    #


# ----------------------------------------------------------------------------


class TestMetSetParse(object):
    """
    Test MetSet parsing.
    """

    #
    # Setup / Teardown
    #

    def setup_method(self, method):
        self.yaml_metset1 = load_test_asset('metset1.yml')
        self.parser1 = mdefl.MetSetParser()
        
    #
    # Tests
    #

    def test_parse_simple(self):
        metset2 = self.parser1.parse_ystr_metset(self.yaml_metset1)
        metset2.validate()
        metset3 = self.parser1.get_metset()
        assert metset2 == metset3
        metset3.validate()

    def test_str(self):
        str(self.parser1)

    def test_parse_table_defaults(self):
        qobj = yaml.load(self.yaml_metset1)
        del(qobj['table_defaults'][1]['table'])
        with pytest.raises(mdefl.MDefLParseError):
            self.parser1.parse_ystr_metset(yaml.dump(qobj))
        qobj['table_defaults'] = 12345 # not list
        with pytest.raises(mdefl.MDefLParseError):
            self.parser1.parse_ystr_metset(yaml.dump(qobj))
        del(qobj['table_defaults'])
        self.parser1.parse_ystr_metset(yaml.dump(qobj))

    def test_parse_metrics(self):
        qobj = yaml.load(self.yaml_metset1)
        del(qobj['metrics'][1]['id'])
        with pytest.raises(mdefl.MDefLParseError):
            self.parser1.parse_ystr_metset(yaml.dump(qobj))
        qobj['metrics'] = 12345 # not list
        with pytest.raises(mdefl.MDefLParseError):
            self.parser1.parse_ystr_metset(yaml.dump(qobj))
        del(qobj['metrics'])
        with pytest.raises(mdefl.MDefLParseError):
            self.parser1.parse_ystr_metset(yaml.dump(qobj))

    def test_parse_verify(self):
        metset2 = self.parser1.parse_ystr_metset(self.yaml_metset1)
        metset2.validate()
        assert metset2.count_metrics() == 4
        mdef2 = metset2.get_metric_by_id('rev_new_sales')
        assert mdef2.table == 'first_sales'          # (explicit)
        assert mdef2.time_type == 'TIME_EPOCH_SECS'  # (from tbldef)
        assert mdef2.filters.count_filters() == 2    # (from tbldef)

    #
    # Internal Helpers
    #



