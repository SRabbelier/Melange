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


from google.appengine.ext import db
from google.appengine.ext import deferred
from google.appengine.runtime import DeadlineExceededError

from soc.models.linkable import Linkable

from soc.modules.gsoc.models.mentor import GSoCMentor
from soc.modules.gsoc.models.org_admin import GSoCOrgAdmin
from soc.modules.gsoc.models.profile import GSoCProfile
from soc.modules.gsoc.models.student import GSoCStudent


POPULATED_PROPERTIES = set(
    GSoCProfile.properties()) - set(Linkable.properties())

def getDjangoURLPatterns():
  """Returns the URL patterns for the tasks in this module.
  """

  patterns = [
      (r'^tasks/role_conversion/update_roles$',
        'soc.tasks.updates.role_conversion.updateRoles')]

  return patterns

class Updater(object):
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

    try:
      entities = query.fetch(batch_size)

      if not entities:
        # all entities has already been processed
        return
      
      to_put = []
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
        for p in POPULATED_PROPERTIES:
          properties[p] = entity.__getattribute__(p)

        profile = self.PROFILE_MODEL.get_or_insert(
            key_name=key_name, **properties)
        to_put.append(profile)

        if self.ROLE_FIELD:
          # the role is either Mentor or OrgAdmin
          profile.__getattribute__(self.ROLE_FIELD).append(entity.scope.key())
        else:
          # the role is certainly Student; we have to create a new StudentInfo
          student_info = StudentInfo(parent=profile)
          profile.student_info = student_info
          to_put.append(student_info)

      db.run_in_transaction(db.put, to_put)
      start_key = entities[-1].key()
      deferred.defer(self._process, start_key, batch_size)
    except DeadlineExceededError:
      # here we should probably be more careful
      deferred.defer(self._process, start_key, batch_size)

def updateRole(role_name):
  """Starts a task which updates a particular role.
  """

  if role_name == 'gsoc_mentor':
    updater = Updater(GSoCMentor, GSoCProfile, 'program', 'mentor_for')
  elif role_name == 'gsoc_org_admin':
    updater = Updater(GSoCOrgAdmin, GSoCProfile, 'program', 'org_admin_for')
  elif role_name == 'gsoc_student':
    updater = Updater(GSoCStudent, GSoCProfile, 'scope')

  updater.run()

def updateRoles(request):
  """Starts a bunch of iterative tasks which update particular roles.

  In order to prevent issues with concurrent access to entities, we set
  ETA so that each role is processed in separation.
  """

  # update org admins
  updateRole('gsoc_org_admin')

  # update mentors
  #updateRole('gsoc_mentor')

  # update students
  # we can assume that students cannot have any other roles, so we do not
  # need to set ETA
#  updateRole('gsoc_student')
