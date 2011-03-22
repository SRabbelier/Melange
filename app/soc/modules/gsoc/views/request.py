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

"""Module containing the view for GSoC request page.
"""

__authors__ = [
  '"Daniel Hans" <daniel.m.hans@gmail.com>',
  ]


from google.appengine.ext import db
from google.appengine.api import users

from django.conf.urls.defaults import url
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext

from soc.logic import dicts
from soc.views import forms
from soc.logic.exceptions import AccessViolation
from soc.logic.exceptions import NotFound

from soc.models.request import Request

from soc.modules.gsoc.models.organization import GSoCOrganization
from soc.modules.gsoc.views.base import RequestHandler

from soc.modules.gsoc.views.helper import url_patterns


class RequestForm(forms.ModelForm):
  """Django form for the request page.
  """

  #link_id = djangoforms.CharField(label='Link ID')

  class Meta:
    model = Request
    css_prefix = 'gsoc_request'
    fields = ['message']


class RequestPage(RequestHandler):
  """Encapsulate all the methods required to generate Request page.
  """

  def templatePath(self):
    return 'v2/modules/gsoc/invite/base.html'

  def djangoURLPatterns(self):
    return [
        url(r'^gsoc/request/%s$' % url_patterns.ORG,
            self, name='gsoc_request')
    ]

  def checkAccess(self):
    """Access checks for GSoC Invite page.
    """

    self.check.isProgramActive()
    
    # check if the current user has a profile, but is not a student
    self.check.isNotStudent()

    # check if the organization exists
    link_id = self.data.kwargs['organization']
    key_name = '%s/%s/%s' % (
        self.data.program.scope_path, self.data.program.link_id, link_id)
    self.data.org = GSoCOrganization.get_by_key_name(key_name)

    if not self.data.org or self.data.org.status != 'active':
      msg = ugettext(
          'The organization with link_id %s does not exist for %s.' % 
          (link_id, self.data.program.name))

      raise NotFound(msg)

    # check if the user is not already mentor role for the organization
    self.check.notHaveRoleForOrganization(self.data.org, 'mentor')

    # check if there is already a request
    query = db.Query(Request)
    query.filter('type = ', 'Request')
    query.filter('user = ', self.data.user)
    query.filter('group = ', self.data.org)
    if query.get():
      raise AccessViolation(
          'You have already sent a request to this organization.')

  def context(self):
    """Handler for GSoC Request Page HTTP get request.
    """

    request_form = RequestForm(self.data.POST or None)

    return {
        'logout_link': users.create_logout_url(self.data.full_path),
        'page_name': 'Request to become a mentor',
        'program': self.data.program,
        'invite_form': request_form
    }

  def post(self):
    """Handler for GSoC Request Page HTTP post request.
    """

    if self._createFromForm():
      kwargs = dicts.filter(self.data.kwargs, [
          'sponsor', 'program', 'organization', 'role'])
      self.redirect(reverse('gsoc_request', kwargs=kwargs))
    else:
      self.get()

  def _createFromForm(self):
    """Creates a new request based on the data inserted in the form.

    Returns:
      a newly created Request entity or None
    """

    assert self.data.org

    request_form = RequestForm(self.data.POST)

    if not request_form.is_valid():
      return None

    # create a new invitation entity
    request_form.cleaned_data['user'] = self.data.user
    request_form.cleaned_data['group'] = self.data.org
    request_form.cleaned_data['role'] = 'mentor'
    request_form.cleaned_data['type'] = 'Request'

    return request_form.create(commit=True)


class ShowRequest(RequestHandler):
  """Encapsulate all the methods required to generate Show Request page.
  """

  ACTIONS = {
      'accept': 'Accept',
      'reject': 'Reject',
      'withdraw': 'Withdraw',
      }

  def templatePath(self):
    return 'v2/soc/request/base.html'


  def djangoURLPatterns(self):
    return [
        url(r'^gsoc/request/%s$' % url_patterns.ID, self,
            name='gsoc_request')
    ]

  def checkAccess(self):
    self.check.isRoleActive()
    
    id = int(self.data.kwargs['id'])
    self.data.request_entity = Request.get_by_id(id)
    self.check.isRequestPresent(self.data.request_entity, id)

    self.data.org = self.data.request_entity.group
    self.data.requester = self.data.request_entity.user

    if self.data.POST:
      self.data.action = self.data.POST['action']

      if self.data.action == self.ACTIONS['accept']:
        self.check.canRespondToRequest()
      elif self.data.action == self.ACTIONS['reject']:
        self.check.canRespondToRequest()
      # withdraw action
    else:
      self.check.canViewRequest()

  def context(self):
    """Handler to for GSoC Show Invitation Page HTTP get request.
    """

    assert self.data.request_entity
    assert self.data.canRespond is not None
    assert self.data.org
    assert self.data.requester

    return {
        'request': self.data.request_entity,
        'org': self.data.org,
        'actions': self.ACTIONS,
        'user': self.data.requester,
        'canRespond': self.data.canRespond,
        } 

  def post(self):
    """Handler to for GSoC Show Request Page HTTP post request.
    """

    assert self.data.action
    assert self.data.request_entity

    if self.data.action == self.ACTIONS['accept']:
      self._acceptRequest()
    elif self.data.action == self.ACTIONS['reject']:
      self._rejectRequest()
    elif self.data.action == self.ACTIONS['withdraw']:
      self._withdrawRequest()

    kwargs = dicts.filter(self.data.kwargs, ['sponsor', 'program'])
    self.redirect(reverse('gsoc_dashboard', kwargs=kwargs))

  def _acceptRequest(self):
    """Accepts a request.
    """

    assert self.data.org

    if not self.data.profile:
      kwargs = dicts.filter(self.data.kwargs, ['sponsor', 'program'])
      self.redirect(reverse('edit_gsoc_profile', kwargs=kwargs))

    self.data.request_entity.status = 'accepted'
    self.data.profile.mentor_for.append(self.data.org.key())

    self.data.request_entity.put()
    self.data.profile.put()

  def _rejectRequest(self):
    """Rejects a request. 
    """

    self.data.request_entity.status = 'rejected'
    self.data.request_entity.put()

  def _withdrawRequest(self):
    """Withdraws an invitation.
    """

    self.data.request_entity.status = 'withdrawn'
    self.data.request_entity.put()
