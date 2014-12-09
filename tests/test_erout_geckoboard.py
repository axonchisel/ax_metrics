"""
Ax_Metrics - Test EROut_geckoboard (geckoboard.com output)

STATUS NOTE:
This module currently has insufficient test coverage.
The individual EROut plugins are executed to ensure the code is run,
but the output is not really verified at this point.


------------------------------------------------------------------------------
Author: Dan Kamins <dos at axonchisel dot net>
Copyright (c) 2014 Dan Kamins, AxonChisel.net
"""


# ----------------------------------------------------------------------------


import pytest
import logging
import json

import axonchisel.metrics.io.erout.plugins.ero_geckoboard as ero_geckoboard
from axonchisel.metrics.run.servant.config import ServantConfig
from axonchisel.metrics.run.servant.request import ServantRequest
from axonchisel.metrics.run.servant.state import ServantState
from axonchisel.metrics.run.servant.servant import Servant

from .util import log_config, load_metset, load_queryset


# ----------------------------------------------------------------------------


def setup_module(module):
    log_config(level=logging.INFO)
    # log_config(level=logging.DEBUG)


# ----------------------------------------------------------------------------


class TestEROut_geckoboard(object):
    """
    Test general EROut.
    """

    #
    # Setup / Teardown
    #

    def setup_method(self, method):
        self.jout = dict()
        self.emfetch_extinfo = {
        }
        self.erout_extinfo = {
            '_default': {
                'jout': self.jout,
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
            'cancels_r7d',
        ]
        self.erout_plugin_ids = []
        self.sreq = ServantRequest(
            query_ids=self.query_ids,
            erout_plugin_ids=self.erout_plugin_ids,
        )



    #
    # Tests
    #

    def test_bullet(self):
        self.erout_extinfo.update({
            'geckoboard_bullet': {
            }
        })
        servant = Servant(self.sconfig)
        self.sreq.collapse = True
        self.sreq.noghosts = True
        # self.sreq.query_ids = [ 'new_users_r7d' ] # TEMP
        self.sreq.erout_plugin_ids = ['geckoboard_bullet']
        servant.process(self.sreq)
        jstr = json.dumps(self.jout, indent=4)
        # print jstr
        jout2 = json.loads(jstr)
        assert len(jout2['item']) == 4
        assert jout2['orientation'] == 'vertical'
        assert jout2['item'][0]['label'] == "New Users"

    def test_numsec_comp(self):
        self.erout_extinfo.update({
            'geckoboard_numsec_comp': {
            }
        })
        servant = Servant(self.sconfig)
        self.sreq.collapse = True
        self.sreq.noghosts = False
        self.sreq.query_ids = [ 'rev_new_sales_qtd' ]
        # self.sreq.query_ids = [ 'cancels_r7d' ]
        self.sreq.erout_plugin_ids = [ 'geckoboard_numsec_comp' ]
        servant.process(self.sreq)
        jstr = json.dumps(self.jout, indent=4)
        # print jstr
        # TODO

    def test_numsec_trend(self):
        self.erout_extinfo.update({
            'geckoboard_numsec_trend': {
            }
        })
        servant = Servant(self.sconfig)
        self.sreq.collapse = False
        self.sreq.noghosts = True
        self.sreq.query_ids = [ 'new_users_r7d' ]
        self.sreq.erout_plugin_ids = [ 'geckoboard_numsec_trend' ]
        servant.process(self.sreq)
        jstr = json.dumps(self.jout, indent=4)
        # print jstr
        # TODO

    def test_meter(self):
        self.erout_extinfo.update({
            'geckoboard_meter': {
            }
        })
        servant = Servant(self.sconfig)
        self.sreq.query_ids = [ 'new_users_r7d' ]
        self.sreq.erout_plugin_ids = [ 'geckoboard_meter' ]
        servant.process(self.sreq)
        jstr = json.dumps(self.jout, indent=4)
        # print jstr
        # TODO

    def test_text(self):
        self.erout_extinfo.update({
            'geckoboard_text': {
            }
        })
        servant = Servant(self.sconfig)
        self.sreq.collapse = True
        # self.sreq.noghosts = True
        self.sreq.query_ids = [ 'cancels_r7d' ]
        self.sreq.erout_plugin_ids = [ 'geckoboard_text' ]
        servant.process(self.sreq)
        jstr = json.dumps(self.jout, indent=4)
        # print jstr
        # TODO

    def test_rag(self):
        self.erout_extinfo.update({
            'geckoboard_rag': {
            }
        })
        servant = Servant(self.sconfig)
        self.sreq.collapse = True
        self.sreq.noghosts = True
        self.sreq.query_ids = [ 'cancels_r7d', 'cancels_r7d'  ]
        self.sreq.erout_plugin_ids = [ 'geckoboard_rag' ]
        servant.process(self.sreq)
        jstr = json.dumps(self.jout, indent=4)
        # print jstr
        # TODO


