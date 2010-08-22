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

"""GHOP specific views for Organization Mentors.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>'
  ]


from django.utils import simplejson
from django.utils.translation import ugettext

from soc.logic import dicts
from soc.logic.helper import timeline as timeline_helper
from soc.logic.models import user as user_logic
from soc.views import out_of_band
from soc.views.helper import decorators
from soc.views.helper import lists
from soc.views.helper import responses
from soc.views.models import mentor

from soc.modules.ghop.logic.models import mentor as ghop_mentor_logic
from soc.modules.ghop.logic.models import organization as ghop_org_logic
from soc.modules.ghop.logic.models import org_admin as ghop_org_admin_logic
from soc.modules.ghop.logic.models import student as ghop_student_logic
from soc.modules.ghop.logic.models import task as ghop_task_logic
from soc.modules.ghop.views.helper import access as ghop_access
from soc.modules.ghop.views.models import organization as ghop_org_view
from soc.modules.ghop.views.models import task as ghop_task_view

import soc.modules.ghop.logic.models.mentor


class View(mentor.View):
  """View methods for the GHOP Mentor model.
  """

  DEF_NO_TASKS_MSG = ugettext(
      'There are no tasks affiliated to you.')

  DEF_PAGE_INACTIVE_MSG = ugettext(
    'This page is inactive at this time.')

  DEF_MENTOR_TASKS_MSG_FMT = ugettext('Tasks I am mentoring for %s.')

  def __init__(self, params=None):
    """Defines the fields and methods required for the mentor View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = ghop_access.GHOPChecker(params)
    rights['create'] = ['checkIsDeveloper']
    rights['edit'] = [('checkIsMyActiveRole', ghop_mentor_logic.logic)]
    rights['delete'] = ['checkIsDeveloper']
    rights['invite'] = [('checkHasRoleForScope',
                         ghop_org_admin_logic.logic)]
    rights['accept_invite'] = [
        ('checkIsMyRequestWithStatus', [['group_accepted']]),
        ('checkIsNotStudentForProgramOfOrgInRequest',
         [ghop_org_logic.logic, ghop_student_logic.logic])]
    rights['request'] = [
        ('checkIsNotStudentForProgramOfOrg',
         [ghop_org_logic.logic, ghop_student_logic.logic]),
        ('checkCanMakeRequestToGroup', ghop_org_logic.logic)]
    rights['process_request'] = [
        ('checkCanProcessRequest', [[ghop_org_admin_logic.logic]])]
    rights['manage'] = [
        ('checkIsAllowedToManageRole', [ghop_mentor_logic.logic,
                                        ghop_org_admin_logic.logic])]
    rights['list_mentor_tasks'] = [
        ('checkCanOpenTaskList', [ghop_mentor_logic.logic, 'ghop/mentor'])]

    new_params = {}
    new_params['logic'] = soc.modules.ghop.logic.models.mentor.logic
    new_params['group_logic'] = ghop_org_logic.logic
    new_params['group_view'] = ghop_org_view.view
    new_params['rights'] = rights

    new_params['scope_view'] = ghop_org_view

    new_params['name'] = "GHOP Mentor"
    new_params['module_name'] = "mentor"
    new_params['sidebar_grouping'] = 'Organizations'

    new_params['module_package'] = 'soc.modules.ghop.views.models'
    new_params['url_name'] = 'ghop/mentor'

    new_params['role'] = 'ghop/mentor'

    patterns = []
    patterns += [
        (r'^%(url_name)s/(?P<access_type>list_mentor_tasks)/%(key_fields)s$',
        '%(module_package)s.%(module_name)s.list_mentor_tasks',
        'List Mentor tasks')]

    new_params['extra_django_patterns'] = patterns

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params=params)

  def getListMentorTasksData(self, request, params, filter):
    """Returns the list data for Organization Tasks list.

    Args:
      request: HTTPRequest object
      params: params of the task entity for the list
      filter: properties on which the tasks must be listed
    """

    idx = request.GET.get('idx', '')
    idx = int(idx) if idx.isdigit() else -1

    # default list settings
    args = []
    order = ['modified_on']
    visibility = 'public'

    if idx == 0:
      contents = lists.getListData(request, params, filter,
                                   visibility=visibility,
                                   order=order, args=args)
    else:
      return responses.jsonErrorResponse(request, "idx not valid")

    json = simplejson.dumps(contents)

    return responses.jsonResponse(request, json)

  @decorators.merge_params
  @decorators.check_access
  def listMentorTasks(self, request, access_type, page_name=None,
                      params=None, **kwargs):
    """Displays a list of all tasks for a given student.

    See base.View.list() for more details.
    """

    entity = self._params['logic'].getFromKeyFieldsOr404(kwargs)

    # obtain program entity based on request params
    program = entity.program

    # this check is performed here and not as part of access
    # checks for this method because the scope for mentor entity
    # is organization and not program so checkIsAfterEvent access
    # check method cannot be used
    if not timeline_helper.isAfterEvent(
        program.timeline, 'accepted_organization_announced_deadline'):
      raise out_of_band.Error(self.DEF_PAGE_INACTIVE_MSG)

    user_account = user_logic.logic.getForCurrentAccount()

    filter = {
        'user': user_account,
        'program': program,
        'status': 'active'
        }
    mentor_entity = self._params['logic'].getForFields(filter, unique=True)

    list_params = ghop_task_view.view.getParams().copy()

    list_params['list_description'] = self.DEF_MENTOR_TASKS_MSG_FMT % (
          program.name)

    filter = {
        'program': program,
        'mentors': [mentor_entity],
        'status': ['Unapproved', 'Unpublished', 'Open', 'Reopened',
                   'ClaimRequested', 'Claimed', 'ActionNeeded', 'Closed',
                   'AwaitingRegistration', 'NeedsWork', 'NeedsReview']
        }

    if request.GET.get('fmt') == 'json':
        return self.getListMentorTasksData(request, list_params,
                                           filter)

    tasks = ghop_task_logic.logic.getForFields(filter=filter, unique=True)

    contents = []

    if tasks:
      tasks_list = lists.getListGenerator(request, list_params, idx=0)
      contents.append(tasks_list)

    if contents:
      return self._list(request, list_params, contents, page_name)
    else:
      raise out_of_band.Error(self.DEF_NO_TASKS_MSG)


view = View()

accept_invite = decorators.view(view.acceptInvite)
admin = decorators.view(view.admin)
create = decorators.view(view.create)
delete = decorators.view(view.delete)
edit = decorators.view(view.edit)
invite = decorators.view(view.invite)
list = decorators.view(view.list)
list_mentor_tasks = decorators.view(view.listMentorTasks)
manage = decorators.view(view.manage)
process_request = decorators.view(view.processRequest)
role_request = decorators.view(view.request)
public = decorators.view(view.public)
export = decorators.view(view.export)
pick = decorators.view(view.pick)
