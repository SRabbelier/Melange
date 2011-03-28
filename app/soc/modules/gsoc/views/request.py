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
from soc.logic import accounts
from soc.logic.exceptions import AccessViolation
from soc.logic.exceptions import NotFound
from soc.models.request import Request
from soc.views import forms
from soc.views.helper.access_checker import isSet

from soc.modules.gsoc.models.organization import GSoCOrganization
from soc.modules.gsoc.models.profile import GSoCProfile
from soc.modules.gsoc.views.base import RequestHandler
from soc.modules.gsoc.views.base_templates import LoggedInMsg

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
    self.check.notStudent()

    # check if the organization exists
    self.mutator.organizationFromKwargs()
    self.check.isOrganizationInURLActive()

    # check if the user is not already mentor role for the organization
    self.check.notMentor()

    # check if there is already a request
    query = db.Query(Request)
    query.filter('type = ', 'Request')
    query.filter('user = ', self.data.user)
    query.filter('group = ', self.data.organization)
    if query.get():
      raise AccessViolation(
          'You have already sent a request to this organization.')

  def context(self):
    """Handler for GSoC Request Page HTTP get request.
    """

    request_form = RequestForm(self.data.POST or None)

    return {
        'logged_in_msg': LoggedInMsg(self.data, apply_link=False),
        'page_name': 'Request to become a mentor',
        'program': self.data.program,
        'invite_form': request_form
    }

  def post(self):
    """Handler for GSoC Request Page HTTP post request.
    """

    request = self._createFromForm()
    if request:
      self.redirect.id(request.key().id())
      self.redirect.to('show_gsoc_request')
    else:
      self.get()

  def _createFromForm(self):
    """Creates a new request based on the data inserted in the form.

    Returns:
      a newly created Request entity or None
    """

    assert isSet(self.data.organization)

    request_form = RequestForm(self.data.POST)

    if not request_form.is_valid():
      return None

    # create a new invitation entity
    request_form.cleaned_data['user'] = self.data.user
    request_form.cleaned_data['group'] = self.data.organization
    request_form.cleaned_data['role'] = 'mentor'
    request_form.cleaned_data['type'] = 'Request'

    return request_form.create(commit=True)


class ShowRequest(RequestHandler):
  """Encapsulate all the methods required to generate Show Request page.
  """

  # maps actions with button names
  ACTIONS = {
      'accept': 'Accept',
      'reject': 'Reject',
      'resubmit': 'Resubmit',
      'withdraw': 'Withdraw',
      }

  def templatePath(self):
    return 'v2/soc/request/base.html'


  def djangoURLPatterns(self):
    return [
        url(r'^gsoc/request/%s$' % url_patterns.ID, self,
            name='show_gsoc_request')
    ]

  def checkAccess(self):
    self.check.isProfileActive()
    
    id = int(self.data.kwargs['id'])
    self.data.invite = self.data.request_entity = Request.get_by_id(id)
    self.check.isRequestPresent(self.data.request_entity, id)

    self.data.organization = self.data.request_entity.group
    self.data.invited_user = self.data.requester = self.data.request_entity.user

    if self.data.POST:
      self.data.action = self.data.POST['action']

      if self.data.action == self.ACTIONS['accept']:
        self.check.canRespondToRequest()
      elif self.data.action == self.ACTIONS['reject']:
        self.check.canRespondToRequest()
      elif self.data.action == self.ACTIONS['resubmit']:
        self.check.canResubmitRequest()
      # withdraw action
    else:
      self.check.canViewRequest()

    self.mutator.canRespondForUser()

    key_name = '/'.join([
        self.data.program.key().name(),
        self.data.requester.link_id])
    self.data.requester_profile = GSoCProfile.get_by_key_name(
        key_name, parent=self.data.requester)

  def context(self):
    """Handler to for GSoC Show Request Page HTTP get request.
    """

    assert isSet(self.data.request_entity)
    assert isSet(self.data.can_respond)
    assert isSet(self.data.organization)
    assert isSet(self.data.requester)

    show_actions = self.data.request_entity.status in ['pending', 'withdrawn']
    if self.data.can_respond and self.data.request_entity.status == 'rejected':
      show_actions = True

    return {
        'page_name': "Request to become a mentor",
        'request': self.data.request_entity,
        'org': self.data.organization,
        'actions': self.ACTIONS,
        'user_name': self.data.requester.name,
        'user_email': accounts.denormalizeAccount(
            self.data.requester.account).email(),
        'show_actions': show_actions,
        'can_respond': self.data.can_respond,
        }

  def post(self):
    """Handler to for GSoC Show Request Page HTTP post request.
    """

    assert isSet(self.data.action)
    assert isSet(self.data.request_entity)

    if self.data.action == self.ACTIONS['accept']:
      self._acceptRequest()
    elif self.data.action == self.ACTIONS['reject']:
      self._rejectRequest()
    elif self.data.action == self.ACTIONS['resubmit']:
      self._resubmitRequest()
    elif self.data.action == self.ACTIONS['withdraw']:
      self._withdrawRequest()

    self.redirect.program()
    self.redirect.to('gsoc_dashboard')

  def _acceptRequest(self):
    """Accepts a request.
    """

    assert isSet(self.data.organization)
    assert isSet(self.data.requester_profile)

    self.data.request_entity.status = 'accepted'
    self.data.requester_profile.mentor_for.append(self.data.organization.key())

    self.data.requester_profile.put()
    self.data.request_entity.put()

  def _rejectRequest(self):
    """Rejects a request. 
    """

    self.data.request_entity.status = 'rejected'
    self.data.request_entity.put()

  def _resubmitRequest(self):
    """Resubmits a request.
    """

    self.data.request_entity.status = 'pending'
    self.data.request_entity.put()

  def _withdrawRequest(self):
    """Withdraws an invitation.
    """

    self.data.request_entity.status = 'withdrawn'
    self.data.request_entity.put()
