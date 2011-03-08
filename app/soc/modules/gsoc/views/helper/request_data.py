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
    self.profile = None
    self.program = None
    self.program_timeline = None
    self.org_app = None
    self.host = None
    self.org_admin = []
    self.mentor = []
    self.student = None
    self.role = None
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

    if 'sponsor' in kwargs and 'program' in kwargs:
      program_keyfields = {'link_id': kwargs.get('program'),
                           'scope_path': kwargs.get('sponsor')}
      self.program = program_logic.getFromKeyFieldsOr404(program_keyfields)
    else:
      self.program =  self.site.active_progam

    self.program_timeline = self.program.timeline

    org_app_fields = {'scope': self.program}
    self.org_app = org_app_logic.getOneForFields(org_app_fields)

    if self.user:
      fields = {'user': self.user,
                'scope': self.program.scope,
                'status': 'active'}
      self.host = host_logic.getOneForFields(fields)

      fields = {'user': self.user,
                'program': self.program,
                'status': ['active', 'inactive']}
      self.org_admin = org_admin_logic.getOneForFields(fields)
      self.mentor = mentor_logic.getOneForFields(fields)

      fields = {'user': self.user,
                'scope': self.program,
                'status': ['active', 'inactive']}
      self.student = student_logic.getOneForFields(fields)
      key_name = '%s/%s' % (self.program.key().name(), self.user.link_id)
      self.role = self.profile = profile.GSoCProfile.get_by_key_name(
          key_name, parent=self.user)

      if self.role:
        orgs = set(self.role.mentor_for + self.role.org_admin_for)
        org_map = dict((i.key(), i) for i in db.get(orgs))

        self.mentor_for = [org_map[i] for i in self.role.mentor_for]
        self.org_admin_for = [org_map[i] for i in self.role.org_admin_for]
        self.student_info = self.role.student_info
