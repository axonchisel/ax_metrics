"""
Ax_Metrics - Query component for data specification

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


from axonchisel.metrics.foundation.ax.obj import AxObj


# ----------------------------------------------------------------------------


# QMetric allowed goal modes
GOAL_MODES = {
    'CONSTANT': {},  # goal fixed throughout period 
    'FROMZERO': {},  # goal frows linearly from zero to goal at end of period
}

# QMetric allowed impacts
IMPACTS = {
    'POSITIVE': {},   # positive metric (e.g. revenue)
    'NEGATIVE': {},   # negative metric (e.g. cancellations)
}


# ----------------------------------------------------------------------------


class QData(AxObj):
    """
    Query component for data specification.
    Contains list of QMetrics to inspect.
    """
    def __init__(self):
        self._qmetrics   = list()


    #
    # Public Methods
    #
    
    def add_qmetric(self, qmetric1):
        """Add a QMetric to the list."""
        self._assert_type("qmetric", qmetric1, QMetric)
        self._qmetrics.append(qmetric1)

    def count_qmetrics(self):
        """Return number of QMetrics included."""
        return len(self._qmetrics)

    def iter_qmetrics(self):
        """Return an iterator over QMetrics."""
        return iter(self._qmetrics)

    def get_qmetric(self, idx):
        """
        Return specific 0-based indexed QMetric.
        Supports negative indexes from tail (-1 = last).
        Raise IndexError if out of range.
        """
        return self._qmetrics[idx]


    #
    # Internal Methods
    #

    def __unicode__(self):
        return (u"QData({qmetrics})"
        ).format(self=self, 
            qmetrics=u", ".join(map(unicode, self._qmetrics))
        )


# ----------------------------------------------------------------------------


class QMetric(AxObj):
    """
    Description of one metric the query should inspect.

    Attributes:

      - metric_id:
            Identifier of MetricDef (from MetSet) with primary data.
            The only required parameter.

      - div_metric_id:  (default = None)
            (Optional) Identifier of MetricDef (from MetSet) with
            secondary data to divide primary by, such as for percentage
            comparisons.

      - label:  (default = None)
            (Optional) Human-readable label for this metric.

      - goal:  (default = None)
            (Optional) Forecast or goal amount.

      - goal_mode:  (default = 'FROMZERO')
            (Optional) How to treat goal.  Specifically if the goal
            is fixed throughout the period or linearly grows from zero
            to goal at end of perod.
            Value from GOAL_MODES: 'CONSTANT', 'FROMZERO'.

      - rag:   (default = None)
            (Optional) List of 2 values representing cutoff points between
            red/amber and amber/green for use with RAG illustrations.
            For POSITIVE impact, the 2 values should be increasing.
            For NEGATIVE impact, the 2 values should be decreasing.

      - impact:  (default = 'POSITIVE')
            (Optional) Impact of high value of metric, positive or negative.
            Default POSITIVE for revenue, new customers, etc.
            Specify NEGATIVE for cancellations, expenses, defects, etc.
            Value from IMPACTS: 'POSITIVE', 'NEGATIVE'.

    """

    def __init__(self, **kwargs):
        """
        Initialize, optionally overriding any default properties with kwargs.
        """
        # Set default state:
        self.metric_id     = ''
        self.div_metric_id = None
        self.label         = ""
        self.goal          = None
        self.goal_mode     = 'FROMZERO'
        self.rag           = None       # [val, val]
        self.impact        = 'POSITIVE'


        # Apply initial values from kwargs:
        self._init_kwargs(kwargs, [
            'metric_id', 'div_metric_id', 'label', 'goal', 'goal_mode', 'rag',
        ])


    #
    # Public Methods
    #


    #
    # Public Properties
    #

    @property
    def metric_id(self):
        """Metric id."""
        return self._metric_id
    @metric_id.setter
    def metric_id(self, val):
        self._assert_type_string("metric_id", val)
        self._metric_id = val

    @property
    def div_metric_id(self):
        """Metric id to divide by (optional)."""
        return self._div_metric_id
    @div_metric_id.setter
    def div_metric_id(self, val):
        if val is not None:
            self._assert_type_string("div_metric_id", val)
        self._div_metric_id = val

    @property
    def label(self):
        """Human-readable label, passed through to output data series."""
        return self._label
    @label.setter
    def label(self, val):
        self._assert_type_string("label", val)
        self._label = val

    @property
    def goal(self):
        """Numeric goal, or None."""
        return self._goal
    @goal.setter
    def goal(self, val):
        if val is not None:
            self._assert_type_numeric("goal", val)
        self._goal = val

    @property
    def goal_mode(self):
        """Goal mode, from GOAL_MODES."""
        return self._goal_mode
    @goal_mode.setter
    def goal_mode(self, val):
        self._assert_type_string("goal_mode", val)
        self._assert_value("goal_mode", val, GOAL_MODES)
        self._goal_mode = val

    @property
    def rag(self):
        """Red/Amber/Green cutoff points (list of 2 numbers)."""
        return self._rag
    @rag.setter
    def rag(self, val):
        if val is not None:
            self._assert_type_list_numeric("rag", val, length=2)
        self._rag = val

    @property
    def impact(self):
        """Impact (positive or negative), from IMPACTS."""
        return self._impact
    @impact.setter
    def impact(self, val):
        self._assert_type_string("impact", val)
        self._assert_value("impact", val, IMPACTS)
        self._impact = val


    #
    # Internal Methods
    #

    def __unicode__(self):
        return (u"QMetric('{self.label}'"+
            " #{self.metric_id} div #{self.div_metric_id}, "+
            "goal {self.goal} {self.goal_mode} {self.impact} rag={self.rag})"
        ).format(self=self)


