"""
Ax_Metrics - Servant Internal State

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


from axonchisel.metrics.foundation.ax.obj import AxObj
from axonchisel.metrics.foundation.query.query import Query
from axonchisel.metrics.foundation.data.multi import MultiDataSeries
from axonchisel.metrics.io.erout.interface import EROut
from axonchisel.metrics.run.mqengine.mqengine import MQEngine

from .request import ServantRequest


# ----------------------------------------------------------------------------


class ServantState(AxObj):
    """
    Servant Internal State. Not for public use.
    """

    def __init__(self):
        # Set valid default state:
        self._request   = None    # (ServantRequest)
        self._erouts    = list()  # (list(EROut))
        self._mqengine  = None    # (MQEngine)


    #
    # Public Methods
    #


    #
    # Public Properties
    #

    @property
    def request(self):
        """ServantRequest being processed."""
        return self._request
    @request.setter
    def request(self, val):
        self._assert_type("request", val, ServantRequest)
        self._request = val

    @property
    def erouts(self):
        """EROut plugin objects to use."""
        return self._erouts
    @erouts.setter
    def erouts(self, val):
        self._assert_type_list("erouts", val, ofsupercls=EROut)
        self._erouts = val

    @property
    def mqengine(self):
        """MQEngine processing query."""
        return self._mqengine
    @mqengine.setter
    def mqengine(self, val):
        self._assert_type("mqengine", val, MQEngine)
        self._mqengine = val



    #
    # Internal Methods
    #

    def __unicode__(self):
        return (u"ServantState({self.request}, {self.erouts},"+
            "{self.mqengine})"
            ).format(self=self)




