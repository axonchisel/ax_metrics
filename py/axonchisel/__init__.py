"""
Python trickery to support multiple separate repos/directories
sharing this same package namespace (axonchisel.*).

Explanation: http://www.doughellmann.com/PyMOTW/pkgutil/
"""

import pkgutil

__path__ = pkgutil.extend_path(__path__, __name__)
