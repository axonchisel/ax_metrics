"""
Ax_Metrics - Default EROut plugin class aggregation

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------

#
# Default Plugins
#

from .ero_strbuf            import EROut_strbuf
from .ero_csv               import EROut_csv

from .ero_geckoboard        import EROut_geckoboard_bullet
from .ero_geckoboard        import EROut_geckoboard_meter
from .ero_geckoboard        import EROut_geckoboard_numsec_comp
from .ero_geckoboard        import EROut_geckoboard_numsec_trend
from .ero_geckoboard        import EROut_geckoboard_rag
from .ero_geckoboard        import EROut_geckoboard_text

