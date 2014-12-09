"""
Ax_Metrics - MQEngine metrics query running engine

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import collections
import time

from axonchisel.metrics.foundation.ax.obj import AxObj
import axonchisel.metrics.foundation.ax.plugin as axplugin

from axonchisel.metrics.foundation.chrono.stepper import Stepper
from axonchisel.metrics.foundation.metricdef.metset import MetSet
from axonchisel.metrics.foundation.data.point import DataPoint
from axonchisel.metrics.foundation.data.series import DataSeries 
from axonchisel.metrics.foundation.data.multi import MultiDataSeries 
from axonchisel.metrics.foundation.query.query import Query
import axonchisel.metrics.io.emfetch.base

from .mqestate import MQEState

import logging
log =  logging.getLogger(__name__)


# ----------------------------------------------------------------------------


# Special extinfo domain for common property defaults.
EXTINFO_DOMAIN_DEFAULT = '_default'


# ----------------------------------------------------------------------------


class MQEngine(AxObj):
    """
    Metrics Query Engine - executes queries, yielding data.

    MQEngine has access to a MetSet of metrics.
    It can execute a Query to generate MultiDataSeries result.

    Lifecycle: An MQEngine instance can execute as many queries
    as desired, but only one at a time.
    """

    def __init__(self,
        metset,
        emfetch_extinfo = None  #  dict  (map pluginid:dict)
    ):
        # Set valid default state:
        self._metset          = MetSet()
        self._emfetch_extinfo = dict()

        # Apply initial values from kwargs:
        self.metset           = metset
        if emfetch_extinfo is not None:
            self.emfetch_extinfo  = emfetch_extinfo

        # Prep internal state:
        self._state = MQEState(self)


    #
    # Public Methods
    #

    def query(self, q):
        """
        Main entrypoint to execute a Query and return a MultiDataSeries.
        """

        # Prep:
        self._assert_type("query", q, Query)
        self._state.reset(query=q)
        self._state.pin_tmfrspec()

        # Log begin:
        t0 = time.time()
        log.info("Executing %s", q)

        # Fetch stats:
        self._fetch_main_metrics()
        self._fetch_ghost_metrics()

        # Log end:
        t9 = time.time()
        log.info("Completed %s in %0.3fs", q, t9-t0)

        # Return MultiDataSeries:
        return self._state.mdseries

    def emfetch_extinfo_for(self, plugin_id):
        """
        Construct and return dict with EMFetcher extinfo for given plugin_id.
        Uses _default dict (if any), extended with plugin_id dict.
        """
        extinfo = dict(self.emfetch_extinfo.get(EXTINFO_DOMAIN_DEFAULT, {}))
        extinfo.update(self.emfetch_extinfo.get(plugin_id, {}))
        return extinfo


    #
    # Public Properties
    #

    @property
    def metset(self):
        """MetSet collection of known MetricDefs."""
        return self._metset
    @metset.setter
    def metset(self, val):
        self._assert_type("metset", val, MetSet)
        self._metset = val

    @property
    def emfetch_extinfo(self):
        """
        Dict with extinfo (dicts) for EMFetchers, keyed by emfetch_id.
        This must be a dict mapping from EMFetch Id (string) to extinfo dict.
        Key '_default' dict (if present) acts as base, extended by
        plugin-specific dicts.
        See macro method: self.emfetch_extinfo_for()
        """
        return self._emfetch_extinfo
    @emfetch_extinfo.setter
    def emfetch_extinfo(self, val):
        self._assert_type("emfetch_extinfo", val, collections.Mapping)
        self._emfetch_extinfo = val


    #
    # Internal Methods
    #

    def _fetch_main_metrics(self):
        """
        Fetch the main metrics from the query QData.
        Accumulates into MultiDataSeries.
        """
        log.info("Processing primary qmetrics from %s", self._state.query)

        # Fetch primary metrics:
        series_id_pfx = 'Q_{q.id}_M_'.format(
            q=self._state.query)
        self._fetch_metrics(series_id_pfx)


    def _fetch_ghost_metrics(self):
        """
        Fetch the ghost metrics from the query QGhosts.
        """
        log.info("Processing ghost qmetrics from %s", self._state.query)

        # Loop over Ghosts:
        ghosts = self._state.query.qghosts.get_ghosts()
        for i, ghost in enumerate(ghosts):

            log.info("Processing ghost %d/%d %s from %s",
                i+1, len(ghosts), ghost, self._state.query)

            # Fetch ghost metrics:
            series_id_pfx = 'Q_{q.id}_G_{g.gtype}_'.format(
                g=ghost, q=self._state.query)
            self._fetch_metrics(series_id_pfx, ghost=ghost)


    def _fetch_metrics(self, series_id_pfx, ghost=None):
        """
        Fetch helper - Fetch metrics for tmfrspec with optional Ghost.
        Adds a DataSeries for each defined metric.
        Typically invoked for normal metrics as well as for each ghost.
        """
        # Prep:
        tmfrspec = self._state.tmfrspec

        # Loop over QMetrics:
        qmetrics = list(self._state.query.qdata.iter_qmetrics())
        for i, qmetric in enumerate(qmetrics):

            log.info("Processing qmetric %d/%d %s from %s",
                i+1, len(qmetrics), qmetric, self._state.query)

            # Find MetricDefs:
            mdef = self.metset.get_metric_by_id(qmetric.metric_id)
            divmdef = None
            if qmetric.div_metric_id is not None:
                divmdef = self.metset.get_metric_by_id(qmetric.div_metric_id)

            # Create and add new (empty) DataSeries:
            series_id = "{pfx}{n}_{mdef.id}{div}".format(
                pfx=series_id_pfx, n=i+1, mdef=mdef, 
                div='_div_%s'%divmdef.id if divmdef is not None else '')
            dseries = DataSeries(id=series_id, query_id=self._state.query.id,
                mdef=mdef, tmfrspec=tmfrspec, ghost=ghost, 
                label=qmetric.label)
            self._state.mdseries.add_series(dseries)

            # Fetch data into new DataSeries:
            self._fetch_series(dseries)

            # If div metric, fetch it too, and divide into existing data:
            if divmdef is not None:
                divsid = "DIV_{pfx}{n}_{divmdef.id}".format(
                    pfx=series_id_pfx, n=i+1, divmdef=divmdef)
                dseries_div = DataSeries(id=divsid,
                    mdef=divmdef, tmfrspec=tmfrspec, ghost=ghost)
                self._fetch_series(dseries_div)
                dseries.div_series(dseries_div)

            log.info("Obtained data from %s: %s",
                qmetric, dseries)


    def _fetch_series(self, dseries):
        """
        Fetch a single DataSeries for MetricDef defined in series.
        Adds DataPoints to series.
        """

        log.info("Fetching series %s", dseries)

        # Load EMFetcher plugin (AxPluginLoadError on error):
        emf = self._make_emfetcher_for_mdef(dseries.mdef)
        emf.plugin_create()

        # Step through, fetching data points, assembling series:
        try:
            stepper = Stepper(dseries.tmfrspec, ghost=dseries.ghost)
            for step in stepper.steps():
                # print step
                dpoint = emf.fetch(step)
                dseries.add_point(dpoint)
        finally:
            emf.plugin_destroy()


    def _make_emfetcher_for_mdef(self, mdef):
        """
        Construct and return EMFetcher for given MetricDef.
        """
        # Get extinfo for this emfetch_id:
        extinfo = self.emfetch_extinfo_for(mdef.emfetch_id)

        # Make EMFetcher (AxPluginLoadError on error):
        emf_cls = axplugin.load_plugin_class(
            mdef.emfetch_id,
            what="EMFetch Plugin",
            def_module_name='axonchisel.metrics.io.emfetch.plugins',
            def_cls_name_pfx='EMFetcher_',
            require_base_cls=axonchisel.metrics.io.emfetch.base.EMFetcherBase,
        )
        emf = emf_cls(mdef, extinfo)

        return emf


    def __unicode__(self):
        return (u"MQEngine({self._state})"
        ).format(self=self)



