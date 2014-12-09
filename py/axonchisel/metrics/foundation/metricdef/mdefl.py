"""
Ax_Metrics - MDefL Metric Definition Language Parser

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import copy
import yaml
import collections

from axonchisel.metrics.foundation.ax.obj import AxObj
from axonchisel.metrics.foundation.ax.dictutil import dict_update_recursive

from .metricdef import MetricDef
from .filters import Filter
from .metset import MetSet


# ----------------------------------------------------------------------------


class MDefLParseError(Exception):
    """Error parsing MDefL"""
    pass    


# ----------------------------------------------------------------------------


class MetricDefParser(AxObj):
    """
    Given raw MDefL YAML strings, parse into MetricDef objects.

    Supports multiple parse passes on the same object, allowing defaults and
    extensions of defaults.

    Usage: Create, parse, parse, parse, ..., get, destroy (or reset).

    Variables prefixed with "y" reference parsed YAML currently existing as
    Python structures.
    Variables prefixed with "ystr_" reference raw YAML strings.


    Example partial YAML:

        ---
        id: num_new_sales
        type:          NUMBER
        func:          COUNT
        table:         first_sales
        time_field:    timeCreated

    """

    def __init__(self, base=None):
        """
        Initialize parser and internal MetricDef.
        If base MetricDef specified, copies as base to extend.
        After parsing, either destroy or call reset to parse a new object.
        """
        self.reset(base=base)


    #
    # Public Methods
    #
    
    def reset(self, base=None):
        """
        Reset and prepare new MetricDef object for parsing.
        If base MetricDef specified, copies as base to extend.
        """
        if base is not None:
            self._assert_type("base", base, MetricDef)
            base = copy.deepcopy(base)
        else:
            base = MetricDef()
        self._metricdef = base

    def get_metricdef(self):
        """
        Get the wrapped up MetricDef object after parsing.
        """
        return self._metricdef

    def parse_ystr_metric(self, ystr_metric):
        """
        Given raw MDefL YAML str, parse into internal MetricDef.
        Only set attributes that are specified, leaving others at default.
        Can be called multiple times to build up the MetricDef.
        Returns currently wrapped MetricDef.

        Raises MDefLParseError on MDefL parse errors.
        Raises yaml.YAMLError on underlying YAML parse errors.
        """
        ymetric = yaml.load(ystr_metric)
        return self.parse_ymetric(ymetric)

    def parse_ymetric(self, ymetric):
        """
        Given dict as parsed from YAML, parse into internal MetricDef.
        Only set attributes that are specified, leaving others at default.
        Can be called multiple times to build up the MetricDef.
        Returns currently wrapped MetricDef.

        Raises MDefLParseError on MDefL parse errors.
        """
        self._parse_item(ymetric, 'id')
        self._parse_item(ymetric, 'emfetch_id')
        self._parse_item(ymetric, 'emfetch_opts', extend=True)
        self._parse_item(ymetric, 'table')
        self._parse_item(ymetric, 'func')
        self._parse_item(ymetric, 'time_field')
        self._parse_item(ymetric, 'time_type')
        self._parse_item(ymetric, 'data_field')
        self._parse_item(ymetric, 'data_type')
        self._parse_filters(ymetric)
        return self.get_metricdef()


    #
    # Internal Methods
    #

    def _parse_item(self, yobj, yname, attr=None, obj=None, extend=False):
        """
        Set object attr to value of specific item in yobj, 
        but only if present.
        If attr unspecified, uses same name as yname.
        If obj unspecified, uses self._metricdef.
        If extend==True, extends dict instead of replacing it.
        """
        if obj is None:
            obj = self._metricdef
        if yname not in yobj:
            return
        if attr is None:
            attr = yname
        if extend:
            d = getattr(obj, attr, {})
            setattr(obj, attr, dict_update_recursive(d, yobj[yname]))
        else:
            setattr(obj, attr, yobj[yname])

    def _parse_filters(self, ymetric):
        """
        Helper - Parse filters in ymetric.
        """
        yfilters = ymetric.get('filters')
        if yfilters is None:
            return
        if not isinstance(yfilters, list):
            raise MDefLParseError(
                "MetricDef #{metricdef.id} filters list not a list: {t}"
                .format(metricdef=self._metricdef, t=type(yfilters)))
        for fnum in range(len(yfilters)):
            if self._metricdef.filters.count_filters() <= fnum:
                self._metricdef.filters.add_filter(Filter())
            f = self._metricdef.filters.get_filters()[fnum]
            self._parse_item(yfilters[fnum], 'field', obj=f)
            self._parse_item(yfilters[fnum], 'op',    obj=f)
            self._parse_item(yfilters[fnum], 'value', obj=f)

    def __unicode__(self):
        return u"MetricDefParser({mdef})".format(mdef=self._metricdef)


# ----------------------------------------------------------------------------


class MetSetParser(AxObj):
    """
    Given raw MDefL YAML strings, parse into MetSet object.

    Handles table_defaults.

    Usage: Create, parse, get, destroy (or reset).

    Variables prefixed with "y" reference parsed YAML currently existing as
    Python structures.
    Variables prefixed with "ystr_" reference raw YAML strings.

    Example partial YAML:

        ---
        table_defaults:
          - table: table1_name
            emfetch_id: ...
            time_field: ...
          - table: table2_name
            func: COUNT

        metrics:
          - id: metric1_id
            table: table1_name
            data_field: ...
            data_type: ..
          - id: metric2_id
            table: ...
          - id: metric3_id
            table: ...

    """

    def __init__(self):
        """
        Initialize parser and internal MetSet.
        After parsing, either destroy or call reset to parse a new object.
        """
        self.reset()


    #
    # Public Methods
    #
    
    def reset(self):
        """
        Reset and prepare new MetSet object for parsing.
        """
        self._metset = MetSet()
        self._table_defaults = dict()

    def get_metset(self):
        """
        Get the wrapped up MetSet object after parsing.
        """
        return self._metset

    def parse_ystr_metset(self, ystr_metset):
        """
        Given raw YAML str, parse into internal MetSet.
        Returns currently wrapped MetSet.
        """
        ymetset = yaml.load(ystr_metset)
        return self.parse_ymetset(ymetset)

    def parse_ymetset(self, ymetset):
        """
        Given dict as parsed from YAML, parse into internal MetSet.
        Returns currently wrapped MetSet.
        """
        self._parse_table_defaults(ymetset)
        self._parse_metricdefs(ymetset)
        return self.get_metset()


    #
    # Internal Methods
    #

    def _parse_table_defaults(self, ymetset):
        """
        Parse helper - parse 'table_defaults' into self._table_defaults dict
        keyed by table.
        """
        ytabledefs = ymetset.get('table_defaults')
        if ytabledefs is None:
            return
        if not isinstance(ytabledefs, list):
            raise MDefLParseError("'table_defaults' list not a list: {t}"
                .format(t=type(ytabledefs)))
        for ytbldef in ytabledefs:
            mdefparser = MetricDefParser()
            mdef = mdefparser.parse_ymetric(ytbldef)
            if not mdef.table:
                raise MDefLParseError("Table default missing table: {t}"
                    .format(t=ytbldef))
            self._table_defaults[mdef.table] = mdef

    def _parse_metricdefs(self, ymetset):
        """
        Parse helper - parse 'metrics' into self.metset._metrics dict
        keyed by metric id.
        """
        ymetrics = ymetset.get('metrics')
        if ymetrics is None:
            raise MDefLParseError("'metrics' list not found")
        if not isinstance(ymetrics, list):
            raise MDefLParseError("'metrics' list not a list: {t}"
                .format(t=type(ymetrics)))
        for ymetric in ymetrics:
            base = None
            table = ymetric.get('table')
            if table:
                tabledef = self._table_defaults.get(table)
                if tabledef:
                    base = tabledef
            mdefparser = MetricDefParser(base=base)
            mdef1 = mdefparser.parse_ymetric(ymetric)
            if not mdef1.id:
                raise MDefLParseError("Metric missing id: {ym}"
                    .format(ym=ymetric))
            self._metset.add_metric(mdef1)

    def __unicode__(self):
        return u"MetSetParser({set})".format(set=self._metset)














