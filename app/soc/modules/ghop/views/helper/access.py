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

from soc.modules.ghop.logic.models import mentor as ghop_mentor_logic
from soc.modules.ghop.logic.models import org_admin as ghop_org_admin_logic
from soc.modules.ghop.logic.models import program as ghop_program_logic
from soc.modules.ghop.logic.models.student import logic as ghop_student_logic
from soc.modules.ghop.logic.models import task as ghop_task_logic


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

DEF_NO_PUB_TASK_MSG = ugettext(
    'There is no such published task.')

DEF_PAGE_INACTIVE_MSG = ugettext(
    'This page is inactive at this time.')

DEF_SIGN_UP_AS_OA_MENTOR_MSG = ugettext(
    'You first need to sign up as an Org Admin or a Mentor.')

DEF_NO_TASKS_ASSIGNED = ugettext(
    'There are no tasks which have been assigned to you.')


class GHOPChecker(access.Checker):
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
      django_args: a dictionary with django's arguments
      key_location: the key for django_args in which the key_name
                    from the mentor is stored
      check_limit: iff true checks if the organization reached the
                   task quota limit for the given program.
    """

    self.checkIsUser(django_args)

    user_account = user_logic.logic.getForCurrentAccount()

    filter = {
        'user': user_account,
        'scope_path': django_args[key_location],
        'status': 'active'
        }

    role_entity = ghop_org_admin_logic.logic.getForFields(filter, unique=True)
    if not role_entity:
      role_entity = ghop_mentor_logic.logic.getForFields(filter, unique=True)

    if not role_entity:
      raise out_of_band.AccessViolation(
          message_fmt=DEF_SIGN_UP_AS_OA_MENTOR_MSG)

    # pylint: disable-msg=E1103
    program_entity = role_entity.program

    if not timeline_helper.isActivePeriod(program_entity.timeline, 'program'):
      raise out_of_band.AccessViolation(message_fmt=DEF_PAGE_INACTIVE_MSG)

    # pylint: disable-msg=E1103
    org_entity = role_entity.scope

    if check_limit:
      # count all tasks from this organization
      fields = {'scope': org_entity}
      task_query = ghop_task_logic.logic.getQueryForFields(fields)

      if task_query.count() >= org_entity.task_quota_limit:
        # too many tasks access denied
        raise out_of_band.AccessViolation(
            message_fmt=DEF_MAX_TASKS_REACHED_MSG)

    if 'link_id' in django_args:
      task_entity = ghop_task_logic.logic.getFromKeyFieldsOr404(django_args)

      if task_entity.status not in ['Unapproved', 'Unpublished', 'Open']:
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
      task_entity = ghop_task_logic.logic.getFromKeyFieldsOr404(django_args)

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

    if 'ghop/org_admin' in allowed_roles:
      # check if the current user is an admin for this task's org
      if ghop_org_admin_logic.logic.getForFields(filter, unique=True):
        return

    if 'ghop/mentor' in allowed_roles:
      # check if the current user is a mentor for this task's org
      if ghop_mentor_logic.logic.getForFields(filter, unique=True):
        return

    if 'public' in allowed_roles:
      return

    # no roles found, access denied
    raise out_of_band.AccessViolation(message_fmt=DEF_NEED_ROLE_MSG)

  def checkStatusForTask(self, django_args):
    """Checks if the current user has access to the given task.

    This method checks if the current user is either an GHOP Org Admin or a
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

    self.checkIsUser(django_args)

    try:
      user_entity = self.user

      filter = {
          'user': user_entity,
          'status': 'active',
          'scope_path': django_args['scope_path'],
          }

      if ghop_org_admin_logic.logic.getForFields(filter, unique=True):
        return

      if ghop_mentor_logic.logic.getForFields(filter, unique=True):
        return

    except out_of_band.Error:
      pass

    program_entity = ghop_program_logic.logic.getFromKeyNameOr404(
        django_args['scope_path'])

    if not timeline_helper.isAfterEvent(program_entity.timeline,
        'tasks_publicly_visible'):
      raise out_of_band.AccessViolation(message_fmt=DEF_PAGE_INACTIVE_MSG)

    # bail out with 404 if no task is found
    task_entity = ghop_task_logic.logic.getFromKeyFieldsOr404(django_args)

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

    program_entity = ghop_program_logic.logic.getFromKeyNameOr404(
        django_args['scope_path'])

    filter = {
        'user': self.user,
        'program': program_entity,
        'status': 'AwaitingRegistration',
        }

    if ghop_task_logic.logic.getForFields(filter, unique=True):
      return

    # no completed tasks found, access denied
    raise out_of_band.AccessViolation(
        message_fmt=DEF_CANT_REGISTER)

  def checkCanOpenTaskList(self, django_args):
    """Checks if the current user is allowed to see a list of his tasks.

    Args:
      django_args: a dictionary with django's arguments

    Raises:
      AccessViolationResponse:
        - if the user is not registered as a student; and
        - if the user has not claimed a single task
    """

    self.checkIsUser(django_args)

    try:
      return self.checkHasRoleForScope(django_args, ghop_student_logic)
    except out_of_band.Error:
      pass

    program = ghop_program_logic.logic.getFromKeyNameOr404(
        django_args['scope_path'])

    filter = {
        'user': self.user,
        'program': program,
        }

    if not ghop_task_logic.logic.getForFields(filter, unique=True):
      raise out_of_band.AccessViolation(message_fmt=DEF_NO_TASKS_ASSIGNED)
