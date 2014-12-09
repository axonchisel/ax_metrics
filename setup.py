"""
Ax_Metrics - setup.py Packaging and Installation Support

Note to developers:
System utility 'pandoc' is required for building PyPi package.
Install on OS X with 'brew install pandoc' (~1 hr unattended).
More info: http://johnmacfarlane.net/pandoc/

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


from __future__ import print_function
from sys import stderr
import os
import re
from subprocess import Popen, PIPE
from setuptools import setup, find_packages


# ----------------------------------------------------------------------------
# Setup dependencies and packages


install_requires = [
    'PyYAML>=3.11',    # YAML parse support (used by MDefL and MQL parsers)
    'requests>=2.4.3', # HTTP requests for humans (used by EMFetcher_http)
]

test_requires = [
    'pytest>=2.6.4',   # py.test test harness
    'coverage>=3.7.1', # code coverage assessment
]


# ----------------------------------------------------------------------------
# Setup utility functions


def read_file(fname):
    """Read and return contents of relative file."""
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def exec_file(fname):
    """Execute contents of relative Python file in global scope."""
    exec(read_file(fname)) in globals()

def md_to_rst(s):
    """
    Return reStructuredText equiv string contents of Markdown string.
    If conversion (via 'pandoc' cmdline) fails, returns raw Markdown.
    Requires pandoc system utility:  http://johnmacfarlane.net/pandoc/
    """
    try:
        args = ['pandoc', '-r', 'markdown', '-w', 'rst']
        p = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        (pout, perr) = p.communicate(s)
        if p.returncode == 0:
            return pout
        raise ValueError("pandoc exit %d, stderr: %s" % (p.returncode, perr))
    except Exception as e:
        print("warning: error converting MD to RST: ", e, file=stderr)
        print("warning: ensure 'pandoc' is properly installed!", file=stderr)
    return s

def pypi_md_clean(s):
    """
    Sanitize Markdown string to remove markup that would break PyPi rendering
    when converted to reStructuredText (as of 2014-12).
    """
    # Remove relative and anchor links:
    re_rel_link    = re.compile(r'\[([^\]]*)\]\((\.[^\)]*)\)', re.DOTALL)
    re_anchor_link = re.compile(r'\[([^\]]*)\]\((#[^\)]*)\)', re.DOTALL)
    s = re.sub(re_rel_link,    r'\1', s)
    s = re.sub(re_anchor_link, r'\1', s)
    return s

def pypi_longdesc():
    """
    Load and convert README.md to PyPi compatible (2014) RST string.
    If errors occur (such as 'pandoc' utility not installed), the raw
    Markdown file is returned, which will probably look ugly in PyPi.
    """
    return md_to_rst(pypi_md_clean(read_file('README.md')))


# ----------------------------------------------------------------------------
# Setup main


exec_file('py/axonchisel/metrics/version.py')  # (sets __version__ global)

setup(
    name         = "Ax_Metrics",
    version      = __version__,
    license      = "MIT",
    author       = "Dan Kamins",
    author_email = "dos@axonchisel.net",
    url          = "https://github.com/axonchisel/ax_metrics",
    platforms    = "Any",
    description  = "\"BI Glue\" Business Intelligence middleware library for "
                   "aggregation of metrics/KPI from any source and custom "
                   "reporting for humans or other APIs",
    keywords     = [
        "business intelligence", "BI", "data", "data warehouse", "DW", "BIDW",
        "metrics", "KPI", "analytics",
        "middleware", "library", "api",
        "report", "chart", "dashboard",
    ],
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Telecommunications Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Database",
        "Topic :: Office/Business :: Financial",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Monitoring",
    ],
    long_description = pypi_longdesc(),
    package_dir = {'': 'py'},
    packages = find_packages(where='py'),

    # These extra options trigger harmless distutils warning.  ignore.
    # setuptools (including pip) likes and uses it.
    install_requires = install_requires,
    tests_require = test_requires,  # (yes, 'tests_require')
)

