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

"""Module containing the AccessChecker class that contains helper functions
for checking access.
"""

__authors__ = [
    '"Daniel Hans" <daniel.m.hans@gmail.com>',
  ]


from django.utils.translation import ugettext

from google.appengine.api import users

from soc.logic.helper import timeline as timeline_helper
from soc.logic.models.user import logic as user_logic

from soc.logic.exceptions import LoginRequest
from soc.logic.exceptions import RedirectRequest
from soc.logic.exceptions import AccessViolation

from soc.modules.gsoc.models.organization import GSoCOrganization
from soc.modules.gsoc.models.proposal import GSoCProposal


DEF_AGREE_TO_TOS_MSG_FMT = ugettext(
    'You must agree to the <a href="%(tos_link)s">site-wide Terms of'
    ' Service</a> in your <a href="/user/edit_profile">User Profile</a>'
    ' in order to view this page.')

DEF_NOT_PARTICIPATING_MSG = ugettext(
    'You are not participating in this program and have no access.')

DEF_ALREADY_PARTICIPATING_MSG = ugettext(
    'You cannot become a Student because you are already participating '
    'in this program.')

DEF_DEV_LOGOUT_LOGIN_MSG_FMT = ugettext(
    'Please <a href="%%(sign_out)s">sign out</a>'
    ' and <a href="%%(sign_in)s">sign in</a>'
    ' again as %(role)s to view this page.')

DEF_NEED_ROLE_MSG = ugettext(
    'You do not have the required role.')

DEF_NO_USER_LOGIN_MSG = ugettext(
    'Please create <a href="/user/create_profile">User Profile</a>'
    ' in order to view this page.')

DEF_PAGE_INACTIVE_MSG = ugettext(
    'This page is inactive at this time.')

DEF_SCOPE_INACTIVE_MSG = ugettext(
    'The scope for this request is not active.')

DEF_PROGRAM_INACTIVE_MSG_FMT = ugettext(
    'This page is inaccessible because %s is not active at this time.')

DEF_PAGE_INACTIVE_OUTSIDE_MSG_FMT = ugettext(
    'This page is inactive before %s and after %s.')

DEF_NO_SUCH_PROGRAM_MSG = ugettext(
    'The url is wrong (no program was found).')

DEF_ROLE_INACTIVE_MSG = ugettext(
    'This page is inaccessible because you do not have a profile '
    'in the program at this time.')

DEF_IS_NOT_STUDENT_MSG = ugettext(
    'This page is inaccessible because you do not have a student role '
    'in the program.')

DEF_IS_STUDENT_MSG = ugettext(
    'This page is inaccessible because you are registered as a student.')

DEF_ORG_DOES_NOT_EXISTS_MSG_FMT = ugettext(
    'Organization, whose link_id is %(link_id)s, does not exist in '
    '%(program)s.')

DEF_ORG_NOT_ACTIVE_MSG_FMT = ugettext(
    'Organization %(name)s is not active in %(program)s.')

DEF_ID_BASED_ENTITY_NOT_EXISTS_MSG_FMT = ugettext(
    '%(model)s entity, whose id is %(id)s, does not exist.')

DEF_ID_BASED_ENTITY_INVALID_MSG_FMT = ugettext(
    '%(model)s entity, whose id is %(id)s, is invalid at this time.')

DEF_ENTITY_DOES_NOT_BELONG_TO_YOU = ugettext(
    'This %(model)s entity does not belong to you.')

DEF_NOT_HOST_MSG = ugettext(
    'You need to be a program adminstrator to access this page.')

DEF_ALREADY_PARTICIPATING_AS_NON_STUDENT_MSG = ugettext(
    'You cannot register as a student since you are already a '
    'mentor or organization administrator in %s.')

DEF_ALREADY_PARTICIPATING_AS_STUDENT_MSG = ugettext(
    'You cannot register as a %s since you are already a '
    'student in %s.')

DEF_NOT_VALID_INVITATION_MSG = ugettext(
    'This is not a valid invitation.')

DEF_HAS_ALREADY_ROLE_FOR_ORG_MSG = ugettext(
    'You already have %(role)s role for %(org)s.')

class AccessChecker(object):
  """Helper classes for access checking.
  """

  def __init__(self, data=None):
    """Initializes the access checker object.
    """

    self.data = data
    self.gae_user = users.get_current_user()

  def fail(self, message):
    """Raises an AccessViolation with the specified message.
    """
    raise AccessViolation(message)

  def isLoggedIn(self):
    """Raises an alternate HTTP response if Google Account is not logged in.
    """

    if self.gae_user:
      return

    raise LoginRequest()

  def isUser(self):
    """Raises an alternate HTTP response if Google Account has no User entity.

    Raises:
      AccessViolationResponse:
      * if no User exists for the logged-in Google Account, or
      * if no Google Account is logged in at all
      * if User has not agreed to the site-wide ToS, if one exists
    """

    self.isLoggedIn()

    if self.data.user:
      return

    raise AccessViolation(DEF_NO_USER_LOGIN_MSG)

  def isHost(self):
    """Checks whether the current user has a host role.
    """

    if self.data.is_host:
      return

    raise AccessViolation(DEF_NOT_HOST_MSG)

  def hasUserEntity(self):
    """Raises an alternate HTTP response if Google Account has no User entity.

    Raises:
      AccessViolationResponse:
      * if no User exists for the logged-in Google Account, or
      * if no Google Account is logged in at all
    """

    self.isLoggedIn()

    if self.data.user:
      return

    raise AccessViolation(DEF_NO_USER_LOGIN_MSG)

  def isDeveloper(self):
    """Raises an alternate HTTP response if Google Account is not a Developer.

    Raises:
      AccessViolationResponse:
      * if User is not a Developer, or
      * if no User exists for the logged-in Google Account, or
      * if no Google Account is logged in at all
    """

    self.isUser()

    if self.data.user.is_developer:
      return

    if users.is_current_user_admin():
      return

    login_message_fmt = DEF_DEV_LOGOUT_LOGIN_MSG_FMT % {
        'role': 'a Site Developer ',
        }

    raise AccessViolation(login_message_fmt)

  def isProgramActive(self):
    """Checks that the program is active.
    """

    if not self.data.program:
      raise AccessViolation(DEF_NO_SUCH_PROGRAM_MSG)

    if self.data.program.status == 'visible':
      return

    raise AccessViolation(
        DEF_PROGRAM_INACTIVE_MSG_FMT % self.data.program.name)

  def isActivePeriod(self, period_name):
    """Checks if the given period is active for the given program.

    Args:
      period_name: the name of the period which is checked
    """
    self.isProgramActive()

    if timeline_helper.isActivePeriod(self.data.program_timeline, period_name):
      return

    active_period = timeline_helper.activePeriod(self.data.program_timeline, period_name)

    raise AccessViolation(DEF_PAGE_INACTIVE_OUTSIDE_MSG_FMT % active_period)

  def canApplyStudent(self, edit_url):
    """Checks if the user can apply as a student.
    """

    if self.data.profile and self.data.profile.student_info:
      raise RedirectRequest(edit_url)

    self.isActivePeriod('student_signup')

    if not self.data.profile:
      return

    raise AccessViolation(
        DEF_ALREADY_PARTICIPATING_AS_NON_STUDENT_MSG % self.data.program.name)

  def canApplyNonStudent(self, role, edit_url):
    """Checks if the user can apply as a mentor or org admin.
    """

    if not self.data.profile.student_info:
      raise RedirectRequest(edit_url)

    if not self.data.profile:
      return

    raise AccessViolation(DEF_ALREADY_PARTICIPATING_AS_STUDENT_MSG % (
        role, self.data.program.name))

  def isRoleActive(self):
    """Checks if the role of the current user is active.
    """

    if self.data.profile and self.data.profile.status == 'active':
      return

    raise AccessViolation(DEF_ROLE_INACTIVE_MSG)

  def isActiveStudent(self):
    """Checks if the user is an active student.
    """

    self.isRoleActive()

    if self.data.student_info:
      return

    raise AccessViolation(DEF_IS_NOT_STUDENT_MSG)

  def isNotStudent(self):
    """Checks if the current user has a profile, but is not registered 
    as a student.
    """

    self.isRoleActive()

    if not self.data.student_info:
      return

    raise AccessViolation(DEF_IS_STUDENT_MSG)

  def notHaveRoleForOrganization(self, org, role):
    """Checks if the user have not the specified role for the organization.
    """

    if not self.data.profile:
      return

    if role == 'org_admin':
      roles = self.data.profile.org_admin_for
    else:
      roles = self.data.profile.mentor_for

    key = org.key()
    if key in roles:
      error_msg = DEF_HAS_ALREADY_ROLE_FOR_ORG_MSG % {
          'role': 'Mentor' if role == 'mentor' else 'Org Admin',
          'org': org.name
          }
      raise AccessViolation(error_msg)

  def hasRoleForOrganization(self, org, role):
    """Checks if the user has the specified role for the organization.
    """

    self.isRoleActive()

    if role == 'org_admin':
      roles = self.data.profile.org_admin_for
    else:
      roles = self.data.profile.mentor_for

    key = org.key()
    if key in roles:
      return

    raise AccessViolation(DEF_NEED_ROLE_MSG)

  def isOrganizationInURLActive(self):
    """Checks if the organization in URL exists and if its status is active.

    Side effects (RequestData):
      - if the organization exists and is active, it is saved as 'organization'
    """

    # kwargs which defines an organization
    fields = ['sponsor', 'program', 'organization']

    key_name = '/'.join(self.data.kwargs[field] for field in fields) 
    self.data.organization = GSoCOrganization.get_by_key_name(key_name)

    if not self.data.organization:
      error_msg = DEF_ORG_DOES_NOT_EXISTS_MSG_FMT % {
          'link_id': self.data.kwargs['organization'],
          'program': self.data.program.name
          }
      raise AccessViolation(error_msg)

    if self.data.organization.status != 'active':
      error_msg = DEF_ORG_NOT_ACTIVE_MSG_FMT % {
          'name': self.data.organization.name,
          'program': self.data.program.name
          }
      raise AccessViolation(error_msg)

  def isProposalInURLValid(self):
    """Checks if the proposal in URL exists.

    Side effects (RequestData):
      - if the proposal exists and is active, it is saved as 'proposal'
    """

    id = int(self.data.kwargs['id'])
    self.data.proposal = GSoCProposal.get_by_id(id, parent=self.data.profile)

    if not self.data.proposal:
      error_msg = DEF_ID_BASED_ENTITY_NOT_EXISTS_MSG_FMT % {
          'model': 'GSoCProposal',
          'id': id
          }
      raise AccessViolation(error_msg)

    if self.data.proposal.status == 'invalid':
      error_msg = DEF_ID_BASED_ENTITY_INVALID_MSG_FMT % {
          'model': 'GSoCProposal',
          'id': id,
          }
      raise AccessViolation(error_msg)

  def canStudentUpdateProposal(self):
    """Checks if the student is eligible to submit a proposal.
    """
    
    # check if the timeline allows updating proposals
    self.isActivePeriod('student_signup')

    # TODO: it should be changed - we should not assume that the proposal
    # is already in RequestData
    if self.data.proposal.status == 'invalid':
      error_msg = DEF_ID_BASED_ENTITY_INVALID_MSG_FMT % {
          'model': 'GSoCProposal',
          'id': id,
          }
      raise AccessViolation(error_msg)

    # check if the proposal belongs to the current user
    expected_profile = self.data.proposal.parent()
    if expected_profile.key().name() != self.data.profile.key().name():
      error_msg = DEF_ENTITY_DOES_NOT_BELONG_TO_YOU % {
          'model': 'GSoCProposal'
          }
      raise AccessViolation(error_msg)

  def isIdBasedEntityPresent(self, entity, id, model_name):
    """Checks if the entity is not None.
    """

    if entity is not None:
      return

    error_msg = DEF_ID_BASED_ENTITY_NOT_EXISTS_MSG_FMT % {
        'model': model_name,
        'id': id,
        }
    raise AccessViolation(error_msg)

  def isRequestPresent(self, entity, id):
    """Checks if the specified Request entity is not None.
    """

    self.isIdBasedEntityPresent(entity, id, 'Request')

  def canRespondToInvite(self):
    """Checks if the current user can accept the invitation.
    """

    assert self.data.invite
    assert self.data.org
    assert self.data.invited_user

    # check if the entity represents an invitation
    if self.data.invite.type != 'Invitation':
      raise AccessViolation(DEF_NOT_VALID_INVITATION_MSG)

    # check if the entity can be responded
    if self.data.invite.status not in ['pending']:
      raise AccessViolation(DEF_NOT_VALID_INVITATION_MSG)

    # check if the entity is addressed to the current user
    if self.data.invited_user.key() != self.data.user.key():
      error_msg = DEF_ENTITY_DOES_NOT_BELONG_TO_YOU % {
          'model': 'Request'
          }
      raise AccessViolation(error_msg)

    # check if the user does not have this role
    self.notHaveRoleForOrganization(self.data.org, self.data.invite.role)

  def canViewInvite(self):
    """Checks if the current user can see the invitation.
    """

    assert self.data.invite
    assert self.data.org
    assert self.data.invited_user

    # check if the entity represents an invitation
    if self.data.invite.type != 'Invitation':
      raise AccessViolation(DEF_NOT_VALID_INVITATION_MSG)

    # check if the entity is addressed to the current user
    if self.data.invited_user.key() != self.data.user.key():
      # check if the current user is an org admin for the organization
      self.hasRoleForOrganization(self.data.org, 'org_admin')
      self.data.canRespond = False
    else:
      self.data.canRespond = True
