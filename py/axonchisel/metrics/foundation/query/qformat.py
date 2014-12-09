"""
Ax_Metrics - Query component for format specification

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


from axonchisel.metrics.foundation.ax.obj import AxObj


# ----------------------------------------------------------------------------


# Special domain for common property defaults.
DOMAIN_DEFAULT = '_default'


# ----------------------------------------------------------------------------


class QFormat(AxObj):
    """
    Mostly opaque format container, mostly for use by ERout output plugins.
    
    Contains "domain" options dicts, each domain identified by a short ID
    (often the name of the plugin).
    """
    def __init__(self):
        self._domain_options = dict()


    #
    # Public Methods
    #

    def has_domain(self, domain):
        """Return T/F indicating if options are set or indicated domain id."""
        return domain in self._domain_options

    def get_domain(self, domain):
        """
        Get options dict for specified domain id, creating if new.
        Note that this dict does not take the common default properties into
        consideration at all.  Use get() for that.
        """
        if domain not in self._domain_options:
            self._domain_options[domain] = dict()
        return self._domain_options[domain]

    def get(self, domain, key, default=KeyError):
        """
        Get value of key in specified domain id or common default, else default.
        Unlike get_domain(), if domain does not exist, it is NOT created.
        If the key is not present, the special '_default' domain is checked.
        Finally if still not found, default is returned, or if not specified,
        KeyError is raised.
        """
        found = False
        if domain in self._domain_options:
            if key in self._domain_options[domain]:
                return self._domain_options[domain][key]
        if DOMAIN_DEFAULT in self._domain_options:
            if key in self._domain_options[DOMAIN_DEFAULT]:
                return self._domain_options[DOMAIN_DEFAULT][key]
        if default is KeyError:
            raise KeyError((
                u"'{key}' within domain '{domain}' not found in {self}"
                ).format(self=self, key=key, domain=domain))
        else:
            return default
    

    #
    # Internal Methods
    #

    def __unicode__(self):
        return (u"QFormat({options})"
            ).format(self=self, options=self._domain_options)


