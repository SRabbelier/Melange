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

from soc.logic.models.user import logic as user_logic

from soc.logic.exceptions import LoginRequest
from soc.logic.exceptions import RedirectRequest
from soc.logic.exceptions import BadRequest
from soc.logic.exceptions import NotFound
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

DEF_PAGE_INACTIVE_BEFORE_MSG_FMT = ugettext(
    'This page is inactive before %s')

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

DEF_NOT_ADMIN_MSG = ugettext(
    'You need to be a organization administrator for %s to access this page.')

DEF_NOT_MENTOR_MSG = ugettext(
    'You need to be a mentor for %s to access this page.')

DEF_ALREADY_ADMIN_MSG = ugettext(
    'You cannot be a organization administrator for %s to access this page.')

DEF_ALREADY_MENTOR_MSG = ugettext(
    'You cannot be a mentor for %s to access this page.')

DEF_NOT_DEVELOPER_MSG = ugettext(
    'You need to be a site developer to access this page.')

DEF_ALREADY_PARTICIPATING_AS_NON_STUDENT_MSG = ugettext(
    'You cannot register as a student since you are already a '
    'mentor or organization administrator in %s.')

DEF_ALREADY_PARTICIPATING_AS_STUDENT_MSG = ugettext(
    'You cannot register as a %s since you are already a '
    'student in %s.')

DEF_NOT_VALID_INVITATION_MSG = ugettext(
    'This is not a valid invitation.')

DEF_NOT_VALID_REQUEST_MSG = ugettext(
    'This is not a valid request.')

DEF_HAS_ALREADY_ROLE_FOR_ORG_MSG = ugettext(
    'You already have %(role)s role for %(org)s.')

DEF_PROPOSAL_NOT_PUBLIC_MSG = ugettext(
    'This proposal is not made public, '
    'and you are not the student who submitted the proposal, '
    'nor are you a mentor for the organization it was submitted to.')

DEF_NOT_PUBLIC_DOCUMENT = ugettext(
    'This document is not publically readable.')

DEF_NO_DOCUMENT = ugettext(
    'The document was not found')


unset = object()


def isSet(value):
  """Returns true iff value is not unset.
  """
  return value is not unset


class Mutator(object):
  """Helper class for access checking.

  Mutates the data object as requested.
  """

  def __init__(self, data):
    self.data = data
    self.unsetAll()

  def unsetAll(self):
    self.data.action = unset
    self.data.can_respond = unset
    self.data.document = unset
    self.data.invited_user = unset
    self.data.invite = unset
    self.data.key_name = unset
    self.data.organization = unset
    self.data.private_comments_visible = unset
    self.data.proposal = unset
    self.data.proposer = unset
    self.data.proposer_user = unset
    self.data.public_comments_visible = unset
    self.data.public_only = unset
    self.data.request_entity = unset
    self.data.requester = unset
    self.data.scope_path = unset

  def organizationFromKwargs(self):
    # kwargs which defines an organization
    fields = ['sponsor', 'program', 'organization']

    key_name = '/'.join(self.data.kwargs[field] for field in fields)
    self.data.organization = GSoCOrganization.get_by_key_name(key_name)

  def documentKeyNameFromKwargs(self):
    """Returns the document key fields from kwargs.

    Returns False if not all fields were supplied/consumed.
    """
    from soc.models.document import Document

    fields = []
    kwargs = self.data.kwargs.copy()

    prefix = kwargs.pop('prefix', None)
    fields.append(prefix)

    if prefix in ['site', 'user']:
      fields.append(kwargs.pop('scope', None))

    if prefix in ['sponsor', 'gsoc_program', 'gsoc_org']:
      fields.append(kwargs.pop('sponsor', None))

    if prefix in ['gsoc_program', 'gsoc_org']:
      fields.append(kwargs.pop('program', None))

    if prefix in ['gsoc_org']:
      fields.append(kwargs.pop('organization', None))

    fields.append(kwargs.pop('document', None))

    if any(kwargs.values()):
      raise BadRequest("Unexpected value for document url")

    if not all(fields):
      raise BadRequest("Missing value for document url")

    self.data.scope_path = '/'.join(fields[1:-1])
    self.data.key_name = '/'.join(fields)
    self.data.document = Document.get_by_key_name(self.data.key_name)

  def proposalFromKwargs(self):
    id = int(self.data.kwargs['id'])
    self.data.proposal = GSoCProposal.get_by_id(id, parent=self.data.profile)

  def canRespondForUser(self):
    assert isSet(self.data.invited_user)
    assert isSet(self.data.invite)

    if self.data.invited_user.key() != self.data.user.key():
      # org admins may see the invitations and can respond to requests
      self.data.can_respond = self.data.invite.type == 'Request'
    else:
      # user that the entity refers to may only respond if it is a Request
      self.data.can_respond = self.data.invite.type == 'Invitation'

  def commentVisible(self):
    assert isSet(self.data.proposer_user)

    self.data.public_comments_visible = False
    self.data.private_comments_visible = False

    # if the user is not logged in, no comments can be made
    if not self.data.user:
      return

    # if the current user is the proposer, he or she may access public comments
    if self.data.user.key() == self.data.proposer_user.key():
      self.data.public_comments_visible = True
      return

    # All the mentors and org admins from the organization may access public
    # and private comments.
    if self.data.mentorFor(self.data.proposal_org):
      self.data.public_comments_visible = True
      self.data.private_comments_visible = True
      return


class DeveloperMutator(Mutator):
  def canRespondForUser(self):
    self.data.can_respond = True

  def commentVisible(self):
    self.data.public_comments_visible = True
    self.data.private_comments_visible = True


class BaseAccessChecker(object):
  """Helper class for access checking.

  Should contain all access checks that apply to both regular users
  and developers.
  """

  def __init__(self, data):
    """Initializes the access checker object.
    """
    self.data = data
    self.gae_user = users.get_current_user()

  def fail(self, message):
    """Raises an AccessViolation with the specified message.
    """
    raise AccessViolation(message)

  def isLoggedIn(self):
    """Ensures that the user is logged in.
    """

    if self.gae_user:
      return

    raise LoginRequest()

  def isUser(self):
    """Checks if the current user has an User entity.
    """
    self.isLoggedIn()

    if self.data.user:
      return

    raise AccessViolation(DEF_NO_USER_LOGIN_MSG)

  def isDeveloper(self):
    """Checks if the current user is a Developer.
    """
    self.isUser()

    if self.data.user.is_developer:
      return

    if users.is_current_user_admin():
      return

    raise AccessViolation(DEF_NOT_DEVELOPER_MSG)

  def isProfileActive(self):
    """Checks if the profile of the current user is active.
    """
    self.isLoggedIn()

    if self.data.profile and self.data.profile.status == 'active':
      return

    raise AccessViolation(DEF_ROLE_INACTIVE_MSG)


class DeveloperAccessChecker(BaseAccessChecker):
  """Helper class for access checking.

  Allows most checks.
  """

  def __getattr__(self, name):
    return lambda *args, **kwargs: None


class AccessChecker(BaseAccessChecker):
  """Helper class for access checking.
  """

  def isHost(self):
    """Checks whether the current user has a host role.
    """
    self.isLoggedIn()

    if self.data.is_host:
      return

    raise AccessViolation(DEF_NOT_HOST_MSG)

  def isProgramActive(self):
    """Checks that the program is active.

    Active means 'visible' or 'inactive'.
    """
    if not self.data.program:
      raise AccessViolation(DEF_NO_SUCH_PROGRAM_MSG)

    if self.data.program.status in ['visible', 'inactive']:
      return

    raise AccessViolation(
        DEF_PROGRAM_INACTIVE_MSG_FMT % self.data.program.name)

  def acceptedOrgsAnnounced(self):
    """Checks if the accepted orgs have been announced.
    """
    self.isProgramActive()

    if self.data.timeline.orgsAnnounced():
      return

    period = self.data.timeline.orgsAnnouncedOn()
    raise AccessViolation(DEF_PAGE_INACTIVE_BEFORE_MSG_FMT % period)

  def acceptedStudentsAnnounced(self):
    """Checks if the accepted students have been announced.
    """
    self.isProgramActive()

    if self.data.timeline.studentsAnnounced():
      return

    period = self.data.timeline.studentsAnnouncedOn()
    raise AccessViolation(DEF_PAGE_INACTIVE_BEFORE_MSG_FMT % period)

  def canApplyStudent(self, edit_url):
    """Checks if the user can apply as a student.
    """
    self.isLoggedIn()

    if self.data.profile and self.data.profile.student_info:
      raise RedirectRequest(edit_url)

    self.studentSignupActive()

    if not self.data.profile:
      return

    raise AccessViolation(
        DEF_ALREADY_PARTICIPATING_AS_NON_STUDENT_MSG % self.data.program.name)

  def canApplyNonStudent(self, role, edit_url):
    """Checks if the user can apply as a mentor or org admin.
    """
    self.isLoggedIn()

    if self.data.profile and not self.data.profile.student_info:
      raise RedirectRequest(edit_url)

    if not self.data.profile:
      return

    raise AccessViolation(DEF_ALREADY_PARTICIPATING_AS_STUDENT_MSG % (
        role, self.data.program.name))

  def isActiveStudent(self):
    """Checks if the user is an active student.
    """
    self.isProfileActive()

    if self.data.student_info:
      return

    raise AccessViolation(DEF_IS_NOT_STUDENT_MSG)

  def notStudent(self):
    """Checks if the current user has a non-student profile.
    """
    self.isProfileActive()

    if not self.data.student_info:
      return

    raise AccessViolation(DEF_IS_STUDENT_MSG)

  def notOrgAdmin(self):
    """Checks if the user is not an admin.
    """
    self.isProfileActive()
    assert isSet(self.data.organization)

    if self.data.organization.key() not in self.data.profile.org_admin_for:
      return

    raise AccessViolation(DEF_ALREADY_ADMIN_MSG % self.data.organization.name)

  def notMentor(self):
    """Checks if the user is not a mentor.
    """
    self.isProfileActive()
    assert isSet(self.data.organization)

    if self.data.organization.key() not in self.data.profile.mentor_for:
      return

    raise AccessViolation(DEF_ALREADY_MENTOR_MSG % self.data.organization.name)

  def isOrgAdmin(self):
    """Checks if the user is an org admin.
    """
    assert isSet(self.data.organization)
    self.isOrgAdminForOrganization(self.data.organization)

  def isMentor(self):
    """Checks if the user is a mentor.
    """
    assert isSet(self.data.organization)
    self.isMentorForOrganization(self.data.organization)

  def isOrgAdminForOrganization(self, org):
    """Checks if the user is an admin for the specified organiztaion.
    """
    self.isProfileActive()

    if org.key() in self.data.profile.org_admin_for:
      return

    raise AccessViolation(DEF_NOT_ADMIN_MSG % org.name)

  def isMentorForOrganization(self, org):
    """Checks if the user is an admin for the specified organiztaion.
    """
    self.isProfileActive()

    if org.key() in self.data.profile.mentor_for:
      return

    raise DEF_NOT_MENTOR_MSG % org.name

  def isOrganizationInURLActive(self):
    """Checks if the organization in URL exists and if its status is active.
    """
    assert isSet(self.data.organization)

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
    """
    assert isSet(self.data.proposal)

    if not self.data.proposal:
      error_msg = DEF_ID_BASED_ENTITY_NOT_EXISTS_MSG_FMT % {
          'model': 'GSoCProposal',
          'id': self.data.kwargs['id']
          }
      raise AccessViolation(error_msg)

    if self.data.proposal.status == 'invalid':
      error_msg = DEF_ID_BASED_ENTITY_INVALID_MSG_FMT % {
          'model': 'GSoCProposal',
          'id': self.data.kwargs['id'],
          }
      raise AccessViolation(error_msg)

  def studentSignupActive(self):
    """Checks if the student signup period is active.
    """
    self.isProgramActive()

    if self.data.timeline.studentSignup():
      return

    raise AccessViolation(DEF_PAGE_INACTIVE_OUTSIDE_MSG_FMT %
        self.data.timeline.studentsSignupBetween())

  def canStudentUpdateProposal(self):
    """Checks if the student is eligible to submit a proposal.
    """
    assert isSet(self.data.proposal)

    self.isActiveStudent()
    self.isProposalInURLValid()

    # check if the timeline allows updating proposals
    self.studentSignupActive()

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

  def _isIdBasedEntityPresent(self, entity, id, model_name):
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
    self._isIdBasedEntityPresent(entity, id, 'Request')

  def canRespondToInvite(self):
    """Checks if the current user can accept/reject the invitation.
    """
    assert isSet(self.data.invite)
    assert isSet(self.data.invited_user)

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
    if self.data.invite.role == 'org_admin':
      self.notOrgAdmin()
    else:
      self.notMentor()

  def canRespondToRequest(self):
    """Checks if the current user can accept/reject the request.
    """
    assert isSet(self.data.request_entity)
    assert isSet(self.data.requester)

    # check if the entity represents an invitation
    if self.data.request_entity.type != 'Request':
      raise AccessViolation(DEF_NOT_VALID_REQUEST_MSG)

    # check if the entity can be responded
    if self.data.request_entity.status not in ['pending']:
      raise AccessViolation(DEF_NOT_VALID_REQUEST_MSG)

    # check if the user is an admin for the organization
    self.isOrgAdmin()

  def canViewInvite(self):
    """Checks if the current user can see the invitation.
    """
    assert isSet(self.data.organization)
    assert isSet(self.data.invite)
    assert isSet(self.data.invited_user)

    self._canAccessRequestEntity(
        self.data.invite, self.data.invited_user, self.data.organization)

  def canViewRequest(self):
    """Checks if the current user can see the request.
    """
    assert isSet(self.data.organization)
    assert isSet(self.data.request_entity)
    assert isSet(self.data.requester)

    self._canAccessRequestEntity(
        self.data.request_entity, self.data.requester, self.data.organization)

  def _canAccessRequestEntity(self, entity, user, org):
    """Checks if the current user is allowed to access a Request entity.
    
    Args:
      entity: an entity which belongs to Request model
      user: user entity that the Request refers to
      org: organization entity that the Request refers to
    """
    # check if the entity is addressed to the current user
    if user.key() != self.data.user.key():
      # check if the current user is an org admin for the organization
      self.isOrgAdmin()

  def canAccessProposalEntity(self):
    """Checks if the current user is allowed to access a Proposal entity.
    """

    assert isSet(self.data.proposal)
    assert isSet(self.data.proposal_org)
    assert isSet(self.data.proposer_user)

    # if the proposal is public, everyone may access it
    if self.data.proposal.is_publicly_visible:
      return

    if not self.data.user:
      raise AccessViolation(DEF_PROPOSAL_NOT_PUBLIC_MSG)

    self.isProfileActive()
    # if the current user is the proposer, he or she may access it
    if self.data.user.key() == self.data.proposer_user.key():
      return

    # all the mentors and org admins from the organization may access it
    if self.data.proposal_org.key() in self.data.profile.mentor_for:
      return

    raise AccessViolation(DEF_PROPOSAL_NOT_PUBLIC_MSG)

  def canEditDocument(self):
    self.isHost()

  def canViewDocument(self):
    """Checks if the specified user can see the document.
    """
    assert isSet(self.data.document)

    if not self.data.document:
      raise NotFound(DEF_NO_DOCUMENT)

    if self.data.document.read_access == 'public':
      return

    raise AccessViolation(DEF_NOT_PUBLIC_DOCUMENT)
