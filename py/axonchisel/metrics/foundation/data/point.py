"""
Ax_Metrics - Encapsulation of a single data point with time range and value

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


from axonchisel.metrics.foundation.ax.obj import AxObj

from axonchisel.metrics.foundation.chrono.timerange import TimeRange


# ----------------------------------------------------------------------------


class DataPoint(AxObj):
    """
    Single 2D data point with a) time range and b) value.

    Value of None is allowed to indicate missing data.

    Many DataPoints may be represented by a DataSeries.
    """

    def __init__(self, **kwargs):
        """
        Initialize, optionally overriding any default properties with kwargs.
        """
        # Set default state:
        self._tmrange = None
        self._value   = None

        # Apply initial values from kwargs:
        self._init_kwargs(kwargs, [
            'tmrange', 'value',
        ])


    #
    # Public Methods
    #
    
    def is_valid(self):
        """
        Check T/F if DataPoint is valid.
        """
        try:
            self.validate()
            return True
        except (TypeError, ValueError) as e:
            return False

    def validate(self):
        """
        Validate self to ensure valid TimeRange.
        Raise TypeError, ValueError if any problems.
        While much validation happens already via property accessors,
        this method does final validation on additional status.
        DataPoint missing data (i.e. value=None) can still be valid.
        """
        self._assert_type("tmrange", self.tmrange, TimeRange)
        self.tmrange.validate()

    def is_missing(self):
        """
        Check T/F if DataPoint is missing value (i.e. None).
        Note: this is separate from the validity of the DataPoint itself.
        """
        return self._value is None


    #
    # Public Properties
    #

    @property
    def tmrange(self):
        """Wrapped TimeRange."""
        return self._tmrange
    @tmrange.setter
    def tmrange(self, val):
        self._assert_type("tmrange", val, TimeRange)
        self._tmrange = val

    @property
    def value(self):
        """Wrapped numeric value, or None for missing data."""
        return self._value
    @value.setter
    def value(self, val):
        if val is not None:
            self._assert_type_numeric("tmrange", val)
        self._value = val


    #
    # Internal Methods
    #

    def __unicode__(self):
        return (u"{cls}('{self.value} at {self.tmrange}')"
            ).format(self=self, cls=self.__class__.__name__)


# ----------------------------------------------------------------------------


