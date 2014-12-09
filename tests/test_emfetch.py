"""
Ax_Metrics - Test io.emfetch package

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import pytest

import axonchisel.metrics.foundation.chrono.timerange as timerange
from axonchisel.metrics.io.emfetch.interface import EMFetcher
from axonchisel.metrics.io.emfetch.base import EMFetcherBase
import axonchisel.metrics.io.emfetch.plugins.emf_random as emf_random
from axonchisel.metrics.io.emfetch.tmrange_time_t import TimeRange_time_t


# ----------------------------------------------------------------------------


class TestEMFetcher(object):
    """
    Test general EMFetcher.
    """

    #
    # Setup / Teardown
    #

    def setup_method(self, method):
        self.extinfo = {'a': 65, 'b': "LilB", 'special': { 'q': 34, 'z': 35 } }


    #
    # Tests
    #

    def test_base_not_impl(self, mdefs, tmranges):
        with pytest.raises(NotImplementedError):
            absbase = EMFetcher(mdefs[1])
        class FakeBase(EMFetcher):
            def __init__(self, mdef, extinfo=None):
                pass
        absbase = FakeBase(mdefs[1])
        with pytest.raises(NotImplementedError):
            absbase.plugin_create()
        with pytest.raises(NotImplementedError):
            absbase.plugin_destroy()
        with pytest.raises(NotImplementedError):
            absbase.plugin_fetch(tmranges[1])


    def test_bad_metricdef(self, mdefs):
        with pytest.raises(TypeError):
            emf_random.EMFetcher_random('Not MetricDef')
        mdefs[1].emfetch_id = ''
        with pytest.raises(ValueError):
            emf_random.EMFetcher_random(mdefs[1])

    def test_bad_timerange(self, mdefs):
        emf = emf_random.EMFetcher_random(mdefs[1])
        with pytest.raises(TypeError):
            emf.fetch('Not TimeRange')
        tmrange3 = timerange.TimeRange()
        with pytest.raises(ValueError):
            emf.fetch(tmrange3)

    def test_random(self, mdefs, tmranges):
        emf = emf_random.EMFetcher_random(mdefs[1])
        emf.plugin_create()
        for x in range(100):
            dpoint1 = emf.fetch(tmranges[1])
            assert (0 <= dpoint1.value <= 100)
        emf.configure(options={'random': {'round': True}})
        assert isinstance(emf.fetch(tmranges[1]).value, (int, long))
        emf.plugin_destroy()

    def test_bad_datapoint(self, mdefs, tmranges):
        class EMFetcher_bad_datapoint(EMFetcherBase):
            def plugin_create(self): pass
            def plugin_destroy(self): pass
            def plugin_fetch(self, tmrange): return 'Not DataPoint'
        emf = EMFetcher_bad_datapoint(mdefs[1])
        with pytest.raises(TypeError):
            emf.fetch(tmranges[1])

    def test_plugin_option(self, mdefs):
        emf = emf_random.EMFetcher_random(mdefs[1])
        assert emf.plugin_option('foo') == 123
        assert emf.plugin_option('bar.zig') == "Zoom"
        with pytest.raises(KeyError):
            emf.plugin_option('BOGUS')
        assert emf.plugin_option('BOGUS', default="D") == "D"

    def test_plugin_extinfo(self, mdefs):
        emf = emf_random.EMFetcher_random(mdefs[1], extinfo=self.extinfo)
        assert emf.plugin_extinfo('a') == 65
        assert emf.plugin_extinfo('b') == "LilB"
        with pytest.raises(KeyError):
            emf.plugin_extinfo('BOGUS')
        assert emf.plugin_extinfo('BOGUS', default="D") == "D"

    def test_format_str(self, mdefs, tmranges):
        emf = emf_random.EMFetcher_random(mdefs[1])
        emf.fetch(tmranges[2])  # (causes plugin to set its self._tmrange)
        assert emf._format_str("plain") == "plain"
        assert emf._format_str("My {mdef.table} here") == "My tblname here"
        assert emf._format_str("{tmrange.inc_begin:%Y-%m-%d}") == "2014-04-14"
        assert emf._format_str("{tmrange.exc_end:%Y-%m-%d %H:%M:%S}") == "2014-04-15 16:42:45"
        assert emf._format_str("{tmrange.exc_end:%s}") == "1397605365"

    def test_format_param_str(self, mdefs, tmranges):
        emf = emf_random.EMFetcher_random(mdefs[1], extinfo=self.extinfo)
        emf.fetch(tmranges[2])  # (causes plugin to set its self._tmrange)
        assert emf._format_str("plain") == "plain"
        assert emf._format_str("My {mdef.table} here") == "My tblname here"
        assert emf._format_str("{tmrange.inc_begin:%Y-%m-%d}") == "2014-04-14"
        assert emf._format_str("{tmrange.exc_end:%Y-%m-%d %H:%M:%S}") == "2014-04-15 16:42:45"
        assert emf._format_str("{tmrange.exc_end:%s}") == "1397605365"

    def test_format_param_literal(self, mdefs, tmranges):
        emf = emf_random.EMFetcher_random(mdefs[1], extinfo=self.extinfo)
        emf.fetch(tmranges[2])  # (causes plugin to set its self._tmrange)
        assert emf._format_str('plain') == "plain"
        assert emf._format_str("My {{mdef.table}} here") == "My {mdef.table} here"

    def test_format_param_extinfo(self, mdefs, tmranges):
        emf = emf_random.EMFetcher_random(mdefs[1], extinfo=self.extinfo)
        emf.fetch(tmranges[2])  # (causes plugin to set its self._tmrange)
        assert emf._format_str('{extinfo[a]}') == "65"
        assert emf._format_str('{extinfo[special][q]}') == "34"
        with pytest.raises(KeyError):
            emf._format_str('{extinfo[special][BOGUS]}')

    def test_format_param_bad(self, mdefs, tmranges):
        emf = emf_random.EMFetcher_random(mdefs[1], extinfo=self.extinfo)
        emf.fetch(tmranges[2])  # (causes plugin to set its self._tmrange)
        with pytest.raises(TypeError):
            emf._format_str(12345)
        with pytest.raises(TypeError):
            emf._format_str(None)
        with pytest.raises(KeyError):
            emf._format_str('{BOGUS}')

    def test_format_params(self, mdefs, tmranges):
        emf = emf_random.EMFetcher_random(mdefs[1], extinfo=self.extinfo)
        emf.fetch(tmranges[2])  # (causes plugin to set its self._tmrange)
        params_spec = {
            'plain': "plainval",
            'mdef': "My {mdef.table} here",
            'lit': "{{mdef.table}}",
            'ext': '{extinfo[special][q]}',
        }
        params = dict()
        for k, v in params_spec.iteritems():
            params[k] = emf._format_str(v)
        assert params['plain'] == "plainval"
        assert params['mdef'] == "My tblname here"
        assert params['lit'] == "{mdef.table}"
        assert params['ext'] == "34"

    def test_tmrange_time_t(self, mdefs, tmranges):
        tmrange = TimeRange_time_t(tmranges[2])
        assert tmrange.inc_begin_time_t == 1397518965
        assert tmrange.exc_begin_time_t == 1397518964
        assert tmrange.inc_end_time_t == 1397605364
        assert tmrange.exc_end_time_t == 1397605365




