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

"""GHOP specific views for Student.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>',
    '"Daniel Hans" <daniel.m.hans@gmail.com>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from django.utils.translation import ugettext

from soc.logic import dicts
from soc.logic.models import user as user_logic

from soc.views.helper import decorators
from soc.views.helper import redirects
from soc.views.models import student

from soc.modules.ghop.logic.models import mentor as ghop_mentor_logic
from soc.modules.ghop.logic.models import org_admin as ghop_org_admin_logic
from soc.modules.ghop.logic.models import program as ghop_program_logic
from soc.modules.ghop.logic.models import student as ghop_student_logic
from soc.modules.ghop.logic.models import task as ghop_task_logic
from soc.modules.ghop.views.helper import access as ghop_access
from soc.modules.ghop.views.models import program as ghop_program_view
from soc.modules.ghop.views.models import task as ghop_task_view

import soc.modules.ghop.logic.models.student


class View(student.View):
  """View methods for the GHOP Student model.
  """

  DEF_STUDENT_TASKS_MSG_FMT = ugettext('Your tasks for %s.')

  def __init__(self, params=None):
    """Defines the fields and methods required for the student View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    patterns = []
    patterns += [
        (r'^%(url_name)s/(?P<access_type>list_student_tasks)/%(scope)s$',
        '%(module_package)s.%(module_name)s.list_student_tasks',
        'List Student tasks')]

    rights = ghop_access.GHOPChecker(params)
    rights['edit'] = [('checkIsMyActiveRole', ghop_student_logic.logic)]
    rights['apply'] = [
        'checkIsUser',
        ('checkIsActivePeriod', ['student_signup', 'scope_path',
            ghop_program_logic.logic]),
        ('checkIsNotParticipatingInProgramInScope',
            [ghop_program_logic.logic, ghop_student_logic.logic,
            ghop_org_admin_logic.logic, ghop_mentor_logic.logic]),
        'checkCanApply']
    rights['manage'] = [('checkIsMyActiveRole', ghop_student_logic.logic)]
    rights['list_student_tasks'] = ['checkCanOpenTaskList']

    new_params = {}
    new_params['logic'] = soc.modules.ghop.logic.models.student.logic
    new_params['rights'] = rights

    new_params['group_logic'] = ghop_program_logic.logic
    new_params['group_view'] = ghop_program_view.view

    new_params['scope_view'] = ghop_program_view

    new_params['name'] = "GHOP Student"
    new_params['module_name'] = "student"
    new_params['sidebar_grouping'] = 'Students'

    new_params['module_package'] = 'soc.modules.ghop.views.models'
    new_params['url_name'] = 'ghop/student'

    new_params['extra_django_patterns'] = patterns

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params=params)

  @decorators.merge_params
  @decorators.check_access
  def listStudentTasks(self, request, access_type, page_name=None,
                       params=None, **kwargs):
    """Displays a list of all tasks for a given student.

    See base.View.list() for more details.
    """

    # obtain program entity based on request params
    program = ghop_program_logic.logic.getFromKeyNameOr404(
        kwargs['scope_path'])

    user_account = user_logic.logic.getForCurrentAccount()

    filter = {
        'user': user_account,
        'program': program
        }

    tasks = ghop_task_logic.logic.getForFields(filter=filter)

    tasks_by_orgs = {}
    for task in tasks:
      key = task.scope.key().id_or_name()
      if key in tasks_by_orgs:
        tasks_by_orgs[key][1].append(task)
      else:
        tasks_by_orgs[key] = (task.scope.name, [task])

    contents = []
    context = {}

    st_params = ghop_task_view.view.getParams().copy()
    st_params['list_template'] = 'soc/models/list.html'
    st_params['list_heading'] = 'modules/ghop/task/list/heading.html'
    st_params['list_row'] = 'modules/ghop/task/list/row.html'
    st_params['public_row_extra'] = lambda entity: {
        'link': redirects.getPublicRedirect(entity, st_params)
    }
# TODO(LIST)
    st_org_params = st_params.copy()
    for k, v in tasks_by_orgs.iteritems():
      st_org_params['list_description'] = self.DEF_STUDENT_TASKS_MSG_FMT % v[0]

      st_org_list = self._listStudentTasks(tasks_by_orgs[k][1], st_org_params)

      contents.append(st_org_list)

    return self._list(request, st_params, contents, page_name, context)

  def _listStudentTasks(self, data, params):
    """Returns a list with all entities specified in data.
    """

    result = dicts.rename(params, params['list_params'])
    result['action'] = (redirects.getPublicRedirect, params)
    result['data'] = data
    result['pagination'] = 'soc/list/no_pagination.html'
# TODO(LIST)
    return result


view = View()

apply = decorators.view(view.apply)
create = decorators.view(view.create)
delete = decorators.view(view.delete)
edit = decorators.view(view.edit)
list = decorators.view(view.list)
list_student_tasks = decorators.view(view.listStudentTasks)
manage = decorators.view(view.manage)
public = decorators.view(view.public)
export = decorators.view(view.export)
