"""
Ax_Metrics - Query component for ghost comparisons specification

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


from axonchisel.metrics.foundation.ax.obj import AxObj

from axonchisel.metrics.foundation.chrono.ghost import Ghost


# ----------------------------------------------------------------------------


class QGhosts(AxObj):
    """
    Query component for ghosts comparison specification.
    Contains list of Ghost references (relative time specs).
    """

    def __init__(self):
        self._ghosts   = list()


    #
    # Public Methods
    #
    
    def add_ghost(self, ghost):
        """Add a Ghost to the list."""
        if not isinstance(ghost, Ghost):
            raise TypeError("QData expected Ghost, got: {t}".
                format(t=type(ghost)))
        self._ghosts.append(ghost)

    def count_ghosts(self):
        """Return number of Ghosts included."""
        return len(self._ghosts)

    def get_ghosts(self):
        """Get (shallow copy of) list of Ghosts."""
        return list(self._ghosts)


    #
    # Internal Methods
    #

    def __getitem__(self, key):
        """Allow indexing like a list itself"""
        return self._ghosts[key]

    def __unicode__(self):
        return (u"QGhosts({ghosts})"
        ).format(self=self, 
            ghosts=u", ".join(map(unicode, self._ghosts))
        )



