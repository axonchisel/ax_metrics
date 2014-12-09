# -*- coding: utf-8 -*-
"""
Ax_Metrics - Common pytest configuration.

Note: 'conftest.py' is a magic filename used by py.test.

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import pytest
from datetime import datetime

from .util import dt

import axonchisel.metrics.foundation.metricdef.metricdef as metricdef
import axonchisel.metrics.foundation.chrono.timerange as timerange
import axonchisel.metrics.foundation.chrono.framespec as framespec
import axonchisel.metrics.foundation.chrono.ghost as ghost
import axonchisel.metrics.foundation.data.point as point
import axonchisel.metrics.foundation.data.series as series
import axonchisel.metrics.foundation.data.multi as multi
import axonchisel.metrics.foundation.query.query as query
import axonchisel.metrics.foundation.query.qdata as qdata



# ----------------------------------------------------------------------------
# Basic fixtures


@pytest.fixture
def dts():
    """Fixture with common datetime objects."""
    return [
        dt('2014-02-01'),
        dt('2014-03-01'),
        dt('2014-04-14 16:42:45'), # (monday)
        dt('2014-04-15 16:42:45'), # (tuesday)
        dt('2014-02-14 16:30:45 001234'), # (friday)
        dt('2014-04-14 16:42:45 001234'), # (monday)
    ]


# ----------------------------------------------------------------------------
# foundation.chrono fixtures


@pytest.fixture
def tmranges(dts):
    """Fixture with common TimeRange objects."""
    return [
        timerange.TimeRange(),
        timerange.TimeRange(inc_begin=dts[0], exc_end=dts[1], anchor=dts[0]),
        timerange.TimeRange(inc_begin=dts[2], exc_end=dts[3], anchor=dts[2]),
        timerange.TimeRange(inc_begin=dts[4], exc_end=dts[5], anchor=dts[4]),
    ]

@pytest.fixture
def tmfrspecs():
    """Fixture with common FrameSpec objects."""
    return [
        framespec.FrameSpec(),
        framespec.FrameSpec(smooth_val=4, smooth_unit='HOUR')
    ]


# ----------------------------------------------------------------------------
# foundation.metricdef fixtures


@pytest.fixture
def mdefs():
    """Fixture with common MetricDef objects."""
    return [
        metricdef.MetricDef(),
        metricdef.MetricDef(
            id = 'mdef1',
            emfetch_id   = 'emfetchid',
            emfetch_opts = {'foo': 123, 'bar': {'zig':"Zoom", 'zag':"Boom"}},
            table        = 'tblname',
            func         = 'COUNT',
            time_field   = 'when',
            time_type    = 'TIME_DATE',
            data_field   = 'myval',
            data_type    = 'NUM_INT',
            # filters,
        ),
    ]

@pytest.fixture
def filters():
    """Fixture with common Filter objects."""
    return [
        metricdef.Filter(),
        metricdef.Filter(field='ffield'),
        metricdef.Filter(op='EQ'),
        metricdef.Filter(field='ffield', op='EQ'),
        metricdef.Filter(field='ffield', op='EQ', value=123),
    ]



# ----------------------------------------------------------------------------
# foundation.data fixtures


@pytest.fixture
def dpoints(tmranges):
    """Fixture with common DataPoint objects."""
    return [
        point.DataPoint(),
        point.DataPoint(tmrange=tmranges[1], value=42),
        point.DataPoint(tmrange=tmranges[2], value=90),
        point.DataPoint(tmrange=tmranges[3], value=2),
    ]

@pytest.fixture
def dseries(mdefs, tmfrspecs, dpoints):
    """Fixture with common DataSeries objects."""
    dseries3 = series.DataSeries(id='s3',
        mdef=mdefs[1], tmfrspec=tmfrspecs[1],
        ghost=ghost.Ghost('PREV_PERIOD1'))
    dseries3.add_point(dpoints[1])
    dseries3.add_point(dpoints[2])
    dseries3.add_point(dpoints[3])

    dseries4 = series.DataSeries(id=u'sérîes4',
        mdef=mdefs[1], tmfrspec=tmfrspecs[1])
    dseries4.add_point(dpoints[1])
    dseries4.add_point(dpoints[2])
    dseries4.add_point(dpoints[3])

    return [
        series.DataSeries(),
        series.DataSeries(id='s1',
            mdef=mdefs[1], tmfrspec=tmfrspecs[1]),
        series.DataSeries(id='s2',
            mdef=mdefs[1], tmfrspec=tmfrspecs[1]),
        dseries3,
        dseries4,
    ]

@pytest.fixture
def mdseries(dseries):
    """Fixture with common MultiDataSeries objects."""
    mdseries1 = multi.MultiDataSeries()
    mdseries1.add_series(dseries[1])
    mdseries1.add_series(dseries[2])
    mdseries2 = multi.MultiDataSeries()
    mdseries2.add_series(dseries[1])
    mdseries2.add_series(dseries[3])
    mdseries3 = multi.MultiDataSeries()
    mdseries3.add_series(dseries[4])
    mdseries3.add_series(dseries[3])
    return [
        multi.MultiDataSeries(),
        mdseries1,
        mdseries2,
        mdseries3,
    ]


# ----------------------------------------------------------------------------
# foundation.query fixtures

@pytest.fixture
def qmetrics():
    """Fixture with common QMetric objects."""
    return [
        qdata.QMetric(),
        qdata.QMetric(metric_id='metric1'),
        qdata.QMetric(metric_id='metric1'),
    ]

@pytest.fixture
def queries(qmetrics):
    """Fixture with common Query objects."""
    q2 = query.Query(id='q2')
    q2.qdata.add_qmetric(qmetrics[1])
    q3 = query.Query(id='q3')
    q3.qdata.add_qmetric(qmetrics[1])
    q3b = query.Query(id='q3')
    q3b.qdata.add_qmetric(qmetrics[2])
    q3b.qghosts.add_ghost(ghost.Ghost('PREV_PERIOD1'))
    return [
        query.Query(),
        query.Query(id='q1'),
        q2,
        q3,
        q3b,
    ]














