"""
Ax_Metrics - AxPlugin dynamic class support

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import collections

from axonchisel.metrics.foundation.ax.obj import AxObj

from . import dictutil


# ----------------------------------------------------------------------------
# EXCEPTIONS


class AxPluginLoadError(Exception):
    """
    Raised on errors during loading of plugins.
    """
    pass


class AxPluginLoadError_Mode(AxPluginLoadError):
    """
    Raised on errors during loading of plugins when bad mode triggered.
    """
    pass

class AxPluginLoadError_Module(AxPluginLoadError):
    """
    Raised on errors during loading of plugins when importing module.
    """
    pass

class AxPluginLoadError_Class(AxPluginLoadError):
    """
    Raised on errors during loading of plugins when importing class.
    """
    pass

class AxPluginLoadError_Type(AxPluginLoadError):
    """
    Raised on errors during loading of plugins when invalid class detected.
    """
    pass


# ----------------------------------------------------------------------------


class AxPlugin(object):
    """
    Plugin Subclass Interface.

    Plugins must implement this interface and should extend required base
    implementation superclass AxPluginBase.

    Lifecycle of an AxPlugin object:
        1. Often identified and resolved by class name.
        2. Instantiated around a specific config + extinfo.
        3. Has plugin_create() called to setup and establish connections.
        4. Subclass methods invoked repeatedly to do work for by application.
           The plugin MAY keep state (see below).
        5. Has plugin_destroy() called to clean up and close connections.
        6. Discarded.

    On keeping state and concurrency:
        Engines managing AxPlugins MUST guarantee thread-safe concurrency
        by ensuring any one AxPlugin is only handling one operation at once.
        However no order is guaranteed.  AxPlugin instances may thus keep 
        state not only within a single operation, but between operations
        as well (such as maintaining an open database connection).
    """

    #
    # Abstract Methods
    #

    # abstract
    def __init__(self, options=None, extinfo=None):
        """
        Initialize around specific optional extinfo dict.
        """
        raise NotImplementedError("AxPlugin abstract superclass")

    # abstract
    def plugin_create(self):
        """
        Invoked once to allow plugin to setup what it needs.
        """
        raise NotImplementedError("AxPlugin abstract superclass")

    # abstract
    def plugin_destroy(self):
        """
        Invoked once to allow plugin to clean up after itself.
        """
        raise NotImplementedError("AxPlugin abstract superclass")


# ----------------------------------------------------------------------------


class AxPluginBase(AxPlugin, AxObj):
    """
    Plugin Superclass Base.

    Implements common useful set of functionality, recommended as base
    class for AxPlugins.

    Properties:

      - options : (optional) dict with common configuration options.

      - extinfo : (optional) dict with external configuration
                  not appropriate to store in common options such as
                  passwords, sensitive data, or data which might
                  vary at runtime or by environment.
    """

    def __init__(self, options=None, extinfo=None):
        """
        Initialize around specific optional options and extinfo dicts.
        Call from subclass __init__ via:
            AxPluginBase.__init__(self, options=options, extinfo=extinfo)
        May raise Exception on bad input, so prep valid state first.
        """
        # Safe default values:
        self.options = dict()
        self.extinfo = dict()

        # Configure form args:
        self.configure(options=options, extinfo=extinfo)


    #
    # Public Properties
    #

    @property
    def options(self):
        """Options dict."""
        return self._options
    @options.setter
    def options(self, val):
        self._assert_type("options", val, collections.Mapping)
        self._options = val

    @property
    def extinfo(self):
        """Extinfo dict."""
        return self._extinfo
    @extinfo.setter
    def extinfo(self, val):
        self._assert_type("extinfo", val, collections.Mapping)
        self._extinfo = val


    #
    # Public Methods
    #

    def plugin_option(self, keypath, default=KeyError):
        """
        Shortcut to get specific MetricDef plugin option by dotted key path.
        Keypath "first.second" would look for opts['first']['second'].
        If not present, raises KeyError with helpful error message,
        or returns default if one is specified via 'default' argument.
        """
        return dictutil.dict_get_by_path(
            self.options, keypath, default=default,
            what="{cls} plugin options".format(cls=self.__class__.__name__)
            )

    def plugin_extinfo(self, keypath, default=KeyError):
        """
        Shortcut to get specific extinfo data by dotted key path.
        Keypath "first.second" would look for info['first']['second'].
        If not present, raises KeyError with helpful error message,
        or returns default if one is specified via 'default' argument.
        """
        return dictutil.dict_get_by_path(
            self.extinfo, keypath, default=default,
            what="{cls} plugin extinfo".format(cls=self.__class__.__name__)
            )

    def configure(self, options=None, extinfo=None):
        """
        Set new configuration of either or both of options and extinfo dicts.
        """
        if options is not None:
            self.options = options
        if extinfo is not None:
            self.extinfo = extinfo


    #
    # Protected Methods for Subclasses
    #

    def _format_str(self, 
            fmt,
            context     = None,
            what        = '?',
            od_defaults = Exception
        ):
        """
        Format a string using options, extinfo, and extra context (if any).
        For use by subclasses.
        Protected wrapper for Python str.format, so example fmt values:
          - "This is a string literal"
          - "Size is: {options.size.width}, {options.size.height}"
        
        Optional what param used for logging and errors.
        
        Optional od_defaults attempts to use default value in place of
        Exceptions when some basic (1 level) missing keys/attrs issues 
        are found on ObjectifiedDicts around options and extinfo.

        Subclasses may override to add additional context and call super.
        """
        # Prep format context:
        fmtctx = dict()
        fmtctx['options'] = dictutil.ObjectifiedDict(self.options, 
            what="%s options" % what, default=od_defaults)
        fmtctx['extinfo'] = dictutil.ObjectifiedDict(self.extinfo,
            what="%s extinfo" % what, default=od_defaults)

        # Fix up and add user context:
        if context is not None:
            for k, v in context.iteritems():
                if isinstance(v, collections.Mapping):
                    context[k] = dictutil.ObjectifiedDict(v,
                        what="%s context %s" % (what, k), default=od_defaults)
            fmtctx.update(context)

        # Format string:
        try:
            return fmt.format(**fmtctx)
        except KeyError as e:
            raise KeyError("No %s found formatting '%s': '%s'" %
                (e, what, fmt))
        except AttributeError as e:
            raise AttributeError("%s found formatting '%s': '%s'" %
                (e, what, fmt))


    #
    # Internal Methods
    #

    def __unicode__(self):
        return (u"{cls}()"
        ).format(self=self, cls=self.__class__.__name__,
        )


# ----------------------------------------------------------------------------


def load_plugin_class(
    plugin_id,
    what             = '',
    allow_absolute   = True,
    def_module_name  = None,
    def_cls_name_pfx = '',
    require_base_cls = None,
):
    """
    Imports, returns a class type from a plugin id (dotted string).

    Plugins can be referenced by plugin_id in either default mode
    (using a set of predefined plugins within a specific module)
    or in absolute mode (using any class available for import).
    Absolute mode is triggered by presence of any dots (".") in the 
    plugin id.

    Usage:
        from axonchisel.metrics.foundation.ax.plugin import load_plugin_class
        try:
            plugin_cls = load_plugin_class(
                'my.plugins.MyPlugin',  # (or 'Default1')
                what="Test Plugin",
                def_module_name='app.plugins.default',
                def_cls_name_pfx='DefaultPlugin_',
                require_base_cls=PluginInterface,
            )
        except AxPluginLoadError:
            raise
        plugin = plugin_cls()

    Raises on error: AxPluginLoadError (or subclass)

    Arguments:

      - plugin_id : this str can be of two forms: default and absolute.

            In default mode (when plugin_id contains no dots),
            the plugin_id is appended to def_cls_name_pfx and treated
            as a class name in the def_module_name module.
            E.g. "PrettyOutput"

            In absolute mode (when plugin_id contains one or more dots),
            it is treated as a full absolute path to a class
            within a module.
            E.g. "my.packages.outputpkg.MyOutputClass"

      - what : short (one or few words) human readable description
            of what the plugin represents. For logging and errors.
            E.g. "Output Plugin"

      - allow_absolute : (optional) Set False to prevent absolute mode
            and require default mode handling.

      - def_module_name : (optional) module name in which the default 
            classes can be found, used with default mode plugin_ids.
            This name is as could be imported with 'import'.
            If None, plugin_id must refer to an absolute class.
            E.g. "app.plugins.defaults"

      - def_cls_name_pfx : (optional) str to prepend to default mode
            plugin_id names when constructing default mode class name.
            E.g. "OutputPlugin_"

      - require_base_cls : (optional) type plugin must be subclass of.
            If specified, the found plugin's type is enforced to be
            subclass of this class, or error is raised.
            E.g. AppPluginBase
    """
    # Parse and split up plugin_id. Eg:    'foo.bar.Zig'           'Single'
    splitpath  = plugin_id.split('.')  # = ['foo','bar','Zig']   = ['Single']
    modname = '.'.join(splitpath[:-1]) # = 'foo.bar'             = ''
    clsname = splitpath[-1]            # = 'Zig'                 = 'Single'

    # Initial mode-specific checks and handling:
    if len(modname) > 0: # i.e. dots in plugin_id, so absolute mode attempted
        if not allow_absolute:
            raise AxPluginLoadError_Mode(
                "{w} '{p}' absolute mode not allowed".format(
                w=what, p=plugin_id ))
    else: # else no dots appeared in plugin_id, i.e. default mode
        if def_module_name is None:
            raise AxPluginLoadError_Mode(
                "{w} '{p}' must be absolute".format(
                w=what, p=plugin_id ))
        modname = def_module_name
        clsname = def_cls_name_pfx + clsname

    # Import module:
    try:
        level = 0  # 0 = no relative imports
        fromlist = [clsname]
        module = __import__(modname, globals(), locals(), fromlist, level)
    except ImportError as e:
        raise AxPluginLoadError_Module(
            "{w} '{p}' module import error: {e}".format(
            w=what, p=plugin_id, e=e ))

    # Extract class from module:
    try:
        cls = getattr(module, clsname)
    except AttributeError as e:
        raise AxPluginLoadError_Class(
            "{w} '{p}' class import error: {e}".format(
            w=what, p=plugin_id, e=e ))

    # Test base class:
    if require_base_cls is not None:
        if not issubclass(cls, require_base_cls):
            raise AxPluginLoadError_Type(
                "{w} '{p}' {c} not subclass of {bc}".format(
                w=what, p=plugin_id, c=cls, bc=require_base_cls ))

    return cls



