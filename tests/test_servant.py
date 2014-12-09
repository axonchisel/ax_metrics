"""
Ax_Metrics - Test servant package

------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import pytest
import logging
from StringIO import StringIO

import axonchisel.metrics.io.erout.plugins.ero_csv as ero_csv
from axonchisel.metrics.run.servant.config import ServantConfig
from axonchisel.metrics.run.servant.request import ServantRequest
from axonchisel.metrics.run.servant.state import ServantState
from axonchisel.metrics.run.servant.servant import Servant

from .util import dt, log_config, load_metset, load_queryset



# ----------------------------------------------------------------------------


def setup_module(module):
    log_config(level=logging.INFO)
    # log_config(level=logging.DEBUG)


# ----------------------------------------------------------------------------


class TestServant(object):
    """
    Test Servant.
    """

    #
    # Setup / Teardown
    #

    def setup_method(self, method):
        self.buf1 = StringIO()
        self.emfetch_extinfo = {
        }
        self.erout_extinfo = {
            'csv': {
                'fout': self.buf1,
            }
        }
        self.metset1 = load_metset( 'mqe-metset1.yml' )
        self.queryset1 = load_queryset( 'queryset2.yml' )
        self.sconfig = ServantConfig(
            metset = self.metset1,
            queryset = self.queryset1,
            emfetch_extinfo = self.emfetch_extinfo,
            erout_extinfo = self.erout_extinfo,
            )
        self.query_ids = [
            'new_users_mtd',
            'new_users_r7d',
            'rev_new_sales_qtd',
        ]
        self.erout_plugin_ids = ['strbuf', 'csv']
        self.sreq = ServantRequest(
            query_ids=self.query_ids,
            erout_plugin_ids=self.erout_plugin_ids,
        )


    #
    # Tests
    #

    def test_basic(self):
        servant = Servant(self.sconfig)
        servant.process(self.sreq)

    def test_collapse(self):
        servant = Servant(self.sconfig)
        self.sreq.collapse = True
        servant.process(self.sreq)
        lines = self.buf1.getvalue().splitlines()
        assert len(lines) == 10  # (header + 3 queries + 6 ghosts)

    def test_from_params(self):
        servant = Servant(self.sconfig)
        params = {
            'query': 'new_users_mtd,new_users_r7d,  rev_new_sales_qtd  ,,',
            'erout': 'strbuf,csv',
        }
        sreq = ServantRequest.from_params(params)
        assert sreq.collapse == False
        assert sreq.noghosts == False
        servant.process(sreq)
        params['collapse'] = '1'
        params['noghosts'] = '1'
        sreq = ServantRequest.from_params(params)
        assert sreq.collapse == True
        assert sreq.noghosts == True
        servant.process(sreq)

    def test_state(self):
        sstate = ServantState()
        sstate.erouts = [ero_csv.EROut_csv()]
        with pytest.raises(TypeError):
            sstate.erouts = ['not an EROut']
        str(sstate)

    def test_misc(self):
        servant = Servant(self.sconfig)
        str(servant)
        str(servant.config)

    def test_config_bad(self):
        sconfig = ServantConfig()
        with pytest.raises(ValueError):
            sconfig.validate()
        sconfig.metset = self.metset1
        with pytest.raises(ValueError):
            sconfig.validate()
        sconfig.queryset = self.queryset1
        with pytest.raises(ValueError):
            sconfig.validate()
        sconfig.emfetch_extinfo = self.emfetch_extinfo
        with pytest.raises(ValueError):
            sconfig.validate()
        sconfig.erout_extinfo = self.erout_extinfo
        sconfig.validate()



