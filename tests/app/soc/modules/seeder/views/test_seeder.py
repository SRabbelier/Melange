#!/usr/bin/env python2.5
#
# Copyright 2010 the Melange authors.
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
"""Tests Data Seeder views.
"""

__authors__ = [
  '"Felix Kerekes" <sttwister@gmail.com>',
  ]


import httplib
from django.utils import simplejson
from tests.test_utils import DjangoTestCase

from google.appengine.api import users

from soc.middleware.xsrf import XsrfMiddleware
from soc.logic.helper import xsrfutil
from soc.logic.models.user import logic as user_logic


class DataSeederViewTest(DjangoTestCase):
  """Tests data seeder views.
  """
  def setUp(self):
    """Set up required for the view tests.
    """
    # Ensure that current user with developer privilege is created
    user_properties = {
        'account': users.get_current_user(),
        'link_id': 'current_user',
        'name': 'Current User',
        'is_developer': True,
        }
    user_logic.updateOrCreateFromFields(user_properties)

  def testShowHome(self):
    """Tests showing the seeder home page.
    """
    url = '/seeder/home'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'modules/seeder/home.html')

  def testGetData(self):
    """Tests getting the JSON data.
    """
    url = '/seeder/get_data'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)

  def getXsrfToken(self):
    """Returns an XSRF token for POST requests.
    """
    request = None
    xsrf = XsrfMiddleware()
    key = xsrf._getSecretKey(request)
    user_id = xsrfutil._getCurrentUserId()
    xsrf_token = xsrfutil._generateToken(key, user_id)
    return xsrf_token

  def ajaxRequest(self, url, postdata):
    """Makes an AJAX request and returns the response.
    """
    postdata['xsrf_token'] = self.getXsrfToken()
    return self.client.post(url, postdata,
                            HTTP_X_REQUESTED_WITH='XMLHttpRequest')


  def testSeedNoConfiguration(self):
    """Tests sending no configuration sheet.
    """
    url = '/seeder/seed'
    postdata = {'data': ''}
    response = self.ajaxRequest(url, postdata)
    self.assertEqual(response.status_code, httplib.OK)
    json = simplejson.loads(response.content)
    self.assertTrue('error' in json)

  def testSeedEmptyConfiguration(self):
    """Tests sending an empty configuration sheet.
    """
    url = '/seeder/seed'
    postdata = {'data': '[]'}
    response = self.ajaxRequest(url, postdata)
    self.assertEqual(response.status_code, httplib.OK)
    json = simplejson.loads(response.content)
    self.assertEquals(json['result'], 'success')

  def testSeedInvalidConfiguration(self):
    """Tests sending an invalid configuration sheet.
    """
    url = '/seeder/seed'
    postdata = {'data': 'a09u3lijw3'}
    response = self.ajaxRequest(url, postdata)
    self.assertEqual(response.status_code, httplib.OK)
    json = simplejson.loads(response.content)
    self.assertTrue('error' in json)
