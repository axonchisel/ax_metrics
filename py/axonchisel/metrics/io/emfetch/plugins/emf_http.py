"""
Ax_Metrics - EMFetch plugin 'http'

Uses URL format str to make HTTP requests to get data.

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import json

import requests

import axonchisel.metrics.foundation.ax.dictutil as dictutil

from axonchisel.metrics.foundation.data.point import DataPoint

from ..base import EMFetcherBase

import logging
log =  logging.getLogger(__name__)


# ----------------------------------------------------------------------------


# Allowed HTTP methods
HTTP_METHODS = {
    'GET': {},
    'POST': {},
}

# Allowed response formats
RESPONSE_FORMATS = {
    'JSON': {},
}


# ----------------------------------------------------------------------------



class EMFetcher_http(EMFetcherBase):
    """
    EMFetch (Extensible Metrics Fetch) Plugin 'http'.
    Uses URL format str and params to make HTTP request to get data.
    Navigates and extracts result from JSON response.
    MetricDef emfetch_opts determine specific behavior.
    """
    
    #
    # Abstract Method Implementations
    #

    # abstract
    def plugin_create(self):
        """
        Invoked once by MQEngine to allow plugin to setup what it needs.
        Always called before any fetch() invocations.
        """
        log.info(u"%s plugin_create (%s)",
            self, self.options.get('options'))
        self.rsession = None
        if not self.plugin_option('options.isolate', default=False):
            self.rsession = self._requests_lib().Session()

    # abstract
    def plugin_destroy(self):
        """
        Invoked once by MQEngine to allow plugin to clean up after itself.
        Always called after create() and any fetch() invocations, assuming
        no fatal errors occurred.
        """
        log.info(u"%s plugin_destroy", self)
        if self.rsession:
            self.rsession.close()


    # abstract
    def plugin_fetch(self, tmrange):
        """
        EMFetcher plugins must implement this abstract method.
        Invoked by fetch() after parameters are validated.
        
        Returns a single DataPoint.
            (axonchisel.metrics.foundation.data.point.DataPoint)

        Parameters:

          - tmrange : specification of time range to gather data for.
            (axonchisel.metrics.foundation.chrono.timerange.TimeRange)
            Also available in TimeRange_time_t format as self._tmrange.
        """
        # Format URL with current TimeRange:
        url_spec = self.plugin_option('request.url')
        url = self._format_str(url_spec, what="url")

        # Format URL params:
        req_params_spec = self.plugin_option('request.params', dict())
        req_params = self._format_request_params(req_params_spec)

        # Execute request:
        try:
            log.info(u"%s requesting %s from %s", self, url, tmrange)
            method = self.plugin_option('request.method')
            str_resp = self._execute_request(method, url, req_params)
            log.debug(u"%s retrieved response, size=%d", self, len(str_resp))
        except Exception as e:
            log.warn(u"%s Error requesting from %s: %r", self, url, e)
            raise

        # Process response:
        try:
            resp_spec = self.plugin_option('response')
            value = self._process_response(resp_spec, str_resp)
        except Exception as e:
            log.warn(u"%s Error processing response from %s: %r", self, url, e)
            log.debug(u"%s problematic response: %s", self, str_resp)
            raise

        # Create and return DataPoint:
        dpoint = DataPoint(tmrange=tmrange, value=value)
        log.debug(u"%s returning %s", self, dpoint)
        return dpoint


    #
    # Dependency Injection (for testing)
    #

    def _use_requests_lib(self, requests_lib):
        """Inject dependency alternate 'requests' lib, e.g. for testing."""
        self._requests_alt_lib = requests_lib

    def _requests_lib(self):
        """Get 'requests' lib, or alternate one if dependency injected."""
        if hasattr(self, '_requests_alt_lib'):
            return self._requests_alt_lib  # use injected library
        return requests                    # use actual library


    #
    # Internal Methods
    #

    def _format_request_params(self, req_params_spec):
        """
        Format request params.
        Return dict string:string.
        Param spec is as from 'request.params' emfetch_opts.
        """
        params = dict()
        for k, v in req_params_spec.iteritems():
            params[k] = self._format_str(v, 
                what="req param (%s)"%k, od_defaults="")
        return params

    def _execute_request(self, method, url, req_params):
        """
        Make the actual HTTP request as described.
        Return raw response content.
        """
        # Requests lib session has same signature as lib itself,
        # so get appropriate object in r that we can work with:
        r = self.rsession
        if not r:  # this is the case when isolate=True
            r = self._requests_lib()

        # Build common request method kwargs:
        kwargs = {
            'timeout': self.plugin_option('options.timeout', default=None),
            'verify':  self.plugin_option('options.verify_ssl', default=True),
        }

        # Execute request:
        if method not in HTTP_METHODS:
            raise ValueError((
                "{self} HTTP method '{method}' not supported."
            ).format(self=self, method=method))
        if method == 'GET':
            resp = r.get(url, params=req_params, **kwargs)
        elif method == 'POST':
            resp = r.post(url, data=req_params, **kwargs)
        resp.raise_for_status()

        return resp.text

    def _process_response(self, resp_spec, str_resp):
        """
        Extract, process, coerce, and return actual data from within response.
        Return numeric value or None.
        Response spec is as from 'response' emfetch_opts.
        """
        resp_format = resp_spec.get('format')
        if resp_format not in RESPONSE_FORMATS:
            raise ValueError(("{self} response format "+
                "'{resp_format}' not supported."
            ).format(self=self, resp_format=resp_format))

        val = None
        if resp_format == 'JSON':
            val = self._process_response_json(resp_spec, str_resp)

        val = self._process_adjust_val(val)
        return val

    def _process_response_json(self, resp_spec, str_resp):
        """
        Parse, navigate JSON response path to extract value, returning as is.
        Raises KeyError if path not navigable, 
        or JSON error if not valid JSON.
        """
        path = resp_spec.get('path', '')
        try:
            resp = json.loads(str_resp)
        except ValueError as e:
            raise ValueError((
                "{self} response not valid JSON: {e} "
            ).format(self=self, e=e))
        val = dictutil.dict_get_by_path(resp, path, what="JSON response")

        return val

    def _process_adjust_val(self, val):
        """
        Adjust/coerce extracted val into final format specified by MetricDef.
        """
        data_type = self.mdef.data_type
        if val is None:
            return None
        val = float(val)
        if data_type == 'NUM_INT':
            val = int(round(val))
        elif data_type == 'MONEY_INT100':
            val = round(val / 100, 2)
        elif data_type == 'MONEY_FLOAT100':
            val = round(val / 100, 2)
        return val




