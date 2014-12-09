#!/bin/sh

#
# Ax_Metrics - Unit testing coverage measurement
#
# Runs all unit tests using py.test wrapped in coverage.py.
# See http://nedbatchelder.com/code/coverage/
# Outputs:
#  - HTML report in ./htmlcov/index.html 
#  - basic console report printed to stdout
#
# Requires coverage.py.  Install with:
#   $ pip install coverage
#
# ------------------------------------------------------------------------------
# Author: Dan Kamins <dos at axonchisel dot net>
# Copyright (c) 2014 Dan Kamins, AxonChisel.net
#

# ----------------------------------------------------------------------------

COVERAGE_SOURCE="axonchisel.metrics"
RUN_PY="`dirname $0`/RUN.py"
RUN_OPTS="$*"

# ----------------------------------------------------------------------------

echo "[Ax_Metrics - automated py.test coverage measurement]"

date

coverage erase
coverage run --source=$COVERAGE_SOURCE "$RUN_PY" $RUN_OPTS
TEST_RESULT="$?"

date

if [ $TEST_RESULT -ne 0 ]
then
  exit $?
fi

coverage html
coverage report

date

echo "See more detailed HTML report in ./htmlcov/index.html"
