"""
Ax_Metrics - MetSet Metric Set (MetricDef collection)

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


from axonchisel.metrics.foundation.ax.obj import AxObj

from .metricdef import MetricDef


# ----------------------------------------------------------------------------


class MetSet(AxObj):
    """
    MetSet Metric Set (MetricDef collection).
    """
    def __init__(self):
        self._metrics        = dict()  # MetricDefs keyed by their id


    #
    # Public Methods
    #
    
    def add_metric(self, mdef):
        """
        Add MetricDef to collection, replacing any with same id.
        """
        if not isinstance(mdef, MetricDef):
            raise TypeError("{set} can't add non MetricDef: {t}"
                .format(set=self, t=type(mdef)))
        self._metrics[mdef.id] = mdef

    def count_metrics(self):
        """
        Returns total number of metrics in set.
        """
        return len(self._metrics)

    def get_metric_by_id(self, id):
        """
        Returns specified MetricDef, or raise KeyError if not found.
        """
        mdef = self._metrics.get(id)
        if not mdef:
            raise KeyError("Metric #{id} not in {set}".format(id=id, set=self))
        return mdef

    def validate(self):
        """
        Validate self and all contained MetricDefs.
        Raise TypeError, ValueError if any problems.
        """
        for (id, mdef) in self._metrics.iteritems():
            mdef.validate()


    #
    # Internal Methods
    #

    def __unicode__(self):
        return (u"MetSet({len} MetricDefs)"
            .format(len=len(self._metrics)))



