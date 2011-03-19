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


"""Utils for manipulating profile data.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from soc.modules.seeder.logic.seeder import logic as seeder_logic


# TODO: Should this go in it's own module?
class GSoCProfileHelper(object):
  """Helper class to aid in manipulating profile data.
  """

  def __init__(self, program):
    self.program = program
    self.user = None
    self.profile = None

  def createUser(self):
    """Creates a user entity for the current user.
    """
    if self.user:
      return
    from soc.models.user import User
    from soc.modules.seeder.logic.providers.user import CurrentUserProvider
    properties = {'account': CurrentUserProvider(), 'status': 'valid'}
    self.user = seeder_logic.seed(User, properties=properties)
    return self.user

  def createProfile(self):
    """Creates a profile for the current user.
    """
    if self.profile:
      return
    from soc.modules.gsoc.models.profile import GSoCProfile
    user = self.createUser()
    properties = {'link_id': user.link_id, 'user': user, 'parent': user,
                  'scope': self.program, 'student_info': None}
    self.profile = seeder_logic.seed(GSoCProfile, properties)

  def createStudent(self):
    """Sets the current suer to be a student for the current program.
    """
    self.createProfile()
    from soc.models.role import StudentInfo
    properties = {'key_name': self.profile.key().name(), 'parent': self.profile}
    self.profile.student_info = seeder_logic.seed(StudentInfo, properties)
    self.profile.put()

  def createStudentWithProposal(self):
    """Sets the current user to be a student with a proposal for the current program.
    """
    self.createStudent()
    from soc.modules.gsoc.models.student_proposal import StudentProposal
    properties = {'link_id': self.profile.link_id, 'scope': self.profile,
                  'parent': self.profile}
    seeder_logic.seed(StudentProposal, properties)

  def createStudentWithProject(self):
    """Sets the current user to be a student with a project for the current program.
    """
    self.createStudentWithProposal()
    from soc.modules.gsoc.models.student_project import StudentProject
    properties = {'link_id': self.profile.link_id, 'scope': self.profile,
                  'student': self.profile, 'parent': self.profile}
    seeder_logic.seed(StudentProject, properties)

  def createHost(self):
    """Sets the current user to be a host for the current program.
    """
    self.createUser()
    self.user.host_for = [self.program.scope.key()]
    self.user.put()

  def createOrgAdmin(self, org):
    """Creates an org admin profile for the current user.
    """
    self.createProfile()
    self.profile.org_admin_for = [org.key()]
    self.profile.put()

  def createMentor(self, org):
    """Creates an mentor profile for the current user.
    """
    self.createProfile()
    self.profile.mentor_for = [org.key()]
    self.profile.put()

  def createMentorWithProject(self, org):
    """Creates an mentor profile with a project for the current user.
    """
    self.createMentor(org)
    from soc.modules.gsoc.models.student_project import StudentProject
    properties = {'mentor': self.profile}
    seeder_logic.seed(StudentProject, properties)
