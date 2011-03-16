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

"""The role conversion updates are defined in this module.
"""

__authors__ = [
    '"Daniel Hans" <daniel.m.hans@gmail.com>',
  ]


import gae_django

from google.appengine.ext import db
from google.appengine.ext import deferred
from google.appengine.runtime import DeadlineExceededError

from soc.models.linkable import Linkable
from soc.models.mentor import Mentor
from soc.models.org_admin import OrgAdmin
from soc.models.role import StudentInfo

from soc.modules.gsoc.models.mentor import GSoCMentor
from soc.modules.gsoc.models.organization import GSoCOrganization
from soc.modules.gsoc.models.org_admin import GSoCOrgAdmin
from soc.modules.gsoc.models.profile import GSoCProfile
from soc.modules.gsoc.models.program import GSoCProgram
from soc.modules.gsoc.models.student import GSoCStudent
from soc.modules.gsoc.models.student_project import StudentProject
from soc.modules.gsoc.models.student_proposal import StudentProposal


ROLE_MODELS = [GSoCMentor, GSoCOrgAdmin, GSoCStudent]

POPULATED_PROFILE_PROPS = set(
    GSoCProfile.properties()) - set(Linkable.properties())

POPULATED_STUDENT_PROPS = StudentInfo.properties()


def getDjangoURLPatterns():
  """Returns the URL patterns for the tasks in this module.
  """

  patterns = [
      (r'^tasks/role_conversion/update_references',
        'soc.tasks.updates.role_conversion.updateReferences'),
      (r'^tasks/role_conversion/update_project_references',
        'soc.tasks.updates.role_conversion.updateStudentProjectReferences'),
      (r'^tasks/role_conversion/update_proposal_references',
        'soc.tasks.updates.role_conversion.updateStudentProposalReferences'),
      (r'^tasks/role_conversion/update_roles$',
        'soc.tasks.updates.role_conversion.updateRoles'),
      (r'^tasks/role_conversion/update_mentors$',
        'soc.tasks.updates.role_conversion.updateMentors'),
      (r'^tasks/role_conversion/update_org_admins$',
        'soc.tasks.updates.role_conversion.updateOrgAdmins'),
      (r'^tasks/role_conversion/update_students$',
        'soc.tasks.updates.role_conversion.updateStudents')]

  return patterns


class RoleUpdater(object):
  """Class which is responsible for updating the entities.
  """

  def __init__(self, model, profile_model, program_field, role_field=None):
    self.MODEL = model
    self.PROFILE_MODEL = profile_model
    self.PROGRAM_FIELD = program_field
    self.ROLE_FIELD = role_field

  def run(self, batch_size=25):
    """Starts the updater.
    """

    self._process(None, batch_size)

  def _process(self, start_key, batch_size):
    """Retrieves entities and creates or updates a corresponding
    Profile entity.
    """

    query = self.MODEL.all()
    if start_key:
      query.filter('__key__ > ', start_key)

    #try:
    entities = query.fetch(batch_size)

    if not entities:
      # all entities has already been processed
      return

    try:
      for entity in entities:
        program = entity.__getattribute__(self.PROGRAM_FIELD)
        user = entity.user

        # try to find an existing Profile entity or create a new one
        key_name = program.key().name() + '/' + user.link_id
        properties = {
            'link_id': entity.link_id,
            'scope_path': program.key().name(),
            'scope': program,
            'parent': user,
            }
        for prop in POPULATED_PROFILE_PROPS:
          properties[prop] = entity.__getattribute__(prop)

        profile = self.PROFILE_MODEL.get_or_insert(
            key_name=key_name, **properties)

        # do not update anything if the role is already in the profile
        if profile.student_info:
          continue
        elif self.ROLE_FIELD:
          if entity.scope.key() in profile.__getattribute__(self.ROLE_FIELD):
            continue

        to_put = [profile]

        if self.ROLE_FIELD:
          # the role is either Mentor or OrgAdmin
          profile.__getattribute__(self.ROLE_FIELD).append(entity.scope.key())
        else:
          # the role is certainly Student; we have to create a new StudentInfo
          properties = {}
          for prop in POPULATED_STUDENT_PROPS:
            properties[prop] = entity.__getattribute__(prop)

          key_name = profile.key().name()
          student_info = StudentInfo(key_name=key_name,
              parent=profile, **properties)
          profile.student_info = student_info
          to_put.append(student_info)

        db.run_in_transaction(db.put, to_put)

      # process the next batch of entities
      start_key = entities[-1].key()
      deferred.defer(self._process, start_key, batch_size)
    except DeadlineExceededError:
      # here we should probably be more careful
      deferred.defer(self._process, start_key, batch_size)


def updateRole(role_name):
  """Starts a task which updates a particular role.
  """

  if role_name == 'gsoc_mentor':
    updater = RoleUpdater(GSoCMentor, GSoCProfile, 'program', 'mentor_for')
  elif role_name == 'gsoc_org_admin':
    updater = RoleUpdater(
        GSoCOrgAdmin, GSoCProfile, 'program', 'org_admin_for')
  elif role_name == 'gsoc_student':
    updater = RoleUpdater(GSoCStudent, GSoCProfile, 'scope')

  updater.run()

def updateRoles(request):
  """Starts a bunch of iterative tasks which update particular roles.

  In order to prevent issues with concurrent access to entities, we set
  ETA so that each role is processed in separation.
  """

  # update org admins
  #updateRole('gsoc_org_admin')

  # update mentors
  #updateRole('gsoc_mentor')

  # update students
  # we can assume that students cannot have any other roles, so we do not
  # need to set ETA
  updateRole('gsoc_student')

def updateMentors(request):
  """Starts an iterative task which update mentors.
  """

  updateRole('gsoc_mentor')

def updateOrgAdmins(request):
  """Starts an iterative task which update org admins.
  """

  updateRole('gsoc_org_admin')

def updateStudents(request):
  """Starts an iterative task which update students.
  """

  updateRole('gsoc_student')

def _getProfileForRole(entity, profile_model):
  """Returns GSoCProfile or GCIProfile which corresponds to the specified
  entity.
  """

  if isinstance(entity, profile_model):
    return entity

  if isinstance(entity, OrgAdmin) or isinstance(entity, Mentor):
    key_name = entity.program.key().name() + '/' + entity.user.key().name()
  else:
    key_name = entity.key().name()

  parent = entity.user
  return profile_model.get_by_key_name(key_name, parent=parent)


def _getProfileKeyForRoleKey(key, profile_model):
  """Returns Key instance of the Profile which corresponds to the Role which
  is represented by the specified Key.
  """

  for model in ROLE_MODELS:
    entity = model.get(key)
    if not entity:
      continue

    profile = _getProfileForRole(entity, profile_model)
    return profile.key()

class ReferenceUpdater(object):
  """Class which is responsible for updating references to Profile in
  the specified model.
  """

  def __init__(self, model, profile_model, fields_to_update,
               lists_to_update=[]):
    self.MODEL = model
    self.PROFILE_MODEL = profile_model
    self.FIELDS_TO_UPDATE = fields_to_update
    self.LISTS_TO_UPDATE = lists_to_update

  def run(self, batch_size=25):
    """Starts the updater.
    """

    self._process(None, batch_size)

  def _process(self, start_key, batch_size):
    """Iterates through the entities and updates the references.
    """

    query = self.MODEL.all()
    if start_key:
      query.filter('__key__ > ', start_key)

    try:
      entities = query.fetch(batch_size)

      if not entities:
        # all entities has already been processed
        return

      for entity in entities:
        for field in self.FIELDS_TO_UPDATE:
          old_reference = entity.__getattribute__(field)

          if not old_reference:
            continue

          # check if the field has not been updated
          if isinstance(old_reference, self.PROFILE_MODEL):
            continue

          profile = _getProfileForRole(old_reference, self.PROFILE_MODEL)
          entity.__setattr__(field, profile)

        for list_property in self.LISTS_TO_UPDATE:
          l = entity.__getattribute__(list_property)
          new_l = []
          for key in l:
            new_l.append(_getProfileKeyForRoleKey(key, self.PROFILE_MODEL))
          entity.__setattr__(list_property, new_l)

      db.put(entities)
      start_key = entities[-1].key()
      deferred.defer(self._process, start_key, batch_size)
    except DeadlineExceededError:
      # here we should probably be more careful
      deferred.defer(self._process, start_key, batch_size)


def updateReferencesForModel(model):
  """Starts a task which updates references for a particular model.
  """

  if model == 'student_proposal':
    updater = ReferenceUpdater(StudentProposal, GSoCProfile,
        ['scope', 'mentor'], ['possible_mentors'])
  elif model == 'student_project':
    updater = ReferenceUpdater(StudentProject, GSoCProfile,
        ['mentor', 'student'], ['additional_mentors'])

  updater.run()


def updateStudentProjectReferences(request):
  """Starts a bunch of iterative tasks which update references in
  StudentProjects.
  """

  updateReferencesForModel('student_project')


def updateStudentProposalReferences(request):
  """Starts a bunch of iterative tasks which update references in
  StudentProposals.
  """

  updateReferencesForModel('student_proposal')


def updateReferences(request):
  """Starts a bunch of iterative tasks which update references to various roles.
  """

  # updates student proposals
  updateReferencesForModel('student_proposal')

  # updates student projects
  updateReferencesForModel('student_project')

