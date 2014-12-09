"""
Ax_Metrics - EROut (Extensible Report Outputter) Plugin Interface

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


from axonchisel.metrics.foundation.ax.plugin import AxPlugin


# ----------------------------------------------------------------------------


class EROut(AxPlugin):
    """
    EROut (Extensible Report Outputter) Plugin Interface.

    EROut plugins are used (e.g. by Servant) to process MultiDataSeries
    into final or intermediary report formats, for humans or machines.

    Implementations provide various format outputs by overriding the
    plugin_output() abstract method.

    See AxPlugin and AxPluginBase for architecture details.

    Additional Parameters:

      - query : Query originally used to create the data, with QFormat, etc.
                Optional. Plugins should work without access to Query.
                (axonchisel.metrics.foundation.query.query.Query)
    """

    #
    # Abstract Methods
    #

    # abstract
    def __init__(self, extinfo=None):
        """
        Initialize around optional extinfo dict.
        """
        raise NotImplementedError("EROut abstract superclass")

    # abstract
    def plugin_output(self, mdseries, query=None):
        """
        EROut plugins must implement this abstract method.
        Invoked to output MultiDataSeries as specified.
        
        Returns nothing. Output target should be configured separately.

        Parameters:

          - mdseries : MultiDataSeries query result with data to output.
                    (axonchisel.metrics.foundation.data.multi.MultiDataSeries)

          - query : optional Query source with more formatting details, etc.
                    Optional. Plugins should work without access to Query.
                    (axonchisel.metrics.foundation.query.query.Query)

        """
        raise NotImplementedError("EROut abstract superclass")




