#!/usr/bin/env python2.5
#
# Copyright 2009 the Melange authors.
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


__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


import unittest

from tests.test_utils import MockRequest
from tests.test_utils import StuboutHelper

from tests.app.soc.logic.models.test_model import TestModelLogic

from soc.views.helper import access
from soc.views.models import base


class TestView(base.View):
  """
  """

  def __init__(self):
    """
    """

    rights = access.Checker(None)
    rights['unspecified'] = ['deny']
    rights['any_access'] = ['allow']
    rights['show'] = ['allow']

    params = {}
    params['name'] = "Test"
    params['logic'] = TestModelLogic()
    params['rights'] = rights

    super(TestView, self).__init__(params=params)


class BaseTest(unittest.TestCase):
  """Tests related to the base view.
  """

  def setUp(self):
    """Set up required for the view tests.
    """

    self.view = TestView()
    self.stubout_helper = StuboutHelper()
    self.stubout_helper.stuboutBase()

  def tearDown(self):
    """Tears down the test environment.
    """

    self.stubout_helper.tearDown()

  def testErrorOnNonExistantEntity(self):
    """
    """

    request = MockRequest("/test/public")
    request.start()
    access_type = "show"
    page_name = "Show Test"
    django_args = {'link_id': 'foo', 'scope_path': 'bar'}
    actual = self.view.public(request, access_type, page_name=page_name, **django_args)
    request.end()
    self.assertTrue('error' in actual)
