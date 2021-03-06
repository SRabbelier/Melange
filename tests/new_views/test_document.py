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

from soc.models.document import Document

from tests.timeline_utils import TimelineHelper
from tests.test_utils import DjangoTestCase
from tests.profile_utils import GSoCProfileHelper

# TODO: perhaps we should move this out?
from soc.modules.seeder.logic.seeder import logic as seeder_logic
from soc.modules.seeder.logic.providers.string import DocumentKeyNameProvider


class EditProgramTest(DjangoTestCase):
  """Tests program edit page.
  """

  def setUp(self):
    self.init()

    properties = {
        'prefix': 'site',
        'scope': self.site,
        'read_access': 'public',
        'key_name': DocumentKeyNameProvider(),
    }
    self.document = self.seed(Document, properties)

  def testShowDocument(self):
    url = '/gsoc/document/show/' + self.document.key().name()
    response = self.client.get(url)
    self.assertGSoCTemplatesUsed(response)

  def testCreateDocumentRestriction(self):
    # TODO(SRabbelier): test document ACL
    pass

  def testCreateDocument(self):
    self.data.createHost()
    url = '/gsoc/document/edit/gsoc_program/%s/doc' % self.gsoc.key().name()
    response = self.client.get(url)
    self.assertGSoCTemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/modules/gsoc/document/base.html')
    self.assertTemplateUsed(response, 'v2/modules/gsoc/_form.html')

    # test POST
    override = {
        'prefix': 'gsoc_program', 'scope': self.gsoc, 'link_id': 'doc',
        'key_name': DocumentKeyNameProvider(), 'modified_by': self.data.user,
        'home_for': None, 'author': self.data.user, 'is_featured': None,
        'write_access': 'admin', 'read_access': 'public',
    }
    properties = seeder_logic.seed_properties(Document, properties=override)
    postdata = properties.copy()
    postdata['xsrf_token'] = self.getXsrfToken(url)
    response = self.client.post(url, postdata)
    self.assertResponseRedirect(response, url)

    key_name = properties['key_name']
    document = Document.get_by_key_name(key_name)
    self.assertPropertiesEqual(properties, document)
