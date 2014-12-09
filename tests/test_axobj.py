"""
Ax_Metrics - Test foundation AxObj

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import pytest
from datetime import datetime

from axonchisel.metrics.foundation.ax.obj import AxObj


# ----------------------------------------------------------------------------


class TestAxObj(object):
    """
    Test AxObj object.
    """

    #
    # Setup / Teardown
    #

    #
    # Tests
    #

    def test_str(self):
        axo = AxObj()
        str(axo)
        axo.id = 'MyId'
        str(axo)

    def test_init_kwargs(self):
        axo = AxObj()
        kwargs = {'foo': 123, 'bar': 'zig'}
        axo._init_kwargs(kwargs, ['foo', 'never'])
        assert hasattr(axo, 'foo')
        assert not hasattr(axo, 'bar')
        assert not hasattr(axo, 'never')
        assert axo.foo == 123

    def test_assert_misc(self):
        axo = AxObj()
        axo._assert_not_none('param', 12345)
        with pytest.raises(ValueError):
            axo._assert_not_none('param', None)
        axo._assert_value("param", 'foo', ['foo', 'bar', 'zig'])
        with pytest.raises(ValueError):
            axo._assert_value("param", 'NOWAY', ['foo', 'bar', 'zig'])

    def test_assert_types1(self):
        axo = AxObj()
        axo._assert_type("param", 12345, (int, long))
        with pytest.raises(TypeError):
            axo._assert_type("param", "Not int", (int, long))
        axo._assert_type_string("param", "String")
        with pytest.raises(TypeError):
            axo._assert_type_string("param", 12345)
        axo._assert_type_int("param", 12345)
        with pytest.raises(TypeError):
            axo._assert_type_int("param", "Not int")
        axo._assert_type_numeric("param", 12345)
        axo._assert_type_numeric("param", 12345L)
        axo._assert_type_numeric("param", 12345.678)
        with pytest.raises(TypeError):
            axo._assert_type_numeric("param", "Not numeric")
        axo._assert_type_datetime("param", datetime.now())
        with pytest.raises(TypeError):
            axo._assert_type_datetime("param", "Not datetime")
        axo._assert_type_bool("param", True)
        with pytest.raises(TypeError):
            axo._assert_type_bool("param", "Not bool")

    def test_assert_types_mapping(self):
        axo = AxObj()
        axo._assert_type_mapping("param", {})
        axo._assert_type_mapping("param", {'a':10})
        with pytest.raises(TypeError):
            axo._assert_type_mapping("param", "Not mapping")

    def test_assert_types_list(self):
        axo = AxObj()
        axo._assert_type_list("param", [])
        axo._assert_type_list("param", [10, 20])
        axo._assert_type_list_string("param", ["Foo", "Bar"])
        with pytest.raises(TypeError):
            axo._assert_type_list_string("param", ["Foo", 20])
        axo._assert_type_list_numeric("param", [10, 20.5])
        with pytest.raises(TypeError):
            axo._assert_type_list_numeric("param", [10, "B"])
        with pytest.raises(TypeError):
            axo._assert_type_list("param", 12345)
        axo._assert_type_list("param", [10, 20], length=2)
        with pytest.raises(ValueError):
            axo._assert_type_list("param", [10, 20], length=3)
        class A(object):
            pass
        class B(A):
            pass
        axo._assert_type_list("param", [A(), B()], ofsupercls=A)
        with pytest.raises(TypeError):
            axo._assert_type_list("param", [A(), 10], ofsupercls=A)


    #
    # Internal Helpers
    #


