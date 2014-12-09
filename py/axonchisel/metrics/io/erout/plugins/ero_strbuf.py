"""
Ax_Metrics - EROut plugin 'strbuf'

Mostly useful for testing and as a superclass for other plugins.

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from ..base import EROutBase


# ----------------------------------------------------------------------------



class EROut_strbuf(EROutBase):
    """
    EROut (Extensible Report Outputter) Plugin 'strbuf'.
    Accumulates output in an internal file-like string (byte) buffer.
    Mostly useful as superclass for other plugins.
    """

    #
    # Abstract Method Implementations
    #

    # abstract
    def plugin_create(self):
        """
        Invoked once to allow plugin to setup what it needs.
        """
        self.buf_reset()

    # abstract
    def plugin_destroy(self):
        """
        Invoked once to allow plugin to clean up after itself.
        """
        self.buf_reset()

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
        # Placeholder just adds str version of mdseries.
        # Subclasses should override and define this themselves.
        self.buf_add_line(str(mdseries))


    #
    # Public Buffer Methods
    #

    def buf_reset(self):
        """Reset internal buffer to empty, discarding contents."""
        self._buf = StringIO()

    def buf_get(self):
        """Return internal buffer contents as single string."""
        return self._buf.getvalue()

    def buf_get_lines(self):
        """
        Break internal buffer into list of lines, returning.
        """
        return self.buf_get().splitlines()

    def buf_add(self, text):
        self._assert_type_string("text", text)
        if isinstance(text, unicode):
            text = text.encode('utf-8')
        self._buf.write(text)

    def buf_add_line(self, line):
        """Add a single line to the internal buffer."""
        self._assert_type_string("line", line)
        self.buf_add("%s\n" % line)

    def buf_add_lines(self, lines):
        """Add a list of lines to the internal buffer."""
        for line in lines:
            self.buf_add_line(line)


# ----------------------------------------------------------------------------


