"""
Ax_Metrics - Metric Definition and MetSet collection

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


from axonchisel.metrics.foundation.ax.obj import AxObj

from .filters import Filters, Filter
from .reduce import _ReduceFuncs


# ----------------------------------------------------------------------------


# MetricDef allowed data field types
DATA_TYPES = {
    'NUM_INT': {},
    'NUM_FLOAT': {},
    'MONEY_FLOAT': {},
    'MONEY_INT100': {},
    'MONEY_FLOAT100': {},
}

# MetricDef allowed time field types
TIME_TYPES = {
    'TIME_EPOCH_SECS': {},
    'TIME_EPOCH_MILLIS': {},
    'TIME_DATE': {},
    'TIME_DATETIME': {},
}

# MetricDef allowed functions
FUNCS = {
    'COUNT': { 'reduce': _ReduceFuncs.reduce_COUNT, },
    'FIRST': { 'reduce': _ReduceFuncs.reduce_FIRST, },
    'LAST':  { 'reduce': _ReduceFuncs.reduce_LAST,  },
    'SUM':   { 'reduce': _ReduceFuncs.reduce_SUM,   },
    'MIN':   { 'reduce': _ReduceFuncs.reduce_MIN,   },
    'MAX':   { 'reduce': _ReduceFuncs.reduce_MAX,   },
    'AVG':   { 'reduce': _ReduceFuncs.reduce_AVG,   },
}


# ----------------------------------------------------------------------------


class MetricDef(AxObj):
    """
    Definition of a single metric and how to obtain it.
    This is a core conceptual object underlying the entire metrics system.

    A metric as defined here MUST be capable of producing a result 
    for any historical time range.
    Past data SHOULD be consistent between queries, but is not required.
    """
    def __init__(self, **kwargs):
        """
        Initialize, optionally overriding any default properties with kwargs.
        """
        # Set valid default state:
        self.id           = ''
        self.emfetch_id   = ''
        self.emfetch_opts = dict()
        self.table        = ''           # table name, etc.
        self.func         = 'COUNT'      # from FUNCS
        self.time_field   = ''
        self.time_type    = 'TIME_EPOCH_SECS'  # from TIME_TYPES
        self.data_field   = ''
        self.data_type    = 'NUM_INT'          # from DATA_TYPES
        self.filters      = Filters()

        # Apply initial values from kwargs:
        self._init_kwargs(kwargs, [
            'id',
            'emfetch_id', 'emfetch_opts',
            'table', 'func', 'time_field', 'time_type',
            'data_field', 'data_type',
            'filters',
        ])


    #
    # Public Methods
    #
    
    def is_valid(self):
        """
        Check T/F if MetricDef is valid.
        """
        try:
            self.validate()
            return True
        except (TypeError, ValueError) as e:
            return False

    def validate(self):
        """
        Validate self to ensure complete valid MetricDef.
        Raise TypeError, ValueError if any problems.
        While much validation happens already via property accessors,
        this method does final validation on additional status.
        """
        self._validate_required()
        self.filters.validate()


    #
    # Public Properties
    #

    @property
    def id(self):
        """Id of the MetricDef itself."""
        return self._id
    @id.setter
    def id(self, val):
        self._assert_type_string("id", val)
        self._id = val

    @property
    def emfetch_id(self):
        """Id of the EMFetch plugin used to access the metric."""
        return self._emfetch_id
    @emfetch_id.setter
    def emfetch_id(self, val):
        self._assert_type_string("emfetch_id", val)
        self._emfetch_id = val

    @property
    def emfetch_opts(self):
        """Options dict for the EMFetch plugin."""
        return self._emfetch_opts
    @emfetch_opts.setter
    def emfetch_opts(self, val):
        self._assert_type("emfetch_opts", val, dict)
        self._emfetch_opts = val

    @property
    def table(self):
        """Name of table containing data."""
        return self._table
    @table.setter
    def table(self, val):
        self._assert_type_string("table", val)
        self._table = val

    @property
    def func(self):
        """Name of function to apply to data, from FUNCS."""
        return self._func
    @func.setter
    def func(self, val):
        self._assert_type_string("func", val)
        self._assert_value("func", val, FUNCS)
        self._func = val

    @property
    def time_field(self):
        """Field name in table containing indexed time data."""
        return self._time_field
    @time_field.setter
    def time_field(self, val):
        self._assert_type_string("time_field", val)
        self._time_field = val

    @property
    def time_type(self):
        """Data type of time_field, from TIME_TYPES."""
        return self._time_type
    @time_type.setter
    def time_type(self, val):
        self._assert_type_string("time_type", val)
        self._assert_value("time_type", val, TIME_TYPES)
        self._time_type = val

    @property
    def data_field(self):
        """Field name in table containing data."""
        return self._data_field
    @data_field.setter
    def data_field(self, val):
        self._assert_type_string("data_field", val)
        self._data_field = val

    @property
    def data_type(self):
        """Data type of data_field, from DATA_TYPES."""
        return self._data_type
    @data_type.setter
    def data_type(self, val):
        self._assert_type_string("data_type", val)
        self._assert_value("data_type", val, DATA_TYPES)
        self._data_type = val

    @property
    def filters(self):
        """List of Filters."""
        return self._filters
    @filters.setter
    def filters(self, val):
        self._assert_type("filters", val, Filters)
        self._filters = val


    #
    # Internal Methods
    #

    def _validate_required(self):
        """Raises ValueError if any required fields not specified."""
        required_attrs = [
            'id', 'emfetch_id', 'table', 'func',
            'time_field', 'time_type', 
        ]
        for a in required_attrs:
            val = getattr(self, a)
            if (val is None) or (val == ''):
                raise ValueError("Missing {k} in #{id}"
                    .format(k=a, id=self.id))

    def __unicode__(self):
        return u"MetricDef('{self.id}')".format(self=self)


