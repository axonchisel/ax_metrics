"""
Ax_Metrics - TimeRange extension with time_t support, for plugin internal use.

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import time
import re

import axonchisel.metrics.foundation.chrono.timerange as timerange


# ----------------------------------------------------------------------------


class TimeRange_time_t(timerange.TimeRange):
    """
    Extend TimeRange to provide 4 new properties named with _time_t appended.
    Each contains time_t (in int seconds) version of equivalent properties.
    Provide patch_format_str support method.
    May be used internally by EMFetch plugins for string formatting.
    This object is intended as a read-only decorator and not for updating.
    New time_t properties are lazily initialized to avoid unnecessary
    performance penalties when time_t variants are not referenced.
    """

    def __init__(self, tmrange):
        """Init based on a TimeRange."""
        timerange.TimeRange.__init__(self, 
            anchor=tmrange.anchor,
            inc_begin=tmrange.inc_begin,
            exc_end=tmrange.exc_end,
        )


    #
    # Public Properties
    #

    @property
    def inc_begin_time_t(self):
        if not hasattr(self, '_inc_begin_time_t'):
            self._inc_begin_time_t = int(self._dt_to_time_t(self.inc_begin))
        return self._inc_begin_time_t

    @property
    def exc_begin_time_t(self):
        if not hasattr(self, '_exc_begin_time_t'):
            self._exc_begin_time_t = int(self._dt_to_time_t(self.exc_begin))
        return self._exc_begin_time_t

    @property
    def inc_end_time_t(self):
        if not hasattr(self, '_inc_end_time_t'):
            self._inc_end_time_t = int(self._dt_to_time_t(self.inc_end))
        return self._inc_end_time_t

    @property
    def exc_end_time_t(self):
        if not hasattr(self, '_exc_end_time_t'):
            self._exc_end_time_t = int(self._dt_to_time_t(self.exc_end))
        return self._exc_end_time_t

    #
    # Public Static Helpers
    #

    @staticmethod
    def patch_format_str(fmt, varnames):
        """
        Given a str.format format str, patch :%s types for _time_t use.
        
        The datetime:%s format is intended to request time_t but is not
        supported natively in Python, and inconsistently on various 
        platforms.

        For all 'varname' in varnames list, this method finds references in
        the format str like:
            '{varname.bar:%s}'
        and replaces them with the valid:
            '{varname.bar_time_t}'

        It is intended for use with TimeRange_time_t objects.
        """
        for varname in varnames:
            pattern = r'\{' + varname + r'\.(\w+):%s\}'
            sub = r'{' + varname + '.\\1_time_t}'
            fmt = re.sub(pattern, sub, fmt)
        return fmt
    

    #
    # Internal Methods
    #
    
    def _dt_to_time_t(self, dt):
        """Helper: convert datetime to int time_t"""
        return int(time.mktime(dt.timetuple()))





