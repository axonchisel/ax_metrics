"""
Ax_Metrics - MQL Metrics Query Language Parser

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import copy
import yaml
from datetime import date, datetime

from axonchisel.metrics.foundation.ax.obj import AxObj

from axonchisel.metrics.foundation.chrono.ghost import Ghost

from .query import Query
from .queryset import QuerySet
from .qdata import QMetric


# ----------------------------------------------------------------------------


class MQLParseError(Exception):
    """Error parsing MQL"""
    pass    


# ----------------------------------------------------------------------------


class QueryParser(AxObj):
    """
    Given raw MQL YAML strings, parse into Query objects.

    Supports multiple parse passes on the same object, allowing defaults and
    extensions of defaults.

    Usage: Create, parse, parse, parse, ..., get, destroy (or reset).

    Variables prefixed with "y" reference parsed YAML currently existing as
    Python structures.
    Variables prefixed with "ystr_" reference raw YAML strings.


    Example partial YAML:

        ---
        id: pct_new_paid_accounts_rolling_30d

        data:
          metrics:
            - metric: num_new_paid_accounts
              div: num_total_paid_accounts
              goal: 10
              goal_mode: CONSTANT
        timeframe:
          range_val: 3
          range_unit: MONTH
          gran_unit: DAY
          mode: CURRENT
          smooth_unit: DAY
          smooth_val: 30
          reframe_dt: 2014-11-01
        format:
          some_erout_plugin_id:
            type: type1
            title: "New Paid Accounts %"
            subtitle: "(rolling 30d)"
        ghosts:
          - PREV_PERIOD1
          - PREV_YEAR1
          - PREV_YEAR2

    """

    def __init__(self, base=None):
        """
        Initialize parser and internal Query.
        If base Query specified, copies as base to extend.
        After parsing, either destroy or call reset to parse a new object.
        """
        self.reset(base=base)


    #
    # Public Methods
    #
    
    def reset(self, base=None):
        """
        Reset and prepare new Query object for parsing.
        If base Query specified, copies as base to extend.
        """
        if base is not None:
            self._assert_type("base", base, Query)
            base = copy.deepcopy(base)
        else:
            base = Query()
        self._query = base

    def get_query(self):
        """
        Get the wrapped up Query object after parsing.
        """
        return self._query

    def parse_ystr_query(self, ystr_query):
        """
        Given raw MQL YAML str, parse into internal Query.
        Only set attributes that are specified, leaving others at default.
        Can be called multiple times to build up the Query.
        Returns currently wrapped Query.
        """
        yquery = yaml.load(ystr_query)
        return self.parse_yquery(yquery)

    def parse_yquery(self, yquery):
        """
        Given dict as parsed from YAML, parse into internal Query.
        Only set attributes that are specified, leaving others at default.
        Can be called multiple times to build up the Query.
        Returns currently wrapped Query.
        """
        self._parse_item(yquery, 'id')
        self._parse_data(yquery)
        self._parse_timeframe(yquery)
        self._parse_format(yquery)
        self._parse_ghosts(yquery)
        return self.get_query()


    #
    # Internal Methods
    #

    def _parse_item(self, yobj, yname, attr=None, obj=None):
        """
        Set object attr to value of specific item in yobj, 
        but only if present.
        If attr unspecified, uses same name as yname.
        If obj unspecified, uses self._query.
        """
        if obj is None:
            obj = self._query
        if yname not in yobj:
            return
        if attr is None:
            attr = yname
        setattr(obj, attr, yobj[yname])

    def _parse_data(self, yquery):
        """
        Helper - Parse data section in yquery.
        """
        ydata = yquery.get('data')
        if ydata is None:
            raise MQLParseError("Query #{query.id} missing data section"
                .format(query=self._query))
        ymetrics = ydata.get('metrics')
        if ymetrics is None:
            raise MQLParseError("Query #{query.id} missing data.metrics"
                .format(query=self._query))
        if not isinstance(ymetrics, list):
            raise MQLParseError("Query #{query.id} data.metrics not list: {t}"
                .format(query=self._query, t=type(ymetrics)))
        for ymetric in ymetrics:
            qmetric1 = self._parse_data_qmetric(ymetric)
            self._query._qdata.add_qmetric(qmetric1)

    def _parse_data_qmetric(self, ymetric):
        """
        Helper - parse single data.metric definition, return QMetric.
        """
        if not isinstance(ymetric, dict):
            raise MQLParseError("Query #{query.id} data.metrics has non-dict: {t}"
                .format(query=self._query, t=type(ymetric)))
        qmetric1 = QMetric()
        def _parse_ymetric_item(yname, attr=None):
            self._parse_item(ymetric, yname, attr=attr, obj=qmetric1)
        _parse_ymetric_item('id')
        _parse_ymetric_item('metric', 'metric_id')
        _parse_ymetric_item('div', 'div_metric_id')
        _parse_ymetric_item('label')
        _parse_ymetric_item('goal')
        _parse_ymetric_item('goal_mode')
        _parse_ymetric_item('rag')
        _parse_ymetric_item('impact')
        return qmetric1

    def _parse_timeframe(self, yquery):
        """
        Helper - parse timeframe section in yquery.
        """
        ytimeframe = yquery.get('timeframe')
        if ytimeframe is None:
            raise MQLParseError("Query #{query.id} missing timeframe section"
                .format(query=self._query))
        if not isinstance(ytimeframe, dict):
            raise MQLParseError("Query #{query.id} timeframe not dict: {t}"
                .format(query=self._query, t=type(ytimeframe)))
        def _parse_ytimeframe_item(yname, attr=None):
            self._parse_item(ytimeframe, yname, attr=attr,
                obj=self._query.qtimeframe.tmfrspec)
        _parse_ytimeframe_item('id')
        _parse_ytimeframe_item('range_unit')
        _parse_ytimeframe_item('range_val')
        _parse_ytimeframe_item('gran_unit')
        _parse_ytimeframe_item('smooth_unit')
        _parse_ytimeframe_item('smooth_val')
        _parse_ytimeframe_item('mode')
        _parse_ytimeframe_item('accumulate')
        _parse_ytimeframe_item('allow_overflow_begin')
        _parse_ytimeframe_item('allow_overflow_end')
        if 'reframe_dt' in ytimeframe:
            rdt = ytimeframe['reframe_dt']
            if not isinstance(rdt, date):
                raise MQLParseError(
                    "Query #{query.id} timeframe reframe_dt not date: {t}"
                    .format(query=self._query, t=type(rdt)))
            if not isinstance(rdt, datetime):
                rdt = datetime(rdt.year, rdt.month, rdt.day)
            self._query.qtimeframe.tmfrspec.reframe_dt = rdt

    def _parse_format(self, yquery):
        """
        Helper - parse format section in yquery.
        """
        yformat = yquery.get('format')
        if yformat is None:
            return
        if not isinstance(yformat, dict):
            raise MQLParseError("Query #{query.id} format not dict: {t}"
                .format(query=self._query, t=type(yformat)))
        qformat1 = self._query.qformat
        for domain, yoptions in yformat.iteritems():
            if not isinstance(yoptions, dict):
                raise MQLParseError(
                    "Query #{query.id} format domain #{domain} not dict: {t}"
                    .format(query=self._query, domain=domain, t=type(yoptions)))
            dopts = qformat1.get_domain(domain)
            for k, v in yoptions.iteritems():
                dopts[k] = v

    def _parse_ghosts(self, yquery):
        """
        Helper - parse ghosts section in yquery.
        """
        yghosts = yquery.get('ghosts')
        if yghosts is None:
            return
        if not isinstance(yghosts, list):
            raise MQLParseError("Query #{query.id} ghosts not list: {t}"
                .format(query=self._query, t=type(yghosts)))
        qghosts1 = self._query.qghosts
        for yghost in yghosts:
            gtype = str(yghost)
            ghost1 = Ghost(gtype)
            qghosts1.add_ghost(ghost1)

    def __unicode__(self):
        return u"QueryParser({mdef})".format(mdef=self._query)


# ----------------------------------------------------------------------------


class QuerySetParser(AxObj):
    """
    Given raw MQL YAML strings, parse into QuerySet object.

    Usage: Create, parse, get, destroy (or reset).

    Variables prefixed with "y" reference parsed YAML currently existing as
    Python structures.
    Variables prefixed with "ystr_" reference raw YAML strings.


    Example partial YAML:

        ---
        queries:
          - id: query1_id
            data: ...
            timeframe: ...
          - id: query2_id
            data: ...
            timeframe: ...

    """

    def __init__(self):
        """
        Initialize parser and internal QuerySet.
        After parsing, either destroy or call reset to parse a new object.
        """
        self.reset()


    #
    # Public Methods
    #
    
    def reset(self):
        """
        Reset and prepare new QuerySet object for parsing.
        """
        self._queryset = QuerySet()

    def get_queryset(self):
        """
        Get the wrapped up QuerySet object after parsing.
        """
        return self._queryset

    def parse_ystr_queryset(self, ystr_queryset):
        """
        Given raw MQL YAML str, parse into internal QuerySet.
        Returns currently wrapped QuerySet.

        Raises MQLParseError on MQL parse errors.
        Raises yaml.YAMLError on underlying YAML parse errors.

        """
        yqueryset = yaml.load(ystr_queryset)
        return self.parse_yqueryset(yqueryset)

    def parse_yqueryset(self, yqueryset):
        """
        Given dict as parsed from YAML, parse into internal QuerySet.
        Returns currently wrapped QuerySet.

        Raises MQLParseError on MQL parse errors.
        """
        self._parse_queries(yqueryset)
        return self.get_queryset()


    #
    # Internal Methods
    #

    def _parse_queries(self, yqueryset):
        """
        Parse helper - parse 'queries' into self.queryset._queries dict
        keyed by query id.
        """
        yqueries = yqueryset.get('queries')
        if yqueries is None:
            raise MQLParseError("'queries' list not found")
        if not isinstance(yqueries, list):
            raise MQLParseError("'queries' list not a list: {t}"
                .format(t=type(yqueries)))
        for yquery in yqueries:
            queryparser = QueryParser()
            query1 = queryparser.parse_yquery(yquery)
            self._queryset.add_query(query1)

    def __unicode__(self):
        return u"QuerySetParser({set})".format(set=self._queryset)














