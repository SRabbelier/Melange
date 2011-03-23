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


"""Tests for program related views.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


import httplib

from tests.timeline_utils import TimelineHelper
from tests.profile_utils import GSoCProfileHelper
from tests.test_utils import DjangoTestCase

# TODO: perhaps we should move this out?
from soc.modules.seeder.logic.seeder import logic as seeder_logic


class EditProgramTest(DjangoTestCase):
  """Tests program edit page.
  """

  def setUp(self):
    from soc.modules.gsoc.models.program import GSoCProgram
    self.gsoc = seeder_logic.seed(GSoCProgram)
    self.data = GSoCProfileHelper(self.gsoc)

  def assertProgramTemplatesUsed(self, response):
    """Asserts that all the templates from the program were used.
    """
    self.assertGSoCTemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/modules/gsoc/program/base.html')
    self.assertTemplateUsed(response, 'v2/modules/gsoc/_form.html')

  def testEditProgramHostOnly(self):
    url = '/gsoc/program/edit/' + self.gsoc.key().name()
    response = self.client.get(url)
    self.assertErrorTemplatesUsed(response)

  def testEditProgram(self):
    from soc.models.document import Document
    self.data.createHost()
    url = '/gsoc/program/edit/' + self.gsoc.key().name()
    response = self.client.get(url)
    self.assertProgramTemplatesUsed(response)

    properties = {'prefix': 'gsoc_program', 'scope': self.gsoc}
    seeder_logic.seed(Document, properties=properties)

    response = self.getJsonResponse(url)
    self.assertIsJsonResponse(response)
    self.assertEqual(1, len(response.context['data']))
