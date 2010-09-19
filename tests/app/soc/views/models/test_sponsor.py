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


__authors__ = [
  '"Leo (Chong Liu)" <HiddenPython@gmail.com>',
  ]


import httplib

from django.core import urlresolvers
from django.http import HttpRequest
from django.utils import simplejson

from google.appengine.api import users

from soc.logic.models.sponsor import logic as sponsor_logic
from soc.logic.models.user import logic as user_logic

from tests.test_utils import DjangoTestCase


class SponsorTestForDeveloper(DjangoTestCase):
  """Tests related to the user view for developer users.
  """
  def setUp(self):
    """Set up required for the view tests.
    """
    # Ensure that current user is created
    properties = {
        'account': users.get_current_user(),
        'link_id': 'current_user',
        'name': 'Current User',
        'is_developer': True,
        }
    key_name = user_logic.getKeyNameFromFields(properties)
    self.user = user_logic.updateOrCreateFromKeyName(properties, key_name)
    # Create another user
    email = "another@example.com"
    account = users.User(email=email)
    link_id = 'another_user'
    name = 'Another User'
    properties = {
        'account': account,
        'link_id': link_id,
        'name': name,
        }
    key_name = user_logic.getKeyNameFromFields(properties)
    self.another_user = user_logic.updateOrCreateFromKeyName(properties,
                                                             key_name)

  def createSponsor(self, user):
    """Creates a sponsor role for user.
    """
    # Create a sponsor for a_user
    link_id = 'a_sponsor'
    name = link_id
    founder = 'a_founder'
    phone = '01234567'
    contact_postalcode = 'A postalcode'
    description = 'A description'
    contact_country = 'United States'
    short_name = 'AS'
    contact_city = 'A city'
    home_page = 'http://www.asponsor.com'
    email = 'email@asponsor.com'
    properties = {
        'link_id': link_id,
        'name': name,
        'short_name': short_name,
        'founder': self.user,
        'phone': phone,
        'description': description,
        'contact_country': contact_country,
       'contact_city': 'A City',
       'contact_street': 'A Street',
        'contact_postalcode': contact_postalcode,
        'home_page': home_page,
        'email': email,
        }
    sponsor = sponsor_logic.updateOrCreateFromFields(properties)
    return sponsor, properties

  def testCreateProgramOwner(self):
    """Tests that a developer user can create a program owner.
    """
    url = '/sponsor/create'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/models/edit.html')
    view_triple = urlresolvers.resolve(url)
    kwargs = view_triple[2]
    self.assertEqual(kwargs.get('page_name', 'a'),
                     response.context[0].get('page_name', 'b'))

  def testCreateProgramOwnerWithScopePath(self):
    """Test that a developer user can create a program owner.

    Even if the specified link id is empty.
    """
    url = '/sponsor/create/'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/models/edit.html')
    view_triple = urlresolvers.resolve(url)
    kwargs = view_triple[2]
    self.assertEqual(kwargs.get('page_name', 'a'),
                     response.context[0].get('page_name', 'b'))

  def testCreateProgramOwnerWithLinkId(self):
    """Test that a developer user can create a program owner with a link id.
    """
    link_id = 'a_sponsor'
    url = '/sponsor/create/' + link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/models/edit.html')
    view_triple = urlresolvers.resolve(url)
    kwargs = view_triple[2]
    self.assertEqual(kwargs.get('page_name', 'a'),
                     response.context[0].get('page_name', 'b'))
    form = response.context[0].get('form')
    self.assertTrue(form.initial.get('link_id'), link_id)

  def testEditProgramOwnerSelfExisted(self):
    """Test that a developer user can edit a program owner with a link id.

    The program owner is the user him/herself.
    """
    sponsor, properties = self.createSponsor(self.user)
    url = '/sponsor/edit/' + properties.get('link_id')
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/models/edit.html')
    view_triple = urlresolvers.resolve(url)
    kwargs = view_triple[2]
    self.assertEqual(kwargs.get('page_name', 'a'),
                     response.context[0].get('page_name', 'b'))
    sponsor2 = response.context[0].get('entity')
    self.assertEqual(sponsor.link_id, sponsor2.link_id)
    form = response.context[0].get('form')
    self.assertTrue(form.initial.get('link_id'), properties.get('link_id'))

  def testEditProgramOwnerAnotherExisted(self):
    """Test that a developer user can edit a program owner with a link id.

    The program owner is another user.
    """
    sponsor, properties = self.createSponsor(self.another_user)
    url = '/sponsor/edit/' + properties.get('link_id')
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/models/edit.html')
    view_triple = urlresolvers.resolve(url)
    kwargs = view_triple[2]
    self.assertEqual(kwargs.get('page_name', 'a'),
                     response.context[0].get('page_name', 'b'))
    sponsor2 = response.context[0].get('entity')
    self.assertEqual(sponsor.link_id, sponsor2.link_id)
    form = response.context[0].get('form')
    self.assertTrue(form.initial.get('link_id'), properties.get('link_id'))

  def testEditProgramOwnerNonExisted(self):
    """Test that a developer user cannot edit a non existed program owner.
    """
    link_id = 'not_a_sponsor'
    url = '/sponsor/edit/' + link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.NOT_FOUND)
    self.assertTemplateUsed(response, 'soc/error.html')
    self.assertTemplateNotUsed(response, 'soc/models/edit.html')

  def testDeleteProgramOwnerSelfExisted(self):
    """Test that deleting a program owner him/herself through GET is forbidden.

    The attempt of a developer user to delete a program owner (him/herself)
    through HTTP GET is forbidden.
    """
    sponsor, properties = self.createSponsor(self.user)
    url = '/sponsor/delete/' + properties.get('link_id')
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FORBIDDEN)
    self.assertEqual(response.context, None)

  def testDeleteProgramOwnerAnotherExisted(self):
    """Test that deleting a program owner another user through GET is forbidden.

    The attempt of a developer user to delete a program owner (another user)
    through HTTP GET is forbidden.
    """
    sponsor, properties = self.createSponsor(self.another_user)
    url = '/sponsor/delete/' + properties.get('link_id')
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FORBIDDEN)
    self.assertEqual(response.context, None)

  def testDeleteProgramOwnerNonExisted(self):
    """Test that deleting a non existed program owner through GET is forbidden.

    The attempt of a developer user to delete a non existed program owner
    through HTTP GET is forbidden.
    """
    link_id = 'not_a_sponsor'
    url = '/sponsor/delete/' + link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FORBIDDEN)
    self.assertEqual(response.context, None)

  def testShowProgramOwnerSelfExisted(self):
    """Test that a developer user can show an existed program owner.

    The existed program owner is the developer user him/herself.
    """
    sponsor, properties = self.createSponsor(self.user)
    url = '/sponsor/show/' + properties.get('link_id')
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/group/public.html')
    view_triple = urlresolvers.resolve(url)
    kwargs = view_triple[2]
    self.assertEqual(kwargs.get('page_name', 'a'),
                     response.context[0].get('page_name', 'b'))
    sponsor2 = response.context[0].get('entity')
    self.assertEqual(sponsor.link_id, sponsor2.link_id)

  def testShowProgramOwnerAnotherExisted(self):
    """Test that a developer user can show an existed program owner.

    The existed program owner is another user.
    """
    sponsor, properties = self.createSponsor(self.another_user)
    url = '/sponsor/show/' + properties.get('link_id')
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/group/public.html')
    view_triple = urlresolvers.resolve(url)
    kwargs = view_triple[2]
    self.assertEqual(kwargs.get('page_name', 'a'),
                     response.context[0].get('page_name', 'b'))
    sponsor2 = response.context[0].get('entity')
    self.assertEqual(sponsor.link_id, sponsor2.link_id)

  def testShowProgramOwnerNonExisted(self):
    """Test that error is returned.

    If a developer user tries to show an unexisted program owner.
    """
    link_id = 'not_a_sponsor'
    url = '/sponsor/show/' + link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.NOT_FOUND)
    self.assertTemplateUsed(response, 'soc/error.html')
    self.assertTemplateNotUsed(response, 'soc/group/public.html')

  def testAdminProgramOwnerSelfExisted(self):
    """Test that a developer user can NOT admin a program owner (him/herself).
    """
    sponsor, properties = self.createSponsor(self.user)
    url = '/sponsor/admin/' + properties.get('link_id')
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/error.html')
    self.assertEqual(response.context[0].get('title'), 'Access denied')

  def testAdminProgramOwnerAnotherExisted(self):
    """Test that a developer user can NOT admin a program owner (another user).
    """
    sponsor, properties = self.createSponsor(self.another_user)
    url = '/sponsor/admin/' + properties.get('link_id')
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/error.html')
    self.assertEqual(response.context[0].get('title'), 'Access denied')

  def testAdminProgramOwnerNonExisted(self):
    """Test that a developer user cannot admin a non existed program owner.
    """
    link_id = 'not_a_sponsor'
    url = '/sponsor/admin/' + link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/error.html')
    self.assertTemplateNotUsed(response, 'soc/group/public.html')
    self.assertEqual(response.context[0].get('title'), 'Access denied')

  def testListProgramOwner(self):
    """Test that a developer user can view all existed program owners.

    (sponsors has not been listed/retrieved).
    """
    sponsor, properties = self.createSponsor(self.user)
    another_sponsor, another_properties = self.createSponsor(self.another_user)
    url = '/sponsor/list'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/models/list.html')
    view_triple = urlresolvers.resolve(url)
    kwargs = view_triple[2]
    self.assertEqual(kwargs.get('page_name', 'a'),
                     response.context[0].get('page_name', 'b'))

  def testListRequestsForProgramOwnerSelfExisted(self):
    """Test that a developer can list requests for an existed program owner.

    The existed program owner is the developer user him/herself.
    """
    sponsor, properties = self.createSponsor(self.user)
    link_id = properties.get('link_id')
    url = '/sponsor/list_requests/' + link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/models/list.html')
    view_triple = urlresolvers.resolve(url)
    kwargs = view_triple[2]
    self.assertEqual(kwargs.get('page_name', 'a') + ' ' + link_id,
                     response.context[0].get('page_name', 'b'))

  def testListRequestsForProgramOwnerAnotherExisted(self):
    """Test that a developer can list requests for an existed program owner.

    The existed program owner is another user.
    """
    sponsor, properties = self.createSponsor(self.another_user)
    link_id = properties.get('link_id')
    url = '/sponsor/list_requests/' + link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/models/list.html')
    view_triple = urlresolvers.resolve(url)
    kwargs = view_triple[2]
    self.assertEqual(kwargs.get('page_name', 'a') + ' ' + link_id,
                     response.context[0].get('page_name', 'b'))

  def testListRequestsForProgramOwnerNonExisted(self):
    """Test that error is NOT returned.

    If a developer user tries to list requests for a nonexisted program owner.
    """
    link_id = 'not_a_sponsor'
    url = '/sponsor/list_requests/' + link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/models/list.html')
    view_triple = urlresolvers.resolve(url)
    kwargs = view_triple[2]
    self.assertEqual(kwargs.get('page_name', 'a') + ' ' + link_id,
                     response.context[0].get('page_name', 'b'))

  def testListRolesForProgramOwnerSelfExisted(self):
    """Test that a developer user can list roles for an existed program owner.

    The existed program owner is the developer user him/herself.
    """
    sponsor, properties = self.createSponsor(self.user)
    link_id = properties.get('link_id')
    url = '/sponsor/list_roles/' + link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/models/list.html')
    view_triple = urlresolvers.resolve(url)
    kwargs = view_triple[2]
    self.assertEqual(kwargs.get('page_name', 'a') + ' ' + link_id,
                     response.context[0].get('page_name', 'b'))

  def testListRolesForProgramOwnerAnotherExisted(self):
    """Test that a developer user can list roles for an existed program owner.

    The existed program owner is another user.
    """
    sponsor, properties = self.createSponsor(self.another_user)
    link_id = properties.get('link_id')
    url = '/sponsor/list_roles/' + link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/models/list.html')
    view_triple = urlresolvers.resolve(url)
    kwargs = view_triple[2]
    self.assertEqual(kwargs.get('page_name', 'a') + ' ' + link_id,
                     response.context[0].get('page_name', 'b'))

  def testListRolesForProgramOwnerNonExisted(self):
    """Test that error is NOT returned.

    If a developer user tries to list roles for an unexisted program owner.
    """
    link_id = 'not_a_sponsor'
    url = '/sponsor/list_roles/' + link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/models/list.html')
    view_triple = urlresolvers.resolve(url)
    kwargs = view_triple[2]
    self.assertEqual(kwargs.get('page_name', 'a') + ' ' + link_id,
                     response.context[0].get('page_name', 'b'))

  def testHomeSelf(self):
    """Test that a developer can show the homepage of an existing program owner.

    The existed program owner is the developer user him/herself.
    """
    sponsor, properties = self.createSponsor(self.user)
    url = '/sponsor/home/' + properties.get('link_id')
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/' + 'sponsor/show/' \
                                 + properties.get('link_id')
    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testHomeAnother(self):
    """Test that a developer can show the homepage of an existing program owner.

    The existed program owner is another user.
    """
    sponsor, properties = self.createSponsor(self.another_user)
    url = '/sponsor/home/' + properties.get('link_id')
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/' + 'sponsor/show/' \
                                 + properties.get('link_id')
    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testHomeNonExisted(self):
    """Test that a developer cannot show the homepage of a non-existent owner.
    """
    link_id = 'not_a_sponsor'
    url = '/sponsor/home/' + link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.NOT_FOUND)
    self.assertTemplateUsed(response, 'soc/error.html')
    self.assertTemplateNotUsed(response, 'soc/group/public.html')
