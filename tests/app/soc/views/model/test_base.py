#!/usr/bin/python2.5
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
from tests.pymox import stubout

from tests.app.soc.logic.models.test_model import TestModelLogic

from soc.views.helper import access
from soc.views.helper import responses
from soc.views.models import base


def error_raw(error, request, template=None, context=None):
  """
  """

  return {
      'error': error,
      'request': request,
      'template': template,
      'context': context,
      }

def respond_raw(request, template, context=None, args=None, headers=None):
  """
  """

  return {
      'request': request,
      'template': template,
      'context': context,
      'args': args,
      'headers': headers,
      }


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
    self.stubout = stubout.StubOutForTesting()
    self.stubout.Set(responses, 'respond', respond_raw)
    self.stubout.Set(responses, 'errorResponse', error_raw)

  def testErrorOnNonExistantEntity(self):
    """
    """

    request = MockRequest("/test/public")
    access_type = "show"
    page_name = "Show Test"
    django_args = {'link_id': 'foo', 'scope_path': 'bar'}
    actual = self.view.public(request, access_type, page_name=page_name, **django_args)
    self.assertTrue('error' in actual)
