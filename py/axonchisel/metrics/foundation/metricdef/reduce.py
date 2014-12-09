"""
Ax_Metrics - Metric Function Reduce Functions

Methods reduce a list of values (including None) to a single value.
Used internally.

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


class _ReduceFuncs(object):
    """
    Internal static wrapper for MetricDef FUNC reduce functions.
    Methods reduce a list of values (including None) to a single value.
    """

    @classmethod
    def reduce_COUNT(cls, vals):
        return len(vals)

    @classmethod
    def reduce_FIRST(cls, vals):
        try:
            return cls._strip_None(vals)[0]
        except IndexError:
            return None

    @classmethod
    def reduce_LAST(cls, vals):
        try:
            return cls._strip_None(vals)[-1]
        except IndexError:
            return None

    @classmethod
    def reduce_SUM(cls, vals):
        return sum(cls._strip_None(vals))

    @classmethod
    def reduce_MIN(cls, vals):
        return min(cls._strip_None(vals))

    @classmethod
    def reduce_MAX(cls, vals):
        return max(cls._strip_None(vals))

    @classmethod
    def reduce_AVG(cls, vals):
        vals = cls._strip_None(vals)
        try:
            return float(sum(vals)) / len(vals)
        except ZeroDivisionError:
            return None

    @classmethod
    def _strip_None(cls, vals):
        """Return list of values from vals that are not None."""
        return [v for v in vals if v is not None]


