"""
Ax_Metrics - Servant Request encapsulation

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


from axonchisel.metrics.foundation.ax.obj import AxObj


# ----------------------------------------------------------------------------


class ServantRequest(AxObj):
    """
    Servant request encapsulation.

    Specifies a list of EROut plugins (by plugin id, loaded dynamically)
    and a list of Queries (by query id, from ServantConfig QuerySet).

    Each of the Queries will be run once and have their output processed
    by each EROut plugins.
    """

    def __init__(self, **kwargs):
        """
        Initialize, optionally overriding any default properties with kwargs.
        """
        # Set valid default state:
        self._query_ids        = list()  # list(str)
        self._erout_plugin_ids = list()  # list(str)
        self._collapse         = False   # bool
        self._noghosts         = False   # bool

        # Apply initial values from kwargs:
        self._init_kwargs(kwargs, [
            'query_ids', 'erout_plugin_ids', 'collapse', 'noghosts',
        ])

        # Validate:
        self._assert_type_list_string(
            "query_ids", self.query_ids)
        self._assert_type_list_string(
            "erout_plugin_ids", self.erout_plugin_ids)


    #
    # Static Factory Methods
    #

    @staticmethod
    def from_params(params):
        """
        Factory: return new ServantRequest parsed from str:str params dict.
        Useful for e.g. parsing web request params.
        Params supported:
            - query : CSL of query ids, e.g. "rev_new_mtd,rev_new_qtd"
            - erout : CSL of erout plugin ids, e.g. "csv,json"
            - collapse : '1' for collapse mode, or '0' (default) for normal
            - noghosts : '1' to disable ghosts, or '0' (default) for normal
        """
        def parse_csl_ids(csl):
            return [id.strip() for id in filter(len, csl.split(','))]
        sreq = ServantRequest()
        sreq.query_ids = parse_csl_ids(params.get('query', ''))
        sreq.erout_plugin_ids = parse_csl_ids(params.get('erout', ''))
        if params.get('collapse') == '1':
            sreq.collapse = True
        if params.get('noghosts') == '1':
            sreq.noghosts = True
        return sreq


    #
    # Public Properties
    #

    @property
    def query_ids(self):
        """List of Query ids (strings) to execute."""
        return self._query_ids
    @query_ids.setter
    def query_ids(self, val):
        self._assert_type_list_string("query_ids", val)
        self._query_ids = val

    @property
    def erout_plugin_ids(self):
        """List of EROut plugin ids (strings) to process results with."""
        return self._erout_plugin_ids
    @erout_plugin_ids.setter
    def erout_plugin_ids(self, val):
        self._assert_type_list_string("erout_plugin_ids", val)
        self._erout_plugin_ids = val

    @property
    def collapse(self):
        """
        Collapse all data into single point? (bool)
        Useful for capturing summaries (e.g. for bullet charts) of more 
        complex query without having to duplicate queries in QuerySet.
        When collapsed:
          - query framespec granularity is set to match range unit
          - query framespec accumulate mode is enabled
          - only the last data point of each series is preserved
        """
        return self._collapse
    @collapse.setter
    def collapse(self, val):
        self._assert_type_bool("collapse", val)
        self._collapse = val

    @property
    def noghosts(self):
        """
        Remove all ghosts? (bool)
        Useful for capturing summaries (e.g. for bullet charts) of more 
        complex query without having to duplicate queries in QuerySet.
        (Who you gonna call?)
        """
        return self._noghosts
    @noghosts.setter
    def noghosts(self, val):
        self._assert_type_bool("noghosts", val)
        self._noghosts = val


    #
    # Internal Methods
    #

    def __unicode__(self):
        return (u"ServantRequest("+
            "queries:{self.query_ids}, "+
            "erouts:{self.erout_plugin_ids}, "+
            "collapse:{self.collapse})"
            ).format(self=self)




