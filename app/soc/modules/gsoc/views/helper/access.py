#!/usr/bin/python2.5
#
# Copyright 2009 the Melange authors.
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

"""Access control helper.

See soc.views.helper.access module.
"""

__authors__ = [
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from django.utils.translation import ugettext

from soc.logic.models.student_project import logic as student_project_logic
from soc.views import out_of_band
from soc.views.helper import access

from soc.modules.gsoc.logic.models.org_admin import logic as org_admin_logic


DEF_NOT_ALLOWED_PROJECT_FOR_SURVEY_MSG = ugettext(
    'You are not allowed to take this Survey for the specified Student'
    ' Project.')


class GSoCChecker(access.Checker):
  """See soc.views.helper.access.Checker.
  """

  @access.denySidebar
  @access.allowDeveloper
  def checkIsAllowedToTakeProjectSurveyAs(self, django_args, survey_logic,
                                          role_name, project_key_location):
    """Checks whether a ProjectSurvey can be taken by the current User.

    role_name argument determines wether the current user is taking the survey
    as a student or mentor specified by the project in GET dict.

    If the survey is taken as a mentor, org admins for the Organization in
    which the project resides will also have access.

    However if the project entry is not present in the dictionary this access
    check passes.

    Args:
      django_args: a dictionary with django's arguments
      survey_logic: instance of ProjectSurveyLogic (or subclass)
      role_name: String containing either "student" or "mentor"
      project_key_location: String containing the key entry in the GET dict
        where the key for the project can be located.
    """

    if not role_name in ['mentor', 'student']:
      raise InvalidArgumentError('role_name is not mentor or student')

    # check if the current user is signed up
    self.checkIsUser(django_args)
    user_entity = self.user

    # get the project keyname from the GET dictionary
    get_dict = django_args['GET']
    key_name = get_dict.get(project_key_location)

    if not key_name:
      # no key name present so no need to deny access
      return

    # retrieve the Student Project for the key
    project_entity = student_project_logic.getFromKeyNameOr404(key_name)

    # check if a survey can be conducted about this project
    if project_entity.status != 'accepted':
      raise out_of_band.AccessViolation(
          message_fmt=DEF_NOT_ALLOWED_PROJECT_FOR_SURVEY_MSG)

    # get the correct role depending on the role_name
    if role_name == 'student':
      role_entity = project_entity.student
    elif role_name == 'mentor':
      role_entity = project_entity.mentor

    # check if the role matches the current user
    if role_entity.user.key() != user_entity.key() and (
        role_entity.status == 'active'):
      if role_name == 'student':
        raise out_of_band.AccessViolation(
            message_fmt=DEF_NOT_ALLOWED_PROJECT_FOR_SURVEY_MSG)
      elif role_name == 'mentor':
        # check if the current user is an Org Admin for this Student Project
        fields = {'user': user_entity,
                  'scope': project_entity.scope,
                  'status': 'active'}
        admin_entity = org_admin_logic.getForFields(fields, unique=True)
        if not admin_entity:
          # this user is no Org Admin or Mentor for this project
          raise out_of_band.AccessViolation(
              message_fmt=DEF_NOT_ALLOWED_PROJECT_FOR_SURVEY_MSG)
    elif role_entity.status != 'active':
      # this role is not active
      raise out_of_band.AccessViolation(message_fmt=access.DEF_NEED_ROLE_MSG)

    return

  @access.denySidebar
  @access.allowDeveloper
  def checkIsAllowedToViewProjectSurveyRecordAs(
      self, django_args, survey_logic, role_name, record_key_location):
    """Checks whether the current user is allowed to view the record given in
    the GET data by the record_key_location.

    Args:
      django_args: a dictionary with django's arguments
      survey_logic: Survey Logic instance that belongs to the SurveyRecord
        type in question
      role_name: string containing either "student" or "mentor". Determines
        which of the roles the within the project the current user should have
        to view the evaluation results.
      record_key_location: string containing the name of the GET param which
        contains the id for the SurveyRecord to retrieve

    Raises:
      AccessViolation if:
        - No valid numeric Record ID is given in the POST data.
        - No Record could be retrieved for the given Record ID.
        - The current user has not taken the survey, is not the Student/Mentor
          (depending on the role_name) and is not an Org Admin for the project
          to which the SurveyRecord belongs.
    """

    if not role_name in ['mentor', 'student']:
      raise InvalidArgumentError('role_name is not mentor or student')

    self.checkIsUser(django_args)
    user_entity = self.user

    get_dict = django_args['GET']
    record_id = get_dict.get(record_key_location)

    if not record_id or not record_id.isdigit():
      raise out_of_band.AccessViolation(
          message_fmt=access.DEF_NO_VALID_RECORD_ID)
    else:
      record_id = int(record_id)

    record_logic = survey_logic.getRecordLogic()
    record_entity = record_logic.getFromIDOr404(record_id)

    if record_entity.user.key() == user_entity.key():
      # this record belongs to the current user
      return

    if role_name == 'student':
      role_entity = record_entity.project.student
    elif role_name == 'mentor':
      role_entity = record_entity.project.mentor

    if role_entity.user.key() == user_entity.key() and (
        role_entity.status == 'active'):
      # this user has the role required
      return

    fields = {'user': user_entity,
              'scope': record_entity.org,
              'status': 'active'}
    admin_entity = org_admin_logic.getForFields(fields, unique=True)

    if admin_entity:
      # this user is org admin for the retrieved record's project
      return

    # The current user is no Org Admin, has not taken the Survey and is not
    # the one responsible for taking this survey.
    raise out_of_band.AccessViolation(message_fmt=DEF_NOT_YOUR_RECORD)

