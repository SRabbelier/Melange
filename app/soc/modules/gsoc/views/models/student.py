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

"""Views for GSoCStudent.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from soc.logic import dicts
from soc.views.helper import decorators
from soc.views.helper import access # TODO
from soc.views.models import student

from soc.logic.models.host import logic as host_logic
from soc.modules.gsoc.logic.models.program import logic as program_logic
from soc.modules.gsoc.logic.models.student import logic as student_logic
from soc.modules.gsoc.logic.models.mentor import logic as mentor_logic
from soc.modules.gsoc.logic.models.org_admin import logic as org_admin_logic
from soc.modules.gsoc.views.models import program as program_view


class View(student.View):
  """View methods for the Student model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = access.Checker(params)
    rights['create'] = ['checkIsDeveloper']
    rights['edit'] = [('checkIsMyActiveRole', student_logic)]
    rights['delete'] = ['checkIsDeveloper']
    rights['apply'] = [
        'checkIsUser',
        ('checkIsActivePeriod',
         ['student_signup', 'scope_path', program_logic]),
        ('checkIsNotParticipatingInProgramInScope', [program_logic,
        student_logic, org_admin_logic, mentor_logic]),
        ]
    rights['manage'] = [('checkIsMyActiveRole', student_logic)]
    rights['list_projects'] = [
        ('checkHasActiveRoleForScope', student_logic),
        ('checkIsAfterEvent', ['accepted_students_announced_deadline',
                               'scope_path', program_logic])]

    new_params = {}
    new_params['logic'] = student_logic
    new_params['rights'] = rights

    new_params['group_logic'] = program_logic
    new_params['group_view'] = program_view.view

    new_params['scope_view'] = program_view

    new_params['name'] = "GSoC Student"
    new_params['module_name'] = "student"
    new_params['sidebar_grouping'] = 'Students'

    new_params['module_package'] = 'soc.modules.gsoc.views.models'
    new_params['url_name'] = 'gsoc/student'

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params)


view = View()

apply = decorators.view(view.apply)
create = decorators.view(view.create)
delete = decorators.view(view.delete)
edit = decorators.view(view.edit)
list = decorators.view(view.list)
list_projects = decorators.view(view.listProjects)
manage = decorators.view(view.manage)
public = decorators.view(view.public)
export = decorators.view(view.export)
