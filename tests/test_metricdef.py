"""
Ax_Metrics - Test foundation metricdef package (not including MDefL parsing)

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import pytest
import copy

from axonchisel.metrics.foundation.metricdef.filters import Filter
from axonchisel.metrics.foundation.metricdef.metset import MetSet
from axonchisel.metrics.foundation.metricdef.reduce import _ReduceFuncs


# ----------------------------------------------------------------------------


class TestMetricDef(object):
    """
    Test MetricDef object on its own.
    """

    #
    # Setup / Teardown
    #

    #
    # Tests
    #

    def test_validate_simple(self, mdefs):
        mdefs[1].validate()
        assert mdefs[1].is_valid() == True

    def test_str(self, mdefs):
        str(mdefs[1])

    def test_validate_missing_attrs(self, mdefs):
        required_attrs = [
            'id', 'emfetch_id', 'table', 'time_field',
        ]
        for a in required_attrs:
            mdef2 = copy.deepcopy(mdefs[1])
            setattr(mdef2, a, '')
            assert mdef2.is_valid() == False
            with pytest.raises(ValueError):
                mdef2.validate()

    def test_validate_field_types(self, mdefs):
        ftype_attrs = [
            'data_type', 'time_type',
        ]
        for a in ftype_attrs:
            mdef2 = copy.deepcopy(mdefs[1])
            with pytest.raises(ValueError):
                setattr(mdef2, a, "BOGUSVAL")

    def test_misc(self, mdefs):
        assert mdefs[1].emfetch_opts['foo'] == 123
        assert mdefs[1].data_field == 'myval'
        assert mdefs[1].data_type == 'NUM_INT'

    def test_filters_misc(self, mdefs, filters):
        str(mdefs[1].filters)
        filter1 = filters[3]
        str(filter1)
        sorted(filters)

    def test_filters_list(self, mdefs, filters):
        mdefs[1].filters.add_filter(filters[3])
        mdefs[1].filters.add_filter(filters[4])
        assert mdefs[1].filters.count_filters() == 2
        assert mdefs[1].filters.get_filters()[1] == filters[4]
        assert mdefs[1].filters[1] == filters[4]
        d = mdefs[1].filters.safe_indexable
        assert d[1] == filters[4]
        assert d[999] == Filter()

    def test_filters_cmp(self, filters):
        assert filters[0] != filters[1]
        assert filters[1] != filters[2]
        assert filters[2] != filters[3]
        assert filters[3] != filters[4]
        assert filters[4] != filters[0]
        filters[1]._op = 'BOGUS'
        assert filters[1] != filters[3]

    def test_validate_filter_types(self, mdefs, filters):
        filter1 = filters[3]
        filter1.validate()
        mdefs[1].filters.add_filter(filter1)
        mdefs[1].validate()
        with pytest.raises(TypeError):
            mdefs[1].filters.add_filter("not a filter object")
    
    def test_validate_filters_bad1(self, mdefs, filters):
        with pytest.raises(ValueError):
            filters[0].validate()
        with pytest.raises(ValueError):
            filters[2].validate()

    def test_validate_filters_bad2(self, mdefs, filters):
        mdefs[1].filters.add_filter(filters[3])
        mdefs[1].filters.add_filter(filters[0])
        with pytest.raises(ValueError):
            mdefs[1].validate()
        filters[0].field = 'realfield'
        mdefs[1].validate()
        with pytest.raises(ValueError):
            filters[0].op = 'BOGUSOP'

    def test_validate_filters_remove(self, mdefs, filters):
        mdefs[1].filters.add_filter(filters[3])
        mdefs[1].filters.add_filter(filters[0])
        mdefs[1].filters.remove_filter(filters[3])

    def test_validate_emfetch(self, mdefs):
        mdefs[1] = copy.deepcopy(mdefs[1])
        with pytest.raises(TypeError):
            mdefs[1].emfetch_opts = "not a dict"

    def test_reduce(self):
        vals = [42, 90, 2]
        assert _ReduceFuncs.reduce_COUNT(vals) == 3
        assert _ReduceFuncs.reduce_FIRST([]) == None
        assert _ReduceFuncs.reduce_FIRST(vals) == 42
        assert _ReduceFuncs.reduce_LAST(vals) == 2
        assert _ReduceFuncs.reduce_LAST([]) == None
        assert _ReduceFuncs.reduce_SUM(vals) == 134
        assert _ReduceFuncs.reduce_MIN(vals) == 2
        assert _ReduceFuncs.reduce_MAX(vals) == 90
        assert _ReduceFuncs.reduce_AVG(vals) == (float(134)/3)
        assert _ReduceFuncs.reduce_AVG([]) == None


    #
    # Internal Helpers
    #


# ----------------------------------------------------------------------------


class TestMetSet(object):
    """
    Test MetSet collection of MetricDefs.
    """

    #
    # Setup / Teardown
    #

    def setup_method(self, method):
        self.metset1 = MetSet()

    #
    # Tests
    #

    def test_simple(self):
        self.metset1.validate()

    def test_str(self):
        str(self.metset1)

    def test_add_get(self, mdefs):
        metset1 = self.metset1
        metset1.add_metric(mdefs[1])
        metset1.validate()
        with pytest.raises(TypeError):
            metset1.add_metric('Not a MetricDef')
        metset1.validate()
        mdef2 = metset1.get_metric_by_id(mdefs[1].id)
        assert mdefs[1] == mdef2
        with pytest.raises(KeyError):
            metset1.get_metric_by_id('Invalid ID')
        assert self.metset1.count_metrics() == 1

    #
    # Internal Helpers
    #


