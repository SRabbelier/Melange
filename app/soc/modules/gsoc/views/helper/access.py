#!/usr/bin/env python2.5
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
    '"Daniel Hans <daniel.m.hans@gmail.com>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from django.utils.translation import ugettext

from soc.logic.models.host import logic as host_logic
from soc.views.helper import access
from soc.views import out_of_band

from soc.modules.gsoc.logic.models.mentor import logic as mentor_logic
from soc.modules.gsoc.logic.models.org_admin import logic as org_admin_logic
from soc.modules.gsoc.logic.models.student import logic as student_logic
from soc.modules.gsoc.logic.models.student_project import logic as student_project_logic
from soc.modules.gsoc.logic.models.student_proposal import logic as student_proposal_logic


DEF_SIGN_UP_AS_STUDENT_MSG = ugettext(
    'You need to sign up as a Student first.')

DEF_MAX_PROPOSALS_REACHED = ugettext(
    'You have reached the maximum number of Proposals allowed '
    'for this program.')

DEF_PROPOSAL_NOT_PUBLIC = ugettext(
    'The public view for proposal in request is not available.' 
    )

DEF_NOT_ALLOWED_PROJECT_FOR_SURVEY_MSG = ugettext(
    'You are not allowed to take this Survey for the specified Student'
    ' Project.')


class GSoCChecker(access.Checker):
  """See soc.views.helper.access.Checker.
  """

  @access.allowDeveloper
  def checkIsStudent(self, django_args, key_location, status):
    """Checks if the current user is the given student.

    Args:
      django_args: a dictionary with django's arguments
      key_location: the key for django_args in which the key_name
                    from the student is stored
      status: the allowed status for the student
    """

    self.checkIsUser(django_args)

    if 'seed' in django_args:
      key_name = django_args['seed'][key_location]
    else:
      key_name = django_args[key_location]

    student_entity = student_logic.getFromKeyName(key_name)

    if not student_entity or student_entity.status not in status:
      raise out_of_band.AccessViolation(
        message_fmt=DEF_SIGN_UP_AS_STUDENT_MSG)

    if student_entity.user.key() != self.user.key():
      # this is not the page for the current user
      self.deny(django_args)

    return

  @access.allowDeveloper
  def checkRoleAndStatusForStudentProposal(self, django_args, allowed_roles,
                                           role_status, proposal_status):
    """Checks if the current user has access to the given proposal.

    Args:
      django_args: a dictionary with django's arguments
      allowed_roles: list with names for the roles allowed to pass access check
      role_status: list with states allowed for the role
      proposal_status: a list with states allowed for the proposal

     Raises:
       AccessViolationResponse:
         - If there is no proposal found
         - If the proposal is not in one of the required states.
         - If the user does not have any ofe the required roles
    """

    self.checkIsUser(django_args)

    # bail out with 404 if no proposal is found
    proposal_entity = student_proposal_logic.getFromKeyFieldsOr404(django_args)

    if not proposal_entity.status in proposal_status:
      # this proposal can not be accessed at the moment
      raise out_of_band.AccessViolation(
          message_fmt=access.DEF_NO_ACTIVE_ENTITY_MSG)

    user_entity = self.user

    if 'proposer' in allowed_roles:
      # check if this proposal belongs to the current user
      student_entity = proposal_entity.scope
      if (user_entity.key() == student_entity.user.key()) and (
          student_entity.status in role_status):
        return

    filter = {'user': user_entity,
        'status': role_status}

    if 'host' in allowed_roles:
      # check if the current user is a host for this proposal's program
      filter['scope'] =  proposal_entity.program

      if host_logic.getForFields(filter, unique=True):
        return

    if 'org_admin' in allowed_roles:
      # check if the current user is an admin for this proposal's org
      filter['scope'] = proposal_entity.org

      if org_admin_logic.getForFields(filter, unique=True):
        return

    if 'mentor' in allowed_roles:
      # check if the current user is a mentor for this proposal's org
      filter['scope'] = proposal_entity.org

      if mentor_logic.getForFields(filter, unique=True):
        return

    # no roles found, access denied
    raise out_of_band.AccessViolation(
        message_fmt=access.DEF_NEED_ROLE_MSG)

  @access.allowDeveloper
  def checkCanStudentPropose(self, django_args, key_location, check_limit):
    """Checks if the program for this student accepts proposals.

    Args:
      django_args: a dictionary with django's arguments
      key_location: the key for django_args in which the key_name
                    from the student is stored
      check_limit: iff true checks if the student reached the apps_tasks_limit
                   for the given program.
    """

    from soc.logic.helper import timeline as timeline_helper

    self.checkIsUser(django_args)

    if django_args.get('seed'):
      key_name = django_args['seed'][key_location]
    else:
      key_name = django_args[key_location]

    student_entity = student_logic.getFromKeyName(key_name)

    if not student_entity or student_entity.status == 'invalid':
      raise out_of_band.AccessViolation(
        message_fmt=DEF_SIGN_UP_AS_STUDENT_MSG)

    program_entity = student_entity.scope

    if not timeline_helper.isActivePeriod(program_entity.timeline,
                                          'student_signup'):
      raise out_of_band.AccessViolation(message_fmt=access.DEF_PAGE_INACTIVE_MSG)

    if check_limit:
      # count all studentproposals by the student
      fields = {'scope': student_entity}
      proposal_query = student_proposal_logic.getQueryForFields(fields)

      if proposal_query.count() >= program_entity.apps_tasks_limit:
        # too many proposals access denied
        raise out_of_band.AccessViolation(message_fmt=DEF_MAX_PROPOSALS_REACHED)

    return

  @access.allowDeveloper
  def checkStudentProjectHasStatus(self, django_args, allowed_status):
    """Checks whether the Project has one of the given statuses.

    Args:
      django_args: a dictionary with django's arguments
      allowed_status: list with the allowed statuses for the entity

     Raises:
       AccessViolationResponse:
         - If there is no project found
         - If the project is not in the requested status
    """

    project_entity = student_project_logic.getFromKeyFieldsOr404(django_args)

    if not project_entity.status in allowed_status:
      raise out_of_band.AccessViolation(
          message_fmt=access.DEF_NO_ACTIVE_ENTITY_MSG)

    return

  @access.allowDeveloper
  def checkCanEditStudentProjectAsStudent(self, django_args):
    """Checks whether the project can be edited in a student mode
    by the current user.

    Args:
      django_args: a dictionary with django's arguments

     Raises:
       AccessViolationResponse:
         - If there is no project found
         - If the project does not belong to the current user
    """

    self.checkIsUser()

    project_entity = student_project_logic.getFromKeyFieldsOr404(django_args)
    student_entity = project_entity.student

    if student_entity.user.key() != self.user.key():
      raise out_of_band.AccessViolation(
          message_fmt=access.DEF_NOT_YOUR_ENTITY_MSG)

    if student_entity.status != 'active':
      raise out_of_band.AccessViolation(
          message_fmt=access.DEF_NO_ACTIVE_ENTITY_MSG)

    return

  @access.allowDeveloper
  def checkIsStudentProposalPubliclyVisible(self, django_args):
    """Checks whether the proposal's content can be seen by everyone.
    
    Args:
      django_args: a dictionary with django's arguments

    Raises:
      AccessViolationResponse:
        - If there is no proposal found
        - If the proposal cannot be publicly seen
    """

    proposal_entity = student_proposal_logic.getFromKeyFieldsOr404(django_args)

    user = self.user
    proposal_owner = proposal_entity.scope.user.key().id_or_name()

    # student may see his own proposal even if public view is not available
    if user and user.key().id_or_name() == proposal_owner:
      return 

    if not proposal_entity.is_publicly_visible:
      raise out_of_band.AccessViolation(
          message_fmt=DEF_PROPOSAL_NOT_PUBLIC)

    return

  @access.allowDeveloper
  def checkIsHostForStudentProject(self, django_args):
    """Checks whether the user is Host for the Program of the
    specified StudentProject.

    Args:
      django_args: a dictionary with django's arguments

     Raises:
       AccessViolationResponse:
         - If there is no project found
         - If the user is not a host for the specified project
    """

    self.checkIsUser()

    project_entity = student_project_logic.getFromKeyFieldsOr404(django_args)
    program_entity = project_entity.program

    new_args = {'scope_path': program_entity.scope_path}
    self.checkHasRoleForScope(new_args, host_logic)

    return

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
        role_entity.status in ['active', 'inactive']):
      # this user has the role required
      return

    fields = {'user': user_entity,
              'scope': record_entity.org,
              'status': ['active','inactive']}
    admin_entity = org_admin_logic.getForFields(fields, unique=True)

    if admin_entity:
      # this user is org admin for the retrieved record's project
      return

    # The current user is no Org Admin, has not taken the Survey and is not
    # the one responsible for taking this survey.
    raise out_of_band.AccessViolation(message_fmt=access.DEF_NOT_YOUR_RECORD)

