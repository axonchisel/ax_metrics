"""
Ax_Metrics - AxObj foundation base class

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import collections
from datetime import datetime


# ----------------------------------------------------------------------------


class AxObj(object):
    """
    Base class for Ax_Metrics classes.

    Assertion Usage Note:
    Failures in the _assert_* methods typically include {self} within
    the raised exception messages.  If your __str__ / __unicode__ methods
    reference attributes on self, then you MUST define sane value for those
    attributes prior to invoking any assertions, or your assert exceptions
    will trigger their own confusing AttributeErrors when attempting to
    format the message!
    """

    #
    # Internal Methods: Init
    #

    def _init_kwargs(self, kwargs, kws):
        """
        Set all attributes (named in kws) on self with vals from kwargs.
        """
        for k in kws:
            if k in kwargs:
                setattr(self, k, kwargs[k])


    #
    # Internal Methods: Debug
    #

    def _get_debug_name(self):
        """Return object name suitable for error msg, stack trace, etc."""
        name = u"{cls}".format(cls=self.__class__.__name__)
        if hasattr(self, 'id'):
            name += u" #{id}".format(id=self.id)
        return name


    #
    # Internal Methods: Type/Value Checks
    #

    def _assert_not_none(self, name, val):
        """
        Raise ValueError if val is None.
        Not necessary if _assert_type is called, but useful on its own.
        """
        if val is None:
            raise ValueError((
                "{obj} {name} got unexpected None"
            ).format(obj=self._get_debug_name(),
                name=name)
            )

    def _assert_type(self, name, val, reqtype):
        """
        Raise TypeError if val is not reqtype type (or tuple of types).
        Values that are None will fail type assertion, so if you allow None,
        check for it before calling this.
        """
        if not isinstance(val, reqtype):
            raise TypeError((
                "{obj} {name} expected {reqtype}, got: {t}"
            ).format(obj=self._get_debug_name(),
                name=name, reqtype=reqtype, t=type(val))
            )

    def _assert_type_string(self, name, val):
        """
        Raise TypeError if val is not a string type.
        """
        self._assert_type(name, val, basestring)

    def _assert_type_int(self, name, val):
        """
        Raise TypeError if val is not a int (or long) numeric type.
        """
        self._assert_type(name, val, (int, long))

    def _assert_type_numeric(self, name, val):
        """
        Raise TypeError if val is not a numeric type.
        """
        self._assert_type(name, val, (int, long, float))

    def _assert_type_datetime(self, name, val):
        """
        Raise TypeError if val is not a datetime.
        """
        self._assert_type(name, val, datetime)

    def _assert_type_bool(self, name, val):
        """
        Raise TypeError if val is not a bool.
        """
        self._assert_type(name, val, bool)

    def _assert_type_mapping(self, name, val):
        """
        Raise TypeError if val is not a dict-like mapping type.
        """
        self._assert_type(name, val, collections.Mapping)

    def _assert_type_list(self, name, val, ofsupercls=None, length=None):
        """
        Raise TypeError if val is not an iterable type.
        Optionally enforce all members subclass ofsupercls too.
        Optionally enforce length.
        """
        self._assert_type(name, val, collections.Iterable)
        if ofsupercls is not None:
            name_item = "item in {name}".format(name=name)
            for x in val:
                self._assert_type(name_item, x, ofsupercls)
        if length is not None:
            if len(val) != length:
                raise ValueError((
                    "{obj} {name} length {lenval} != {lenexp}"
                ).format(obj=self._get_debug_name(),
                    name=name, lenval=len(val), lenexp=length)
                )

    def _assert_type_list_string(self, name, val, length=None):
        """
        Raise TypeError if val is not a list of strings.
        """
        self._assert_type_list(
            name, val, ofsupercls=basestring, length=length)

    def _assert_type_list_numeric(self, name, val, length=None):
        """
        Raise TypeError if val is not a list of numeric types.
        """
        self._assert_type_list(
            name, val, ofsupercls=(int, long, float), length=length)

    def _assert_value(self, name, val, allowed):
        """
        Raise ValueError if val is not in iterable allowed.
        """
        if val not in allowed:
            raise ValueError((
                "{obj} {name} not valid: {v}"
            ).format(obj=self._get_debug_name(),
                name=name, v=val)
            )


    #
    # Internal Methods: String Conversion
    #

    def __str__(self):
        """Return UTF-8 encoding of __unicode__."""
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        """Override this to provide more detailed display string."""
        return self._get_debug_name()


