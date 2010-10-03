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

"""GCI specific views for Organization Mentors.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>'
  ]


from django.utils import simplejson
from django.utils.translation import ugettext

from soc.logic import dicts
from soc.logic.models import user as user_logic
from soc.views import out_of_band
from soc.views.helper import decorators
from soc.views.helper import lists
from soc.views.helper import responses
from soc.views.models import mentor

from soc.modules.gci.logic.models import mentor as gci_mentor_logic
from soc.modules.gci.logic.models import organization as gci_org_logic
from soc.modules.gci.logic.models import org_admin as gci_org_admin_logic
from soc.modules.gci.logic.models import program as gci_program_logic
from soc.modules.gci.logic.models import student as gci_student_logic
from soc.modules.gci.logic.models import task as gci_task_logic
from soc.modules.gci.views.helper import access as gci_access
from soc.modules.gci.views.models import organization as gci_org_view
from soc.modules.gci.views.models import task as gci_task_view

import soc.modules.gci.logic.models.mentor


class View(mentor.View):
  """View methods for the GCI Mentor model.
  """

  DEF_NO_TASKS_MSG = ugettext(
      'There are no tasks affiliated to you.')

  DEF_MENTOR_TASKS_MSG_FMT = ugettext('Tasks I am mentoring for %s.')

  def __init__(self, params=None):
    """Defines the fields and methods required for the mentor View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = gci_access.GCIChecker(params)
    rights['create'] = ['checkIsDeveloper']
    rights['edit'] = [('checkIsMyActiveRole', gci_mentor_logic.logic)]
    rights['delete'] = ['checkIsDeveloper']
    rights['invite'] = [('checkHasRoleForScope',
                         gci_org_admin_logic.logic)]
    rights['accept_invite'] = [
        ('checkIsMyRequestWithStatus', [['group_accepted']]),
        ('checkIsNotStudentForProgramOfOrgInRequest',
         [gci_org_logic.logic, gci_student_logic.logic])]
    rights['request'] = [
        ('checkIsNotStudentForProgramOfOrg',
         [gci_org_logic.logic, gci_student_logic.logic]),
        ('checkCanMakeRequestToGroup', gci_org_logic.logic)]
    rights['process_request'] = [
        ('checkCanProcessRequest', [[gci_org_admin_logic.logic]])]
    rights['manage'] = [
        ('checkIsAllowedToManageRole', [gci_mentor_logic.logic,
                                        gci_org_admin_logic.logic])]
    rights['list_mentor_tasks'] = [
        ('checkCanOpenTaskList', [gci_mentor_logic.logic, 'gci/mentor']),
        ('checkIsAfterEvent', ['accepted_organization_announced_deadline',
                               '__all__', gci_program_logic.logic])]

    new_params = {}
    new_params['logic'] = soc.modules.gci.logic.models.mentor.logic
    new_params['group_logic'] = gci_org_logic.logic
    new_params['group_view'] = gci_org_view.view
    new_params['rights'] = rights

    new_params['scope_view'] = gci_org_view

    new_params['name'] = "GCI Mentor"
    new_params['module_name'] = "mentor"
    new_params['sidebar_grouping'] = 'Organizations'

    new_params['module_package'] = 'soc.modules.gci.views.models'
    new_params['url_name'] = 'gci/mentor'

    new_params['role'] = 'gci/mentor'

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

    idx = lists.getListIndex(request)

    # default list settings
    args = []
    order = ['modified_on']
    visibility = 'public'

    if idx == 0:
      contents = lists.getListData(request, params, filter,
                                   visibility=visibility,
                                   order=order, args=args)
    else:
      return lists.getErrorResponse(request, "idx not valid")


    return lists.getResponse(request, contents)

  @decorators.merge_params
  @decorators.check_access
  def listMentorTasks(self, request, access_type, page_name=None,
                      params=None, **kwargs):
    """Displays a list of all tasks for a given student.

    See base.View.list() for more details.
    """

    entity = params['logic'].getFromKeyFieldsOr404(kwargs)

    # obtain program entity based on request params
    program = entity.program

    user_account = user_logic.logic.getForCurrentAccount()

    filter = {
        'user': user_account,
        'program': program,
        'status': 'active'
        }

    list_params = gci_task_view.view.getParams().copy()

    list_params['list_description'] = self.DEF_MENTOR_TASKS_MSG_FMT % (
          program.name)

    filter = {
        'program': program,
        'mentors': [entity],
        'status': ['Unapproved', 'Unpublished', 'Open', 'Reopened',
                   'ClaimRequested', 'Claimed', 'ActionNeeded', 'Closed',
                   'AwaitingRegistration', 'NeedsWork', 'NeedsReview']
        }

    if lists.isDataRequest(request):
        return self.getListMentorTasksData(request, list_params,
                                           filter)

    tasks = gci_task_logic.logic.getForFields(filter=filter, unique=True)

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
