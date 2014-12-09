"""
Ax_Metrics - MetricDef Filter specification

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


from collections import defaultdict

from axonchisel.metrics.foundation.ax.obj import AxObj


# ----------------------------------------------------------------------------


# Filter allowed operations
FILTER_OPS = {
    'EQ': {},
}


# ----------------------------------------------------------------------------


class Filters(AxObj):
    """
    Part of a MetricDef, contains list of Filters.
    """
    def __init__(self):
        self._filters   = list()


    #
    # Public Methods
    #
    
    def add_filter(self, filter1):
        """Add a Filter to the list."""
        self._assert_type("filter", filter1, Filter)
        self._filters.append(filter1)

    def count_filters(self):
        """Return number of Filters included."""
        return len(self._filters)

    def get_filters(self):
        """Get (shallow copy of) list of filters."""
        return list(self._filters)

    def remove_filter(self, filter1):
        """Remove first matching filter, or ValueError if no matches."""
        self._filters.remove(filter1)

    def validate(self):
        """
        Validate all contained Filters.
        Raise TypeError, ValueError if any problems.
        """
        for f in self._filters:
            f.validate()


    #
    # Public Properties
    #

    @property
    def safe_indexable(self):
        """
        Return indexable (by 0-based index) dict of filters,
        but with default Filters returned for indexes out of range.
        (Useful for dynamic string formatting in higher layers.)
        """
        d = defaultdict(Filter)
        d.update(enumerate(self._filters))
        return d


    #
    # Internal Methods
    #

    def __getitem__(self, key):
        """Allow indexing like a list itself"""
        return self._filters[key]

    def __unicode__(self):
        return (u"Filters({filters})"
        ).format(self=self, 
            filters=u", ".join(map(unicode, self._filters))
        )


# ----------------------------------------------------------------------------


class Filter(AxObj):
    """
    Field filter representation.
    """

    def __init__(self, **kwargs):
        """
        Initialize, optionally overriding any default properties with kwargs.
        """
        # Set valid default state:
        self.field    = ''
        self.op       = 'EQ'     # from FILTER_OPS
        self.value    = ''

        # Apply initial values from kwargs:
        self._init_kwargs(kwargs, [
            'field', 'op', 'value',
        ])


    #
    # Public Methods
    #

    def validate(self):
        """
        Validate params in self against allowed values.
        Raise TypeError, ValueError if any problems.
        While much validation happens already via property accessors,
        this method does final validation on additional status.
        """
        if not self.field:
            raise ValueError("Missing Filter field")


    #
    # Public Properties
    #

    @property
    def field(self):
        """Field to filter on."""
        return self._field
    @field.setter
    def field(self, val):
        self._assert_type_string("field", val)
        self._field = val

    @property
    def op(self):
        """Operator for filter comparison."""
        return self._op
    @op.setter
    def op(self, val):
        self._assert_type_string("op", val)
        self._assert_value("op", val, FILTER_OPS)
        self._op = val

    @property
    def value(self):
        """Filter value."""
        return self._value
    @value.setter
    def value(self, val):
        self._value = val


    #
    # Internal Methods
    #

    def __cmp__(self, other):
        """Compare filters, mainly for equality."""
        if self.field != other.field:
            return cmp(self.field, other.field)
        if self.op != other.op:
            return cmp(self.op, other.op)
        if self.value != other.value:
            return cmp(self.value, other.value)
        return 0

    def __unicode__(self):
        return (u"Filter({self.field} {self.op} '{self.value}')"
            .format(self=self)
        )



