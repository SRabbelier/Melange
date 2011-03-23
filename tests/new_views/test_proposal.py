#!/usr/bin/env python2.5
#
# Copyright 2011 the Melange authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for proposal view.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


import httplib

from tests.profile_utils import GSoCProfileHelper
from tests.test_utils import DjangoTestCase
from tests.timeline_utils import TimelineHelper

# TODO: perhaps we should move this out?
from soc.modules.gsoc.models.proposal import GSoCProposal
from soc.modules.seeder.logic.seeder import logic as seeder_logic


class ProposalTest(DjangoTestCase):
  """Tests proposal page.
  """

  def setUp(self):
    self.init()

  def assertProposalTemplatesUsed(self, response):
    """Asserts that all the templates from the dashboard were used.
    """
    self.assertGSoCTemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/modules/gsoc/proposal/base.html')
    self.assertTemplateUsed(response, 'v2/modules/gsoc/_form.html')

  def testSubmitProposal(self):
    self.data.createStudent()
    self.timeline.studentSignup()
    url = '/gsoc/proposal/submit/' + self.org.key().name()
    response = self.client.get(url)
    self.assertProposalTemplatesUsed(response)

    # test POST
    override = {'program': self.gsoc, 'score': 0, 'mentor': None, 'org': self.org, 'status': 'new'}
    properties = seeder_logic.seed_properties(GSoCProposal, properties=override)
    postdata = properties.copy()
    postdata['xsrf_token'] = self.getXsrfToken(url)
    response = self.client.post(url, postdata)
    self.assertResponseRedirect(response)

    # TODO(SRabbelier): verify
    proposal = GSoCProposal.all().get()
    self.assertPropertiesEqual(properties, proposal)
