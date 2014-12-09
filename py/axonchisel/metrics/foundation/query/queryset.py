"""
Ax_Metrics - QuerySet Query Set (Query collection)

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


from axonchisel.metrics.foundation.ax.obj import AxObj

from .query import Query


# ----------------------------------------------------------------------------


class QuerySet(AxObj):
    """
    QuerySet Query Set (QueryDef collection).
    """

    def __init__(self):
        self._queries        = dict()  # Queries keyed by their id


    #
    # Public Methods
    #
    
    def add_query(self, query1):
        """
        Add valid Query to collection, replacing any with same id.
        """
        self._assert_type("query", query1, Query)
        query1.validate()
        self._queries[query1.id] = query1

    def count_queries(self):
        """
        Returns total number of queries in set.
        """
        return len(self._queries)

    def get_query_by_id(self, id):
        """
        Returns specified Query, or raise KeyError if not found.
        """
        m = self._queries.get(id)
        if not m:
            raise KeyError("Query #{id} not in {set}".format(id=id, set=self))
        return m

    def validate(self):
        """
        Validate self and all contained Querys.
        Raise TypeError, ValueError if any problems.
        """
        for (id, q) in self._queries.iteritems():
            q.validate()


    #
    # Internal Methods
    #

    def __unicode__(self):
        return (u"QuerySet({len} Queries)"
            .format(len=len(self._queries)))




