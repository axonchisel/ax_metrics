"""
Ax_Metrics - Servant Config (construction config)

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


from axonchisel.metrics.foundation.ax.obj import AxObj
from axonchisel.metrics.foundation.metricdef.metset import MetSet
from axonchisel.metrics.foundation.query.queryset import QuerySet


# ----------------------------------------------------------------------------


# Special extinfo domain for common property defaults.
EXTINFO_DOMAIN_DEFAULT = '_default'


# ----------------------------------------------------------------------------


class ServantConfig(AxObj):
    """
    Construction configuration for Servant.
    See property docs for details.
    """

    def __init__(self, **kwargs):
        """
        Initialize, optionally overriding any default properties with kwargs.
        """
        # Set valid default state:
        self._metset          = None  # (MetSet)
        self._queryset        = None  # (QuerySet)
        self._emfetch_extinfo = None  # (dict)
        self._erout_extinfo   = None  # (dict)

        # Apply initial values from kwargs:
        self._init_kwargs(kwargs, [
            'metset', 'queryset',
            'emfetch_extinfo', 'erout_extinfo',
        ])


    #
    # Public Methods
    #

    def validate(self):
        """
        Validate params in self against allowed values.
        Raise TypeError, ValueError if any problems.
        While much validation happens already via property accessors,
        this method does final validation on additional status and
        ensures default None properties have values.
        """
        if self._metset is None:
            raise ValueError("ServantConfig invalid: missing MetSet")
        if self._queryset is None:
            raise ValueError("ServantConfig invalid: missing QuerySet")
        if self._emfetch_extinfo is None:
            raise ValueError("ServantConfig invalid: missing emfetch_extinfo")
        if self._erout_extinfo is None:
            raise ValueError("ServantConfig invalid: missing erout_extinfo")

    def erout_extinfo_for(self, plugin_id):
        """
        Construct and return dict with EROut extinfo for given plugin_id.
        Uses _default dict (if any), extended with plugin_id dict.
        """
        extinfo = dict(self.erout_extinfo.get(EXTINFO_DOMAIN_DEFAULT, {}))
        extinfo.update(self.erout_extinfo.get(plugin_id, {}))
        return extinfo


    #
    # Public Properties
    #

    @property
    def metset(self):
        """MetSet containing all metric definitions."""
        return self._metset
    @metset.setter
    def metset(self, val):
        self._assert_type("metset", val, MetSet)
        self._metset = val

    @property
    def queryset(self):
        """QuerySet containing all query definitions."""
        return self._queryset
    @queryset.setter
    def queryset(self, val):
        self._assert_type("queryset", val, QuerySet)
        self._queryset = val

    @property
    def emfetch_extinfo(self):
        """
        Additional custom (site-specific, sensitive) info for EMFetchers.
        This must be a dict mapping from EMFetch Id (string) to extinfo dict.
        Key '_default' dict (if present) acts as base, extended by 
        plugin-specific dicts.
        """
        return self._emfetch_extinfo
    @emfetch_extinfo.setter
    def emfetch_extinfo(self, val):
        self._assert_type_mapping("emfetch_extinfo", val)
        self._emfetch_extinfo = val

    @property
    def erout_extinfo(self):
        """
        Additional custom (site-specific, sensitive) info for EROuts.
        This must be a dict mapping from EROut Id (string) to extinfo dict.
        Key '_default' dict (if present) acts as base, extended by 
        plugin-specific dicts.
        See macro method: self.erout_extinfo_for()
        """
        return self._erout_extinfo
    @erout_extinfo.setter
    def erout_extinfo(self, val):
        self._assert_type_mapping("erout_extinfo", val)
        self._erout_extinfo = val


    #
    # Internal Methods
    #

    def __unicode__(self):
        # Note: do not reveal extinfo which may contain sensistive data.
        return (u"ServantConfig({self.metset}, {self.queryset})"
            .format(self=self))




