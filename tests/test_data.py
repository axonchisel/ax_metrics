"""
Ax_Metrics - Test foundation data package

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import pytest


# ----------------------------------------------------------------------------



class TestDataPoint(object):
    """
    Test single DataPoint class.
    """

    #
    # Setup / Teardown
    #

    #
    # Tests
    #

    def test_str(self, dpoints):
        str(dpoints[1])

    def test_expected(self, dts, dpoints):
        assert dpoints[1].tmrange.inc_begin == dts[0]
        assert dpoints[1].tmrange.exc_end == dts[1]
        assert dpoints[1].value == 42

    def test_set_get(self, dpoints):
        dpoints[1].tmrange = dpoints[2].tmrange
        dpoints[1].value = dpoints[2].value
        assert dpoints[1].tmrange == dpoints[2].tmrange
        assert dpoints[1].value == dpoints[2].value

    def test_bad_tmrange(self, dpoints):
        with pytest.raises(TypeError):
            dpoints[1].tmrange = 'Not a TimeRange'
        with pytest.raises(TypeError):
            dpoints[1].tmrange = None

    def test_bad_value(self, dpoints):
        dpoints[1].value = None  # None allowed
        with pytest.raises(TypeError):
            dpoints[1].value = 'Not a number'

    def test_validate(self, dpoints):
        dpoints[1].validate()
        assert dpoints[1].is_valid() == True
        assert dpoints[0].is_valid() == False

    def test_missing(self, dpoints):
        assert dpoints[1].is_missing() == False
        dpoints[1].value = None
        assert dpoints[1].is_missing() == True

    #
    # Internal Helpers
    #


# ----------------------------------------------------------------------------


class TestDataSeries(object):
    """
    Test DataSeries class.
    """

    #
    # Setup / Teardown
    #

    #
    # Tests
    #

    def test_str(self, dseries):
        str(dseries[1])

    def test_expected(self, dseries):
        assert dseries[1].tmfrspec.smooth_val == 4
        assert dseries[1].mdef.time_field == 'when'

    def test_set_get(self, dseries):
        dseries[1].tmfrspec = dseries[2].tmfrspec
        dseries[1].mdef = dseries[2].mdef
        assert dseries[1].tmfrspec == dseries[2].tmfrspec
        assert dseries[1].mdef == dseries[2].mdef

    def test_points(self, dpoints, dseries):
        assert dseries[1].count_points() == 0
        dseries[1].add_point(dpoints[1])
        dseries[1].add_point(dpoints[2])
        assert dseries[1].count_points() == 2
        assert dseries[1].get_point(0) == dpoints[1]
        assert dseries[1].get_point(1) == dpoints[2]
        lst = dseries[1].iter_points()
        with pytest.raises(Exception):
            lst.pop()
        assert len(list(lst)) == 2
        dseries[1].reset_points()
        assert dseries[1].count_points() == 0
        with pytest.raises(TypeError):
            dseries[1].add_point('Not a DataPoint')

    def test_add_points(self, dpoints, dseries):
        dpoints = [dpoints[1], dpoints[2]]
        dseries[1].add_points(dpoints)

    def test_div(self, dpoints, dseries):
        dpoints = [dpoints[1], dpoints[2]]
        dseries[1].add_points(dpoints)
        dseries[2].add_points(dpoints)
        dseries[1].div_series(dseries[2])
        assert dseries[1].get_point(0).value == 1

    def test_div_diff_len(self, dpoints, dseries):
        dseries[1].add_points([dpoints[1], dpoints[2]])
        dseries[2].add_points([dpoints[1]])
        dseries[1].div_series(dseries[2])
        assert dseries[1].get_point(0).value is not None
        assert dseries[1].get_point(1).value is None

    def test_div_none1(self, dpoints, dseries):
        dseries[1].add_points([dpoints[1], dpoints[2]])
        dseries[2].add_points([dpoints[1], dpoints[3]])
        dpoints[2].value = None
        dseries[1].div_series(dseries[2])
        assert dseries[1].get_point(0).value is not None
        assert dseries[1].get_point(1).value is None

    def test_div_none2(self, dpoints, dseries):
        dseries[1].add_points([dpoints[1], dpoints[2]])
        dseries[2].add_points([dpoints[1], dpoints[3]])
        dpoints[3].value = None
        dseries[1].div_series(dseries[2])
        assert dseries[1].get_point(0).value is not None
        assert dseries[1].get_point(1).value is None

    def test_reduce(self, dseries):
        ds = dseries[3]
        with pytest.raises(ValueError):
            assert ds.reduce('Not valid mdef func')
        assert ds.reduce('COUNT') == 3
        assert ds.reduce('SUM') == 134
        # (More reduce tests in test_metricdef)

    def test_missing(self, dpoints, dseries):
        dseries[1].add_point(dpoints[1])
        dseries[1].add_point(dpoints[2])
        assert dseries[1].count_missing() == 0
        dpoints[1].value = None
        assert dseries[1].count_missing() == 1
        dpoints[2].value = None
        assert dseries[1].count_missing() == 2

    def test_bad_tmfrspec(self, dseries):
        with pytest.raises(TypeError):
            dseries[1].tmfrspec = 'Not a FrameSpec'
        with pytest.raises(TypeError):
            dseries[1].tmfrspec = None

    def test_bad_mdef(self, dseries):
        with pytest.raises(TypeError):
            dseries[1].mdef = 'Not a MetricDef'
        with pytest.raises(TypeError):
            dseries[1].mdef = None

    #
    # Internal Helpers
    #


# ----------------------------------------------------------------------------


class TestMultiDataSeries(object):
    """
    Test MultiDataSeries class.
    """

    #
    # Setup / Teardown
    #

    #
    # Tests
    #

    def test_str(self, mdseries):
        str(mdseries[1])

    def test_expected(self, mdseries):
        assert mdseries[1].get_series(1).id == 's2'

    def test_series(self, dseries, mdseries):
        assert mdseries[1].count_series() == 2
        mdseries[1].add_series(dseries[0])
        assert mdseries[1].count_series() == 3

    def test_iter(self, dseries, mdseries):
        dslist = list(mdseries[2].iter_series())
        assert dslist == [dseries[1], dseries[3]]
        dslist = list(mdseries[2].iter_primary_series())
        assert dslist == [dseries[1]]
        dslist = list(mdseries[2].iter_ghost_series())
        assert dslist == [dseries[3]]

    def test_add_bad(self, mdseries):
        with pytest.raises(TypeError):
            mdseries[1].add_series('Not a DataSeries')

    def test_series_by_id(self, dseries, mdseries):
        s2 = mdseries[1].get_series_by_id('s2')
        assert s2 == dseries[2]
        with pytest.raises(KeyError):
            mdseries[1].get_series_by_id('Bogus Id')

    #
    # Internal Helpers
    #


