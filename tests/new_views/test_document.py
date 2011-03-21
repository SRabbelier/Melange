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
from tests.test_utils import DjangoTestCase

# TODO: perhaps we should move this out?
from soc.modules.seeder.logic.seeder import logic as seeder_logic
from soc.modules.seeder.logic.providers.string import DocumentKeyNameProvider


class EditProgramTest(DjangoTestCase):
  """Tests program edit page.
  """

  def setUp(self):
    from soc.models.document import Document
    from soc.modules.gsoc.models.program import GSoCProgram
    self.gsoc = seeder_logic.seed(GSoCProgram)
    properties = {
        'prefix': 'gsoc_program',
        'scope': self.gsoc,
        'key_name': DocumentKeyNameProvider(),
    }
    self.document = seeder_logic.seed(Document, properties=properties)

  def testShowDocument(self):
    url = '/gsoc/document/show/' + self.document.key().name()
    response = self.client.get(url)
    self.assertGSoCTemplatesUsed(response)

  def testEditDocument(self):
    url = '/gsoc/document/edit/' + self.document.key().name()
    response = self.client.get(url)
    self.assertGSoCTemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/modules/gsoc/document/base.html')
    self.assertTemplateUsed(response, 'v2/modules/gsoc/_form.html')
