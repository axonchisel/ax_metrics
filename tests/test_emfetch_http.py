"""
Ax_Metrics - Test io.emfetch 'http' plugin

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import pytest

import axonchisel.metrics.foundation.chrono.timerange as timerange
import axonchisel.metrics.foundation.metricdef.metricdef as metricdef
import axonchisel.metrics.foundation.metricdef.filters as filters
import axonchisel.metrics.foundation.metricdef.mdefl as mdefl
import axonchisel.metrics.io.emfetch.plugins.emf_http as emf_http

from .util import dt, load_test_asset, log_config

import logging


# ----------------------------------------------------------------------------


# Use mock requests lib to simulate all HTTP requests?
# False for some real requests which require an actual API endpoint
# (customized via extinfo).
# Even with False, many requests in this test suite are still mocked.
MOCK_REQUESTS = True


# ----------------------------------------------------------------------------


def setup_module(module):
    # log_config(level=logging.DEBUG)
    log_config(level=logging.INFO)


# ----------------------------------------------------------------------------


class TestEMFetcher_http(object):
    """
    Test EMFetcher 'http'.
    """

    #
    # Setup / Teardown
    #

    def setup_method(self, method):
        self.extinfo = {
            'api_url': 'http://localhost/apidemo/kpi_reduce/',
            'api_key': 'TestKey',
            # 'table_prefix': 'my_',
        }
        # Parse MDefL MetSet:
        self.yaml_metset1 = load_test_asset('metset-http.yml')
        self.parser1 = mdefl.MetSetParser()
        self.metset1 = self.parser1.parse_ystr_metset(self.yaml_metset1)

    #
    # Tests
    #

    def test_maybe_real(self):
        mdef1 = self.metset1.get_metric_by_id('rev_new_sales')
        emfetch1 = emf_http.EMFetcher_http(mdef1, extinfo=self.extinfo)
        if MOCK_REQUESTS:
            self._mock_requests(emfetch1, '{ "body": { "result": 12345 } }')
        emfetch1.plugin_create()
        for x in range(1):
            tmrange = timerange.TimeRange(
                inc_begin=dt('2013-02-01'), exc_end=dt('2013-02-02'))
            dpoint1 = emfetch1.fetch(tmrange)
            print dpoint1
            tmrange = timerange.TimeRange(
                inc_begin=dt('2013-02-02'), exc_end=dt('2013-02-03'))
            dpoint1 = emfetch1.fetch(tmrange)
            print dpoint1
        emfetch1.plugin_destroy()

    def test_mock_good(self, tmranges):
        mdef1 = self.metset1.get_metric_by_id('rev_new_sales')
        emfetch1 = emf_http.EMFetcher_http(mdef1, extinfo=self.extinfo)
        self._mock_requests(emfetch1, '{ "body": { "result": 12345 } }')
        self._run_emfetch(emfetch1, tmranges)

    def test_mock_good_null(self, tmranges):
        mdef1 = self.metset1.get_metric_by_id('rev_new_sales')
        emfetch1 = emf_http.EMFetcher_http(mdef1, extinfo=self.extinfo)
        self._mock_requests(emfetch1, '{ "body": { "result": null } }')
        self._run_emfetch(emfetch1, tmranges)

    def test_mock_good_types(self, tmranges):
        mdef1 = self.metset1.get_metric_by_id('rev_new_sales')
        emfetch1 = emf_http.EMFetcher_http(mdef1, extinfo=self.extinfo)
        self._mock_requests(emfetch1, '{ "body": { "result": 12345.6789 } }')
        mdef1.data_type = 'NUM_INT'
        self._run_emfetch(emfetch1, tmranges)
        mdef1.data_type = 'MONEY_INT100'
        self._run_emfetch(emfetch1, tmranges)
        mdef1.data_type = 'MONEY_FLOAT100'
        self._run_emfetch(emfetch1, tmranges)

    def test_mock_good_isolate(self, tmranges):
        mdef1 = self.metset1.get_metric_by_id('rev_new_sales')
        mdef1.emfetch_opts['options']['isolate'] = True
        emfetch1 = emf_http.EMFetcher_http(mdef1, extinfo=self.extinfo)
        self._mock_requests(emfetch1, '{ "body": { "result": 12345 } }')
        self._run_emfetch(emfetch1, tmranges)

    def test_mock_good_http_post(self, tmranges):
        mdef1 = self.metset1.get_metric_by_id('rev_new_sales')
        mdef1.emfetch_opts['request']['method'] = 'POST'
        emfetch1 = emf_http.EMFetcher_http(mdef1, extinfo=self.extinfo)
        self._mock_requests(emfetch1, '{ "body": { "result": 12345 } }')
        self._run_emfetch(emfetch1, tmranges)

    def test_mock_bad_response_format(self, tmranges):
        mdef1 = self.metset1.get_metric_by_id('rev_new_sales')
        mdef1.emfetch_opts['response']['format'] = 'BogusFormat'
        emfetch1 = emf_http.EMFetcher_http(mdef1, extinfo=self.extinfo)
        self._mock_requests(emfetch1, 'Invalid JSON { XXX')
        with pytest.raises(ValueError) as e:
            self._run_emfetch(emfetch1, tmranges)
        assert "response format" in str(e.value)

    def test_mock_bad_json(self, tmranges):
        mdef1 = self.metset1.get_metric_by_id('rev_new_sales')
        emfetch1 = emf_http.EMFetcher_http(mdef1, extinfo=self.extinfo)
        self._mock_requests(emfetch1, 'Invalid JSON { XXX')
        with pytest.raises(ValueError) as e:
            self._run_emfetch(emfetch1, tmranges)
        assert "not valid JSON" in str(e.value)

    def test_mock_bad_json_content(self, tmranges):
        mdef1 = self.metset1.get_metric_by_id('rev_new_sales')
        emfetch1 = emf_http.EMFetcher_http(mdef1, extinfo=self.extinfo)
        self._mock_requests(emfetch1, '{ "dummy": "dummy" }')
        with pytest.raises(KeyError) as e:
            self._run_emfetch(emfetch1, tmranges)
        assert "not found in 'JSON" in str(e.value)

    def test_mock_bad_http_error(self, tmranges):
        mdef1 = self.metset1.get_metric_by_id('rev_new_sales')
        emfetch1 = emf_http.EMFetcher_http(mdef1, extinfo=self.extinfo)
        self._mock_requests(emfetch1, error="Fake HTTP Error")
        with pytest.raises(ValueError) as e:
            self._run_emfetch(emfetch1, tmranges)
        assert "Fake HTTP Error" in str(e.value)

    def test_mock_bad_http_method(self, tmranges):
        mdef1 = self.metset1.get_metric_by_id('rev_new_sales')
        mdef1.emfetch_opts['request']['method'] = 'BogusMethod'
        emfetch1 = emf_http.EMFetcher_http(mdef1, extinfo=self.extinfo)
        self._mock_requests(emfetch1, '{ "body": { "result": 12345 } }')
        with pytest.raises(ValueError) as e:
            self._run_emfetch(emfetch1, tmranges)
        assert "HTTP method" in str(e.value)


    #
    # Internal Helpers
    #

    def _run_emfetch(self, emfetch1, tmranges):
        """
        Run EMFetch through multiple TimeRanges, returning list of DataPoints.
        Wrapped in plugin create, delete.
        """
        dpoints = list()
        emfetch1.plugin_create()
        for tmrange in tmranges[1:3]:
            dpoint1 = emfetch1.fetch(tmrange)
            dpoints.append(dpoint1)
        emfetch1.plugin_destroy()
        return dpoints

    def _mock_requests(self, emfetch1, resp_text="Response", error=None):
        """
        Inject mock version of requests dependency into given EMFetcher_http.
        Will simulate HTTP call and return resp_text.
        """
        mockRequests = MockRequests(resp_text=resp_text, error=error)
        emfetch1._use_requests_lib(mockRequests)


# ----------------------------------------------------------------------------


class MockRequests(object):
    """
    A light mock version of requests lib.
    Only implements what is used by this test.
    """
    def __init__(self, resp_text="Response", error=None):
        """
        Init with specific text to respond or optional error msg to raise.
        """
        self.resp_text = resp_text
        self.error = error

    def get(self, url, params, **kwargs):
        resp = MockRequestsResponse(self)
        return resp

    def post(self, url, data, **kwargs):
        resp = MockRequestsResponse(self)
        return resp

    def close(self):
        pass

    def Session(self):
        return self

class MockRequestsResponse(object):
    """
    A mock version of requests lib response obj.
    Only implements what is used by this test.
    """
    def __init__(self, mock_requests):
        self.mock_requests = mock_requests

    @property
    def text(self):
        return self.mock_requests.resp_text

    def raise_for_status(self):
        if self.mock_requests.error:
            raise ValueError(
                "Mock Request Error: %s" % self.mock_requests.error)







