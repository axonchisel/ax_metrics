"""
Ax_Metrics - Query container and QuerySet collection

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


from axonchisel.metrics.foundation.ax.obj import AxObj

from .qdata import QData
from .qtimeframe import QTimeFrame
from .qformat import QFormat
from .qghosts import QGhosts


# ----------------------------------------------------------------------------


class Query(AxObj):
    """
    Representation of an MQL (Metrics Query Language) query.

    Query objects can be processed by MQEngine to obtain data.
    """

    def __init__(self,
        id = ''
    ):
        # Set valid default state:
        self.id          = ''
        self._qdata      = QData()
        self._qtimeframe = QTimeFrame()
        self._qformat    = QFormat()
        self._qghosts    = QGhosts()

        # Apply initial values from kwargs:
        self.id          = id


    #
    # Public Methods
    #

    def is_valid(self):
        """
        Check T/F if Query is valid.
        """
        try:
            self.validate()
            return True
        except (TypeError, ValueError) as e:
            return False

    def validate(self):
        """
        Validate self.
        Raise TypeError, ValueError if any problems.
        """
        if self.qdata.count_qmetrics() == 0:
            raise ValueError("Query #{self.id} qdata has no metrics".
                format(self=self))


    #
    # Public Properties
    #

    @property
    def qdata(self):
        """Wrapped QData."""
        return self._qdata
    @qdata.setter
    def qdata(self, val):
        self._assert_type("qdata", val, QData)
        self._qdata = val

    @property
    def qtimeframe(self):
        """Wrapped QTimeFrame."""
        return self._qtimeframe
    @qtimeframe.setter
    def qtimeframe(self, val):
        self._assert_type("qtimeframe", val, QTimeFrame)
        self._qtimeframe = val

    @property
    def qformat(self):
        """Wrapped QFormat."""
        return self._qformat
    @qformat.setter
    def qformat(self, val):
        self._assert_type("qformat", val, QFormat)
        self._qformat = val

    @property
    def qghosts(self):
        """Wrapped QGhosts."""
        return self._qghosts
    @qghosts.setter
    def qghosts(self, val):
        self._assert_type("qghosts", val, QGhosts)
        self._qghosts = val


    #
    # Internal Methods
    #

    def __unicode__(self):
        return (u"Query(#{self.id} " +
            "{self.qdata}, {self.qtimeframe}, "+
            "{self.qformat}, {self.qghosts})"
        ).format(self=self)


