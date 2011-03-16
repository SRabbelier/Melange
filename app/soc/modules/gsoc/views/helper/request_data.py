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

"""Module containing the RequestData object that will be created for each
request in the GSoC module.
"""

__authors__ = [
    '"Daniel Hans" <daniel.m.hans@gmail.com>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from google.appengine.ext import db

from soc.models import role
from soc.logic.models.host import logic as host_logic
from soc.logic.models.site import logic as site_logic
from soc.logic.models.user import logic as user_logic
from soc.views.helper.request_data import RequestData

from soc.modules.gsoc.models import profile

from soc.modules.gsoc.logic.models.mentor import logic as mentor_logic
from soc.modules.gsoc.logic.models.organization import logic as org_logic
from soc.modules.gsoc.logic.models.org_admin import logic as org_admin_logic
from soc.modules.gsoc.logic.models.org_app_survey import logic as org_app_logic
from soc.modules.gsoc.logic.models.program import logic as program_logic
from soc.modules.gsoc.logic.models.student import logic as student_logic


class RequestData(RequestData):
  """Object containing data we query for each request in the GSoC module.

  The only view that will be exempt is the one that creates the program.

  Fields:
    site: The Site entity
    user: The user entity (if logged in)
    program: The GSoC program entity that the request is pointing to
    program_timeline: The GSoCTimeline entity
    host: The Host entity of the current user for the sponsor of the program
    org_admins: GSoCOrgadmin entities belonging to the current user and program
    mentors: GSoCMentor entities belonging to the current user and program
    student: GSoCStudent entity belonging to the current user and program

  Raises:
    out_of_band: 404 when the program does not exist
  """

  def __init__(self):
    """Constructs an empty RequestData object.
    """
    super(RequestData, self).__init__()
    # program wide fields
    self.program = None
    self.program_timeline = None
    self.org_app = None

    # user profile specific fields
    self.profile = None
    self.is_host = False
    self.mentor_for = []
    self.org_admin_for = []
    self.student_info = None

  def populate(self, request, *args, **kwargs):
    """Populates the fields in the RequestData object.

    Args:
      request: Django HTTPRequest object.
      args & kwargs: The args and kwargs django sends along.
    """
    super(RequestData, self).populate(request, *args, **kwargs)

    if kwargs.get('sponsor') and kwargs.get('program'):
      program_keyfields = {'link_id': kwargs['program'],
                           'scope_path': kwargs['sponsor']}
      self.program = program_logic.getFromKeyFieldsOr404(program_keyfields)
    else:
      self.program =  self.site.active_program

    self.program_timeline = self.program.timeline

    org_app_fields = {'scope': self.program}
    self.org_app = org_app_logic.getOneForFields(org_app_fields)

    if 'organization' in kwargs:
      org_keyfields = {
          'link_id': kwargs.get('organization'),
          'scope_path': self.program.key().id_or_name(),
          }
      self.organization = org_logic.getFromKeyFieldsOr404(org_keyfields)

    if self.user:
      key_name = '%s/%s' % (self.program.key().name(), self.user.link_id)
      self.profile = profile.GSoCProfile.get_by_key_name(
          key_name, parent=self.user)

      self.is_host = self.program.scope.key() in self.user.host_for

    if self.profile:
      orgs = set(self.profile.mentor_for + self.profile.org_admin_for)
      org_map = dict((i.key(), i) for i in db.get(orgs))

      self.mentor_for = [org_map[i] for i in self.profile.mentor_for]
      self.org_admin_for = [org_map[i] for i in self.profile.org_admin_for]
      self.student_info = self.profile.student_info
