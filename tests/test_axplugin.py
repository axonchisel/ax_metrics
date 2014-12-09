"""
Ax_Metrics - Test foundation AxPlugin

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import pytest

import axonchisel.metrics.foundation.ax.plugin as axplugin


# ----------------------------------------------------------------------------


class TestAxPlugin(object):
    """
    Test AxPlugin class.
    """

    #
    # Setup / Teardown
    #

    def setup_method(self, method):
        options = {'foo': 10, 'bar': {'a': 100, 'b': 200}}
        extinfo = {'zig': 10, 'zag': {'x': 100, 'y': 200}}
        self.p = axplugin.AxPluginBase(options=options, extinfo=extinfo)

    #
    # Tests
    #

    def test_str(self):
        str(self.p)

    def test_config_basic(self):
        assert self.p.options['foo'] == 10
        assert self.p.plugin_option('foo') == 10
        assert self.p.extinfo['zig'] == 10
        assert self.p.plugin_extinfo('zig') == 10

    def test_config_basic_defaults(self):
        with pytest.raises(KeyError):
            self.p.options['BOGUS']
        assert self.p.plugin_option('BOGUS', "DEF") == "DEF"
        with pytest.raises(KeyError):
            self.p.extinfo['BOGUS']
        assert self.p.plugin_extinfo('BOGUS', "DEF") == "DEF"

    def test_config_dotted(self):
        assert self.p.plugin_option('bar.a') == 100
        assert self.p.plugin_extinfo('zag.x') == 100

    def test_config_dotted_defaults(self):
        with pytest.raises(KeyError):
            self.p.plugin_option('bar.BOGUS')
        assert self.p.plugin_option('bar.BOGUS', "DEF") == "DEF"
        with pytest.raises(KeyError):
            self.p.plugin_extinfo('zag.BOGUS')
        assert self.p.plugin_extinfo('zag.BOGUS', "DEF") == "DEF"

    def test_format_str_basic(self):
        tests = [  # [(result, fmtstr)]
            ("simple literal", "simple literal"), 
            ("foo bar.a is 10 100", "foo bar.a is {options.foo} {options.bar.a}"), 
            ("zig zag.x is 10 100", "zig zag.x is {extinfo.zig} {extinfo.zag.x}"), 
            ("barb zagy is 200 200", "barb zagy is {options.bar.b} {extinfo.zag.y}"),
            ("Jimbo weighs 190", "{name} weighs {more.weight}"),
            ("Jimbo weighs 190", "{name} weighs {more[weight]}"),
        ]
        context = {
            'name': "Jimbo",
            'more': { 'weight': 190, 'height': 75 },
        }
        for exp, fmt in tests:
            v = self.p._format_str(fmt, context=context)
            assert v == exp

    def test_format_str_defaults(self):
        tests = [  # [(result, fmtstr, od_defaults)]
            ("Jimbo eats garbage.", "{name} eats {more.favoritefood}.", "garbage"),
        ]
        context = {
            'name': "Jimbo",
            'more': { 'weight': 190, 'height': 75 },
        }
        for exp, fmt, oddefs in tests:
            v = self.p._format_str(fmt, context=context, od_defaults=oddefs)
            assert v == exp

    def test_format_str_bad(self):
        tests = [  # [(exception, fmtstr)]
            (AttributeError, "{name} eats {more.favoritefood}."),
            (KeyError, "{name} eats {more[favoritefood]}."),
        ]
        context = {
            'name': "Jimbo",
            'more': { 'weight': 190, 'height': 75 },
        }
        for exc, fmt in tests:
            with pytest.raises(exc):
                self.p._format_str(fmt, context=context)



# ----------------------------------------------------------------------------


class TestAxPluginLoad(object):
    """
    Test AxPlugin loading.
    """

    #
    # Setup / Teardown
    #

    #
    # Tests
    #

    def test_good(self):
        # Note: We use "AxPluginLoadError" as a "plugin" class here for 
        # the sole reason that it is a known class that will be available 
        # to this code.  The fact that it is an "Exception" is irrelevant.
        cls = axplugin.AxPluginLoadError
        tests = [  # [(class expected, {load_plugin_class args})]
            (cls, { # (absolute class)
                'plugin_id':
                    'axonchisel.metrics.foundation.ax.plugin.AxPluginLoadError',
            }), 
            (cls, { # (simple default class)
                'plugin_id': 'AxPluginLoadError',
                'def_module_name': 'axonchisel.metrics.foundation.ax.plugin',
            }), 
            (cls, { # (prefixed default class)
                'plugin_id': 'LoadError',
                'def_module_name': 'axonchisel.metrics.foundation.ax.plugin',
                'def_cls_name_pfx': 'AxPlugin',
            }), 
            (cls, { # (require base class)
                'plugin_id': 'AxPluginLoadError',
                'def_module_name': 'axonchisel.metrics.foundation.ax.plugin',
                'require_base_cls': axplugin.AxPluginLoadError,
            }), 
        ]
        for (testcls, test) in tests:
            test['what'] = "Test Plugin"
            cls = axplugin.load_plugin_class(**test)
            assert cls == testcls

    def test_errors(self):
        tests = [  # [(str expected in exception, {load_plugin_class args})]
            ('must be absolute', { # (default without def_module_name)
                'plugin_id': 'PluginId',
            }), 
            ('import', { # (invalid default module)
                'plugin_id': 'PluginId',
                'def_module_name': 'axonchisel.metrics.BOGUS'
            }), 
            ('import', { # (invalid class in default module)
                'plugin_id': 'Bogus',
                'def_module_name': 'axonchisel.metrics.foundation.ax.plugin'
            }), 
            ('not subclass', { # (require base class)
                'plugin_id': 'AxPluginLoadError', # (see note in test_good)
                'def_module_name': 'axonchisel.metrics.foundation.ax.plugin',
                'require_base_cls': self.__class__, # (just another class)
            }), 
            ('absolute mode', { # (absolute not allowed)
                'allow_absolute': False,
                'plugin_id':
                    'axonchisel.metrics.foundation.ax.plugin.AxPluginLoadError',
            }), 
        ]
        for (errstr, test) in tests:
            test['what'] = "Test Plugin"
            with pytest.raises(axplugin.AxPluginLoadError) as e:
                cls = axplugin.load_plugin_class(**test)
            assert errstr in str(e)



    #
    # Internal Helpers
    #


