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
    '"Madhusudan.C.S" <madhusudancs@gmail.com>',
    '"Daniel Hans" <daniel.m.hans@gmail.com>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
    '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


from django.utils.translation import ugettext

from soc.logic.helper import timeline as timeline_helper
from soc.logic.models import host as host_logic
from soc.logic.models import user as user_logic
from soc.views import out_of_band
from soc.views.helper import access

from soc.modules.gci.logic.models import mentor as gci_mentor_logic
from soc.modules.gci.logic.models import organization as gci_org_logic
from soc.modules.gci.logic.models import org_admin as gci_org_admin_logic
from soc.modules.gci.logic.models import program as gci_program_logic
from soc.modules.gci.logic.models import task as gci_task_logic


DEF_ALREADY_CLAIMED_A_TASK = ugettext(
    'You have already claimed a task and can therefore not become a mentor '
    'or org admin.')

DEF_CANT_EDIT_MSG = ugettext(
    'This task cannot be edited since it has been claimed at least '
    'once before.')

DEF_CANT_REGISTER = ugettext(
    'You have not completed your first task to register as a student. ')

DEF_MAX_TASKS_REACHED_MSG = ugettext(
    'You have reached the maximum number of Tasks allowed '
    'for your organization for this program.')

DEF_NEED_ROLE_MSG = ugettext(
    'You do not have the required role.')

DEF_NO_ACTIVE_ENTITY_MSG = ugettext(
    'There is no such active entity.')

DEF_NO_FILE_ACCESS_MSG = ugettext(
    'You do not have the necessary privileges to access this file.')

DEF_NO_FILE_SPECIFIED_MSG = ugettext(
    'File to download is not specified')

DEF_NO_PUB_TASK_MSG = ugettext(
    'There is no such published task.')

DEF_PAGE_INACTIVE_MSG = ugettext(
    'This page is inactive at this time.')

DEF_SIGN_UP_AS_OA_MENTOR_MSG = ugettext(
    'You first need to sign up as an Org Admin or a Mentor.')

DEF_NO_TASKS_AFFILIATED = ugettext(
    'There are no tasks affiliated to you.')

DEF_UNEXPECTED_ERROR = ugettext(
    'An unexpected error occurred please file an issue report, make sure you '
    'note the URL.')

DEF_ORG_HAS_TASKS = ugettext(
    'The organization has at least one task which may be claimed.')

class GCIChecker(access.Checker):
  """See soc.views.helper.access.Checker.
  """

  @access.allowDeveloper
  @access.denySidebar
  def checkCanOrgAdminOrMentorEdit(self, django_args,
                                   key_location, check_limit):
    """Checks if the mentors can create task for this program,
    and obeys the task quota limit assigned for their org when check_limit is
    True.

    Args:
      django_args: a dictionary with django's arguments.
      key_location: the key for django_args in which the key_name
                    of the org is stored.
      check_limit: iff true checks if the organization reached the
                   task quota limit for the given program.
    """

    import settings

    self.checkIsUser(django_args)

    user_account = user_logic.logic.getCurrentUser()

    if key_location not in django_args:
      raise out_of_band.AccessViolation(
          message_fmt=DEF_NEED_ROLE_MSG)

    filter = {
        'user': user_account,
        'scope_path': django_args[key_location],
        'status': 'active'
        }

    role_entity = gci_org_admin_logic.logic.getForFields(filter, unique=True)
    if not role_entity:
      role_entity = gci_mentor_logic.logic.getForFields(filter, unique=True)

    if not role_entity:
      raise out_of_band.AccessViolation(
          message_fmt=DEF_SIGN_UP_AS_OA_MENTOR_MSG)

    # pylint: disable=E1103
    program_entity = role_entity.program

    if not timeline_helper.isActivePeriod(program_entity.timeline, 'program'):
      raise out_of_band.AccessViolation(message_fmt=DEF_PAGE_INACTIVE_MSG)

    # pylint: disable=E1103
    org_entity = role_entity.scope

    if settings.GCI_TASK_QUOTA_LIMIT_ENABLED and check_limit:
      # count all tasks from this organization
      fields = {'scope': org_entity}
      task_query = gci_task_logic.logic.getQueryForFields(fields)

      if task_query.count() >= org_entity.task_quota_limit:
        # too many tasks access denied
        raise out_of_band.AccessViolation(
            message_fmt=DEF_MAX_TASKS_REACHED_MSG)

    if 'link_id' in django_args:
      task_entity = gci_task_logic.logic.getFromKeyFieldsOr404(django_args)

      if task_entity.status not in ['Unapproved', 'Unpublished', 'Open',
                                    'ClaimRequested', 'Reopened']:
        # task is claimed at least once
        raise out_of_band.AccessViolation(message_fmt=DEF_CANT_EDIT_MSG)

    return

  @access.allowDeveloper
  @access.denySidebar
  def checkRoleAndStatusForTask(self, django_args, allowed_roles,
                                role_status, task_status):
    """Checks if the current user has access to the given task.

    This method checks if the current user is in one of the allowed_roles
    and has specified role_status, If yes, allows him to access the Task page.

    Args:
      django_args: a dictionary with django's arguments
      allowed_roles: list with names for the roles allowed to pass access check
      role_status: list with states allowed for the role
      task_status: a list with states allowed for the task

     Raises:
       AccessViolationResponse:
         - If there is no task found
         - If the task is not in one of the required states.
         - If the user does not have any of the required roles
    """

    self.checkIsUser(django_args)

    if 'link_id' in django_args:
      # bail out with 404 if no task is found
      task_entity = gci_task_logic.logic.getFromKeyFieldsOr404(django_args)

      if not task_entity.status in task_status:
        # this task can not be accessed at the moment
        raise out_of_band.AccessViolation(
            message_fmt=DEF_NO_ACTIVE_ENTITY_MSG)

    user_entity = self.user

    filter = {
        'user': user_entity,
        'scope_path': django_args['scope_path'],
        'status': role_status
        }

    if 'host' in allowed_roles:
      # check if the current user is a host for this proposal's program
      if host_logic.logic.getForFields(filter, unique=True):
        return

    if 'gci/org_admin' in allowed_roles:
      # check if the current user is an admin for this task's org
      if gci_org_admin_logic.logic.getForFields(filter, unique=True):
        return

    if 'gci/mentor' in allowed_roles:
      # check if the current user is a mentor for this task's org
      if gci_mentor_logic.logic.getForFields(filter, unique=True):
        return

    if 'public' in allowed_roles:
      return

    # no roles found, access denied
    raise out_of_band.AccessViolation(message_fmt=DEF_NEED_ROLE_MSG)

  @access.allowDeveloper
  @access.denySidebar
  def checkStatusForTask(self, django_args):
    """Checks if the current user has access to the given task.

    This method checks if the current user is either an GCI Org Admin or a
    Mentor and is active, if yes it allows them to view the task page at any
    task state. If the user is none of the above, it checks the status of the
    task, and if it is in one of the valid published states it allows access
    to view the task page.

    Args:
      django_args: a dictionary with django's arguments

    Raises:
      AccessViolationResponse:
        - If there is no task found
        - If the task is not in one of the required states.
    """

    user_entity = self.user

    # bail out with 404 if no task is found
    task_entity = gci_task_logic.logic.getFromKeyFieldsOr404(django_args)

    if (user_entity and task_entity.user and
        task_entity.user.key() == user_entity.key()):
      return

    filter = {
        'user': user_entity,
        'status': 'active',
        }

    if host_logic.logic.getForFields(filter, unique=True):
      return

    filter['scope_path'] = django_args['scope_path']

    if gci_org_admin_logic.logic.getForFields(filter, unique=True):
      return

    if gci_mentor_logic.logic.getForFields(filter, unique=True):
      return

    org_entity = gci_org_logic.logic.getFromKeyNameOr404(
        django_args['scope_path'])

    if not timeline_helper.isAfterEvent(org_entity.scope.timeline,
        'tasks_publicly_visible'):
      raise out_of_band.AccessViolation(message_fmt=DEF_PAGE_INACTIVE_MSG)

    if task_entity.status in ['Unapproved', 'Unpublished', 'Invalid']:
      # this proposal can not be task at the moment
      raise out_of_band.AccessViolation(
          message_fmt=DEF_NO_PUB_TASK_MSG)

  def checkCanApply(self, django_args):
    """Checks if the user has the completed at least one task to register as
    a student.

    Args:
      django_args: a dictionary with django's arguments

     Raises:
       AccessViolationResponse:
         - If student has not completed even a single task
    """

    self.checkIsUser(django_args)

    program_entity = gci_program_logic.logic.getFromKeyNameOr404(
        django_args['scope_path'])

    filter = {
        'user': self.user,
        'program': program_entity,
        'status': 'AwaitingRegistration',
        }

    if gci_task_logic.logic.getForFields(filter, unique=True):
      return

    # no completed tasks found, access denied
    raise out_of_band.AccessViolation(
        message_fmt=DEF_CANT_REGISTER)

  def checkCanOpenTaskList(self, django_args, role_logic, role):
    """Checks if the current user is allowed to see a list of his tasks.

    Args:
      django_args: a dictionary with django's arguments
      role_logic: the specific role whose logic must be used to check
                  for the scope
      role: name of the role for this check is performed

    Raises:
      AccessViolationResponse:
        - if the user is not registered as a student; and
        - if the user has not claimed a single task
    """

    self.checkIsUser(django_args)

    try:
      return self.checkHasRoleForScope(django_args, role_logic)
    except out_of_band.Error:
      pass

    program = gci_program_logic.logic.getFromKeyNameOr404(
        django_args['scope_path'])

    filter = {
        'program': program,
        }

    if role == 'gci/student':
      filter['user'] = self.user
    elif role == 'gci/mentor':
      mentor_filter = {
          'user': self.user,
          'program': program,
          'status': 'active'
          }
      mentor_entity = role_logic.getForFields(mentor_filter, unique=True)
      filter['mentors'] = [mentor_entity]

    if not gci_task_logic.logic.getForFields(filter, unique=True):
      raise out_of_band.AccessViolation(message_fmt=DEF_NO_TASKS_AFFILIATED)

  def checkTimelineFromTaskScope(self, django_args, status, period_name):
    """Checks the timeline for the program found in the scope variable of a
    Task.

    Args:
      django_args: a dictionary with django's arguments
      status: one of three strings, during which calls isActivePeriod(),
              before which calls isBeforeEvent() and after which calls
              isAfterEvent().
      period_name: the name of the period to check the timeline for.

    Raises:
      AccessViolationResponse:
        - if the program is not in a valid state
        - if the period specified does not pass the required status check
    """

    org_entity = gci_org_logic.logic.getFromKeyNameOr404(
        django_args['scope_path'])

    program_args = {'scope_path': org_entity.scope_path}

    if status is 'during':
      return self.checkIsActivePeriod(program_args, period_name,
                                      'scope_path', gci_program_logic.logic)
    elif status is 'before':
      return self.checkIsBeforeEvent(program_args, period_name,
                                     'scope_path', gci_program_logic.logic)
    elif status is 'after':
      return self.checkIsAfterEvent(program_args, period_name,
                                    'scope_path', gci_program_logic.logic)
    # no right status set, but we can't give the user access
    raise out_of_band.AccessViolation(message_fmt=DEF_UNEXPECTED_ERROR)


  def checkIsNotStudentForProgramOfOrg(self, django_args, org_logic,
                                       student_logic):
    """Extends the basic with one that checks whether the current user has
    claimed a task in the program.

    Args:
        See Checker.checkIsNotStudentForProgramOfOrg().
    """
    org_entity = super(GCIChecker, self).checkIsNotStudentForProgramOfOrg(
        django_args, org_logic, student_logic)

    fields = {
        'user': self.user,
        'program': org_entity.scope
        }
    if gci_task_logic.logic.getForFields(fields, unique=True):
      raise out_of_band.AccessViolation(message_fmt=DEF_ALREADY_CLAIMED_A_TASK)

    return org_entity

  @access.allowDeveloper
  def checkOrgHasNoOpenTasks(self, django_args):
    """Checks if the organization does not have any tasks which might be 
    claimed by students.
    """

    org_entity = gci_org_logic.logic.getFromKeyFieldsOr404(django_args)

    fields = {
        'status': ['Open', 'Reopened'],
        'scope': org_entity
        }
    if gci_task_logic.logic.getForFields(fields, unique=True):
      raise out_of_band.AccessViolation(message_fmt=DEF_ORG_HAS_TASKS)

  @access.allowDeveloper
  @access.denySidebar
  def checkCanDownloadConsentForms(self, django_args, student_logic,
                                   forms_data):
    """Checks if the user is a student who can download the forms i.e.
    the blobs he has requested.

    Args:
      django_args: a dictionary with django's arguments
      student_logic: student logic used to look up student entity
      forms_data: dictionary containing the data related to the forms
          that student should upload and entities that store the form.

    Raises:
      AccessViolationResponse:
        - If there are no forms uploaded for the student.
        - If the logged in user is not the one to whom the form belongs to.
    """

    self.checkIsUser(django_args)

    user_entity = self.user

    try:
      # if the current user is the program host no more access is required
      if self.checkIsHostForProgramInScope(
          django_args, gci_program_logic.logic):
        return
    except out_of_band.AccessViolation:
      # if the user is not the host proceed for other checks
      # NOTE: This is not combined with the following exception because
      # if we catch AccessViolation there the access check for blob key
      # being null which raises the same exception will also be caught
      pass

    filter = {
          'user': user_entity,
          'status': 'active',
          'scope_path': django_args['scope_path'],
          'link_id': django_args['link_id'],
          }

    student_entity = student_logic.getForFields(filter, unique=True)

    try:
      form_type = django_args['GET'].get('type', '')
      blob_key = django_args['GET'].get('key', '')

      if not blob_key:
        raise out_of_band.AccessViolation(
            message_fmt=DEF_NO_FILE_SPECIFIED_MSG)

      form_entity_name = forms_data.get(form_type, '')
      form_entity = getattr(student_entity, form_entity_name)
      if blob_key == str(form_entity.key()):
        return

    except AttributeError:
      pass

    raise out_of_band.AccessViolation(message_fmt=DEF_NO_FILE_ACCESS_MSG)
