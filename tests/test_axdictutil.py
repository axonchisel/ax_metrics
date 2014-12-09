"""
Ax_Metrics - Test foundation Ax dictutil

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import pytest

from axonchisel.metrics.foundation.ax.dictutil import dict_get_by_path
from axonchisel.metrics.foundation.ax.dictutil import ObjectifiedDict


# ----------------------------------------------------------------------------


@pytest.fixture
def dicts():
    return [{
        'foo': "Big Foo",
        'bar': "Big Bar",
        'zig': [10, 20, 30],
        'zag': {
            'z1': 1000,
            'z2': {
                'a': 65,
                'b': 66,
            },
        },
    }]


# ----------------------------------------------------------------------------


class TestAxDictUtil(object):
    """
    Test dictutil module methods.
    """

    #
    # Setup / Teardown
    #

    #
    # Tests
    #

    def test_good(self, dicts):
        d = dicts[0]
        assert dict_get_by_path(d, 'foo') == "Big Foo"
        assert dict_get_by_path(d, 'zig') == [10, 20, 30]
        assert dict_get_by_path(d, 'zag.z1') == 1000
        assert dict_get_by_path(d, 'zag.z2.a') == 65

    def test_default(self, dicts):
        d = dicts[0]
        assert dict_get_by_path(d, 'foo', "DEF") == "Big Foo"
        assert dict_get_by_path(d, 'BOGUS', "DEF") == "DEF"

    def test_bad(self, dicts):
        d = dicts[0]
        with pytest.raises(KeyError):
            dict_get_by_path(d, 'BOGUS')
        with pytest.raises(KeyError):
            dict_get_by_path(d, 'foo.BOGUS')
        with pytest.raises(KeyError):
            dict_get_by_path(d, 'zag.z1.BOGUS')
        with pytest.raises(KeyError):
            dict_get_by_path(d, 'zag.z2.BOGUS')

    def test_what(self, dicts):
        d = dicts[0]
        with pytest.raises(KeyError) as e:
            dict_get_by_path(d, 'BOGUS', what="Test Dict")
        assert "'Test Dict'" in str(e)


    #
    # Internal Helpers
    #


# ----------------------------------------------------------------------------


class TestAxObjectifiedDict(object):
    """
    Test Ax ObjectifiedDict.
    """

    #
    # Setup / Teardown
    #

    #
    # Tests
    #

    def test_good(self, dicts):
        d = dicts[0]
        od = ObjectifiedDict(d)
        assert od.foo == "Big Foo"
        assert od.zig == [10, 20, 30]
        assert od.zag.z1 == 1000
        assert od.zag.z2.a == 65

    def test_as_dict(self, dicts):
        d = dicts[0]
        od = ObjectifiedDict(d)
        od['foo'] = "Bigger Foo"
        assert od.foo == "Bigger Foo"
        assert 'foo' in od.keys()
        assert 'zig' in od.keys()
        assert od.has_key('zag')
        del od['foo']
        with pytest.raises(AttributeError):
            od.foo

    def test_default(self, dicts):
        d = dicts[0]
        od = ObjectifiedDict(d, default="DEF")
        assert od.foo == "Big Foo"
        assert od.BOGUS == "DEF"
        assert od.zag.BOGUS == "DEF"

    def test_copy(self, dicts):
        d = dicts[0]
        od = ObjectifiedDict(d)
        od2 = od.copy()
        assert od2.foo == "Big Foo"
        od['foo'] = "Another Foo"
        assert od2.foo == "Big Foo"

    def test_bad_key(self, dicts):
        d = dicts[0]
        od = ObjectifiedDict(d)
        with pytest.raises(AttributeError):
            od.BOGUS
        with pytest.raises(AttributeError):
            od.foo.BOGUS
        with pytest.raises(AttributeError):
            od.zag.z1.BOGUS
        with pytest.raises(AttributeError):
            od.zag.z2.BOGUS

    def test_bad_misc(self, dicts):
        d = dicts[0]
        with pytest.raises(TypeError):
            od = ObjectifiedDict("Not a Dict")

    def test_what(self, dicts):
        d = dicts[0]
        od = ObjectifiedDict(d, what="Test Dict")
        with pytest.raises(AttributeError) as e:
            od.zag.z2.BOGUS
        assert "'Test Dict'" in str(e)


    #
    # Internal Helpers
    #

