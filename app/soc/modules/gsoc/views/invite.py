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

"""Module containing the view for GSoC invitation page.
"""

__authors__ = [
  '"Daniel Hans" <daniel.m.hans@gmail.com>',
  ]


from google.appengine.ext import db
from google.appengine.api import users

from django import forms as djangoforms
from django.conf.urls.defaults import url
from django.core.urlresolvers import reverse
from django.forms import widgets
from django.utils.translation import ugettext

from soc.logic import cleaning
from soc.logic import dicts
from soc.logic.exceptions import NotFound
from soc.views import forms

from soc.models.request import Request
from soc.models.user import User

from soc.modules.gsoc.views.base import RequestHandler

from soc.modules.gsoc.logic.models.organization import logic as org_logic
from soc.modules.gsoc.models.profile import GSoCProfile
from soc.modules.gsoc.views.helper import access_checker
from soc.modules.gsoc.views.helper import url_patterns


class InviteForm(forms.ModelForm):
  """Django form for the invite page.
  """

  link_id = djangoforms.CharField(label='Link ID')

  class Meta:
    model = Request
    css_prefix = 'gsoc_intivation'
    fields = ['message']

  def __init__(self, request_data, *args, **kwargs):
    super(InviteForm, self).__init__(*args, **kwargs)

    # store request object to cache results of queries
    self.request_data = request_data

    # reorder the fields so that link_id is the first one
    field = self.fields.pop('link_id')
    self.fields.insert(0, 'link_id', field)
    
  def clean_link_id(self):
    """Accepts link_id of users which may be invited.
    """

    assert self.request_data.org

    link_id = cleaning.clean_link_id('link_id')(self)

    # get the user entity that the invitation is to
    invited_user = cleaning.clean_existing_user('link_id')(self)
    self.request_data.invited_user = invited_user
    
    # check if the organization has already sent an invitation to the user
    query = db.Query(Request)
    query.filter('type = ', 'Invitation')
    query.filter('user = ', invited_user)
    query.filter('group = ', self.request_data.org)
    if query.get():
      raise djangoforms.ValidationError(
          'An invitation to this user has already been sent.')

    # check if the user that is invited does not have the role
    key_name = '/'.join([
        self.request_data.program.key().name(),
        invited_user.link_id])
    profile = GSoCProfile.get_by_key_name(key_name, parent=invited_user)
    if self.request_data.kwargs['role'] == 'org_admin':
      role_for = profile.org_admin_for
    else:
      role_for = profile.mentor_for

    for key in role_for:
      if key == self.request_data.org.key():
        raise djangoforms.ValidationError(
            'The user already has this role.')

    
class InvitePage(RequestHandler):
  """Encapsulate all the methods required to generate Invite page.
  """

  def templatePath(self):
    return 'v2/modules/gsoc/invite/base.html'

  def djangoURLPatterns(self):
    return [
        url(r'^gsoc/invite/(?P<role>org_admin|mentor)/%s$' % url_patterns.ORG,
            self, name='gsoc_invite')
    ]

  def checkAccess(self):
    """Access checks for GSoC Invite page.
    """

    checker = access_checker.AccessChecker(self.data)
    #checker.checkIsActive(self.data.program)
      
    link_id = self.data.kwargs['organization']
    filter = {
        'link_id': link_id,
        'scope': self.data.program,
        'status': 'active'
        }
    self.data.org = org_logic.getForFields(filter, unique=True)
    if not self.data.org:
      msg = ugettext(
          'The organization with link_id %s does not exist for %s.' % 
          (link_id, self.data.program.name))

      raise NotFound(msg)

    #checker.checkIsOrgAdminForOrg(self.data.org)

  def context(self):
    """Handler to for GSoC Invitation Page HTTP get request.
    """

    role = 'Org Admin' if self.data.kwargs['role'] == 'org_admin' else 'Mentor'

    invite_form = InviteForm(self.data, self.data.POST or None)

    return {
        'logout_link': users.create_logout_url(self.data.full_path),
        'page_name': 'Invite a new %s' % role,
        'program': self.data.program,
        'invite_form': invite_form
    }

  def _createFromForm(self):
    """Creates a new invitation based on the data inserted in the form.

    Returns:
      a newly created proposal entity or None
    """

    assert self.data.org

    invite_form = InviteForm(self.data, self.data.POST)
    
    if not invite_form.is_valid():
      return None

    assert self.data.invited_user

    # create a new invitation entity
    invite_form.cleaned_data['user'] = self.data.invited_user
    invite_form.cleaned_data['group'] = self.data.org
    invite_form.cleaned_data['role'] = self.data.kwargs['role']
    invite_form.cleaned_data['status'] = 'new'
    invite_form.cleaned_data['type'] = 'Invitation'

    return invite_form.create(commit=True)

  def post(self):
    """Handler to for GSoC Invitation Page HTTP post request.
    """

    if self._createFromForm():
      kwargs = dicts.filter(self.data.kwargs, [
          'sponsor', 'program', 'organization', 'role'])
      self.redirect(reverse('gsoc_invite', kwargs=kwargs))
    else:
      self.get()


# TODO: that may be moved to a separate module
class ShowInvite(RequestHandler):
  """Encapsulate all the methods required to generate Show Invite page.
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
        url(r'^gsoc/invitation/%s$' % url_patterns.ID, self,
            name='gsoc_invitation')
    ]

  def checkAccess(self):
    self.check.isRoleActive()
    
    id = int(self.data.kwargs['id'])
    self.data.invite = Request.get_by_id(id)
    self.data.org = self.data.invite.group
    self.data.invited_user = self.data.invite.user

    self.check.isRequestPresent(self.data.invite, id)

    if self.data.POST:
      self.data.action = self.data.POST['action']

      if self.data.action == self.ACTIONS['accept']:
        self.check.canRespondToInvite()
      elif self.data.action == self.ACTIONS['reject']:
        self.check.canRespondToInvite()
    else:
      self.check.canViewInvite()

  def context(self):
    """Handler to for GSoC Show Invitation Page HTTP get request.
    """

    assert self.data.invite
    assert self.data.canRespond
    assert self.data.org
    assert self.data.invited_user

    return {
        'request': self.data.invite,
        'org': self.data.org,
        'actions': self.ACTIONS,
        'user': self.data.invited_user,
        'canRespond': self.data.canRespond,
        } 

  def post(self):
    """Handler to for GSoC Show Invitation Page HTTP post request.
    """

    assert self.data.action
    assert self.data.invite

    if self.data.action == self.ACTIONS['accept']:
      self._acceptInvitation()
    elif self.data.action == self.ACTIONS['reject']:
      self._rejectInvitation()
    elif self.data.action == self.ACTIONS['withdraw']:
      self._withdrawInvitation()

  def _acceptInvitation(self):
    """Accepts an invitation.
    """

    assert self.data.org

    if not self.data.profile:
      kwargs = dicts.filter(self.data.kwargs, ['sponsor', 'program'])
      self.redirect(reverse('edit_gsoc_profile', kwargs=kwargs))

    self.data.invite.status = 'completed'

    if self.data.invite.role == 'mentor':
      self.data.profile.mentor_for.append(self.data.org.key())
    else:
      self.data.profile.org_admin_for.append(self.data.org.key())

    self.data.invite.put()
    self.data.profile.put()

  def _rejectInvitation(self):
    """Rejects a invitation. 
    """

    self.data.invite.status = 'rejected'
    self.data.invite.put()

  def _withdrawInvitation(self):
    """Withdraws an invitation.
    """

    self.data.invite.status = 'withdrawn'
    self.data.invite.put()
