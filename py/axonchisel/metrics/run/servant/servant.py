"""
Ax_Metrics - Servant Main Controller - Recommended Ax_Metrics Public Interface

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import time
import copy

from axonchisel.metrics.foundation.ax.obj import AxObj
import axonchisel.metrics.foundation.ax.plugin as axplugin
from axonchisel.metrics.foundation.data.multi import MultiDataSeries
from axonchisel.metrics.foundation.query.qghosts import QGhosts
from axonchisel.metrics.io.erout.interface import EROut
from axonchisel.metrics.run.mqengine.mqengine import MQEngine

from .config import ServantConfig
from .request import ServantRequest
from .state import ServantState

import logging
log =  logging.getLogger(__name__)


# ----------------------------------------------------------------------------


class Servant(AxObj):
    """
    Servant Main Controller and public interface.
    This is the recommended application layer interface to Ax_Metrics.

    Usage:
      1. Load MetSet (all metrics) and QuerySet (all queries).
      2. Construct and populate ServantConfig object, including
         MetSet, QuerySet, and emfetch_extinfo and erout_extinfo
         (containing output targets such as streams to write to).
      3. Construct Servant instance around ServantConfig.
      4. Construct and populate ServantRequest object, including
         list of queries (by id) to run and list of EROut plugins (by id)
         to process results with.
      5. Invoke servant.query(request).
      6. Optionally repeat with additional ServantRequests.

    Lifecycle: A Servant instance can process as many requests
    as desired, but only one at a time.
    EROut plugins are created and destroyed around each request
    (which may itself contain multiple queries).
    """

    def __init__(self, config):
        # Set valid default state:
        self._config          = None  # (ServantConfig)
        self._state           = None  # (ServantState)
        self._reset_state()

        # Apply initial values from kwargs:
        self._assert_type("config", config, ServantConfig)
        self._config = config

        # Log begin:
        log.info("Servant initialized (%s)", config)


    #
    # Public Methods
    #

    def process(self, request):
        """
        Main entry-point to process ServantRequest.
        """
        self._assert_type("request", request, ServantRequest)

        # Log begin:
        t0 = time.time()
        log.info("Processing Request %s", request)

        self._reset_state(request)
        self._create_erouts()
        self._create_mqengine()
        self._run_queries()
        self._destroy_erouts()

        # Log end:
        t9 = time.time()
        log.info("Completed Request %s in %0.3fs", request, t9-t0)


    #
    # Public Properties
    #

    @property
    def config(self):
        """ServantConfig, as specified at construction time."""
        return self._config


    #
    # Internal Methods
    #

    def _reset_state(self, request=None):
        """Reset internal state, optionally around given request."""
        self._state = ServantState()
        if request is not None:
            self._state.request = request

    def _create_erouts(self):
        """Instantiate and startup the EROut plugins and add to state."""
        erout_plugin_ids = self._state.request.erout_plugin_ids
        log.info("Creating EROuts (%s)", erout_plugin_ids)
        for id in erout_plugin_ids:
            ero = self._create_erout(id)
            self._state.erouts.append(ero)

    def _create_erout(self, erout_plugin_id):
        """Instantiate and startup single EROut plugin by id, returning it."""
        plugin_load = {
            'what': "EROut Plugin",
            'def_module_name': 'axonchisel.metrics.io.erout.plugins',
            'def_cls_name_pfx': 'EROut_',
            'require_base_cls': EROut,
            'plugin_id': erout_plugin_id,
        }
        cls = axplugin.load_plugin_class(**plugin_load)
        extinfo = self._config.erout_extinfo_for(erout_plugin_id)
        ero = cls(extinfo=extinfo)
        ero.plugin_create()
        return ero

    def _destroy_erouts(self):
        """Final destroy cleanup on EROut plugins."""
        log.info("Destroying EROuts (%s)", self._state.erouts)
        for ero in self._state.erouts:
            ero.plugin_destroy()

    def _create_mqengine(self):
        """Create and configure MQEngine, storing in state."""
        log.info("Creating MQEngine")
        self._state.mqengine = MQEngine(
            metset = self._config.metset,
            emfetch_extinfo = self._config.emfetch_extinfo,
        )

    def _run_queries(self):
        """Run our queries and output results -- the core logic loop."""
        # Iterate requested queries:
        query_ids = self._state.request.query_ids
        for i, query_id in enumerate(query_ids):

            log.info("Running query (%d/%d) #%s", i+1, len(query_ids), query_id)

            # Load and adjust query:
            q = self._config.queryset.get_query_by_id(query_id)
            if self._state.request.collapse:
                q = self._collapse_query(q)
            if self._state.request.noghosts:
                q = self._bust_query_ghosts(q)

            # Run query in MQEngine
            mdseries = self._state.mqengine.query(q)
            if self._state.request.collapse:
                mdseries = self._collapse_mdseries(mdseries)

            # Process query results through all EROuts:
            for ero in self._state.erouts:
                ero.output(mdseries, query=q)

    def _collapse_query(self, q):
        """
        Return copy of query, collapsed for collapse mode.
        Collapsing the query does:
          - query framespec granularity is set to match range unit
          - query framespec accumulate mode is enabled
        """
        q = copy.deepcopy(q)
        tmfrspec = q.qtimeframe.tmfrspec
        tmfrspec.accumulate = True
        tmfrspec.gran_unit = tmfrspec.range_unit
        return q

    def _bust_query_ghosts(self, q):
        """
        Return copy of query, with ghosts removed.
        """
        q = copy.deepcopy(q)
        q.qghosts = QGhosts()
        return q

    def _collapse_mdseries(self, mdseries):
        """
        Return copy of MultiDataSeries, collapsed for collapse mode.
        Collapsing the MultiDataSeries does:
         - only last data point of each series is preserved.
        """
        mdseries2 = MultiDataSeries()
        for dseries in mdseries.iter_series():
            dseries2 = copy.deepcopy(dseries)
            dseries2.reset_points()
            dseries2.add_point(dseries.get_point(-1)) # (keep only last point)
            mdseries2.add_series(dseries2)
        return mdseries2

    def __unicode__(self):
        return (u"Servant({self._config}, {self._state})"
            .format(self=self))




